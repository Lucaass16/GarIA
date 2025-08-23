"""Serviço de detecção usando YOLO para resíduos recicláveis.

SPDX-License-Identifier: AGPL-3.0-only
Copyright (c) 2025 Lucas da Silva
"""

import time
from datetime import datetime
from typing import Any, List, Dict, Optional, Union
from PIL import Image
import numpy as np
from dataclasses import asdict

from app.domain.ml.entities import Detection, DetectionResult, BoundingBox, ModelConfiguration
from app.infrastructure.ml.yolo_model import YOLOModelLoader, YOLOInference
from app.infrastructure.config.settings import Config


class ObjectDetectionService:
    def __init__(self, config: Config):
        self.config = config
        self.model_loader = YOLOModelLoader(config)
        self.inference_engine = YOLOInference(self.model_loader)
        self.model_config: Optional[ModelConfiguration] = None
        
    def initialize_model(self, model_config: ModelConfiguration) -> bool:
        try:
            if not model_config.is_valid():
                raise ValueError("Configuração do modelo inválida")
                
            self.model_config = model_config
            self.model_loader.load_model(model_config.model_name)
            
            print(f"✅ Modelo inicializado: {model_config.model_name}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao inicializar modelo: {str(e)}")
            return False
            
    def detect_objects(
        self,
        image_source: Union[str, Image.Image, np.ndarray],
        custom_config: Optional[Dict[str, Any]] = None
    ) -> DetectionResult:

        model_config = ModelConfiguration(
                        model_name="GarIA.pt",
                        model_path="models/GarIA.pt",
                        confidence_threshold=custom_config.get('confidence', 0.25),
                        iou_threshold=custom_config.get('iou_threshold', 0.45),
                        max_detections=custom_config.get('max_detections', 1000)
                    )

        self.initialize_model(model_config)

        if self.model_config is None:
            raise ValueError("Modelo não inicializado. Chame initialize_model() primeiro.")
            
        start_time = time.time()
        
        try:
            config = self._merge_configs(custom_config or {})
            
            raw_detections = self.inference_engine.predict(
                source=image_source,
                confidence=config["confidence"],
                iou_threshold=config["iou_threshold"],
                max_detections=config["max_detections"],
                classes=config.get("class_ids")
            )
            
            detections = self._convert_to_domain_entities(raw_detections)
            
            if self.model_config.target_classes is not None:
                detections = [
                    d for d in detections 
                    if d.class_name in self.model_config.target_classes
                ]
            
            processing_time = time.time() - start_time
            
            image_info = self._get_image_info(image_source)
            
            result = DetectionResult(
                detections=detections,
                image_info=image_info,
                processing_time=processing_time,
                model_info=self.model_loader.get_model_info(),
                timestamp=datetime.now()
            )
            
            print(f"🎯 Detectados {len(detections)} objetos em {processing_time:.3f}s")
            return result
            
        except Exception as e:
            print(f"❌ Erro durante detecção: {str(e)}")
            raise
            
    def detect_objects_batch(
        self,
        image_sources: List[Union[str, Image.Image, np.ndarray]],
        custom_config: Optional[Dict[str, Any]] = None
    ) -> List[DetectionResult]:

        results = []
        for i, image_source in enumerate(image_sources):
            try:
                result = self.detect_objects(image_source, custom_config)
                results.append(result)
                print(f"✅ Processada imagem {i+1}/{len(image_sources)}")
                
            except Exception as e:
                print(f"❌ Erro ao processar imagem {i+1}: {str(e)}")
                results.append(DetectionResult(
                    detections=[],
                    image_info={"error": str(e)},
                    processing_time=0.0,
                    model_info=self.model_loader.get_model_info(),
                    timestamp=datetime.now()
                ))
                
        return results
        
    def get_model_status(self) -> Dict[str, Any]:

        model_info = self.model_loader.get_model_info()
        
        return {
            "model_loaded": model_info["status"] == "loaded",
            "model_config": asdict(self.model_config) if self.model_config else None,
            "model_info": model_info
        }
        
    def _merge_configs(self, custom_config: Dict[str, Any]) -> Dict[str, Any]:
        if self.model_config is None:
            raise ValueError("Modelo não inicializado. Chame initialize_model() primeiro.")

        default_config = {
            "confidence": self.model_config.confidence_threshold,
            "iou_threshold": self.model_config.iou_threshold,
            "max_detections": self.model_config.max_detections
        }
            
        default_config.update(custom_config)
        return default_config
        
    def _convert_to_domain_entities(self, raw_detections: List[Dict[str, Any]]) -> List[Detection]:

        detections = []
        
        for raw_detection in raw_detections:
            bbox = BoundingBox(
                x1=raw_detection["bbox"]["x1"],
                y1=raw_detection["bbox"]["y1"],
                x2=raw_detection["bbox"]["x2"],
                y2=raw_detection["bbox"]["y2"]
            )
            
            detection = Detection(
                class_id=raw_detection["class_id"],
                class_name=raw_detection["class_name"],
                confidence=raw_detection["confidence"],
                bbox=bbox,
                bbox_normalized=raw_detection.get("bbox_normalized")
            )
            
            detections.append(detection)
            
        return detections
        
    def _get_image_info(self, image_source: Any) -> Dict[str, Any]:

        try:
            if isinstance(image_source, str):
                from PIL import Image
                with Image.open(image_source) as img:
                    return {
                        "width": img.width,
                        "height": img.height,
                        "format": img.format,
                        "mode": img.mode,
                        "source_type": "file_path"
                    }
            elif isinstance(image_source, Image.Image):
                return {
                    "width": image_source.width,
                    "height": image_source.height,
                    "format": image_source.format,
                    "mode": image_source.mode,
                    "source_type": "pil_image"
                }
            elif isinstance(image_source, np.ndarray):
                return {
                    "width": image_source.shape[1] if len(image_source.shape) > 1 else image_source.shape[0],
                    "height": image_source.shape[0],
                    "channels": image_source.shape[2] if len(image_source.shape) > 2 else 1,
                    "dtype": str(image_source.dtype),
                    "source_type": "numpy_array"
                }
            else:
                return {"source_type": "unknown"}
                
        except Exception as e:
            return {"error": str(e), "source_type": "error"}
