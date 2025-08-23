"""Infraestrutura de carregamento e inferência YOLO.

SPDX-License-Identifier: AGPL-3.0-only
Copyright (c) 2025 Lucas da Silva
"""

import os
from typing import List, Dict, Any, Optional
import torch
from ultralytics import YOLO
from .torch_setup import configure_torch_serialization
from app.infrastructure.config.settings import Config


class YOLOModelLoader:
    
    def __init__(self, config: Config):
        self.config = config
        self.model: Optional[YOLO] = None
        self.model_path: Optional[str] = None
        
    def load_model(self, model_name: str = "yolov8n.pt") -> YOLO:
        if self.model is not None and self.model_path == model_name:
            return self.model
            
        model_path = os.path.join("models", model_name)
        
        if not os.path.exists(model_path):
            print(f"⚠️  Modelo {model_path} não encontrado localmente. Tentando baixar/usar fallback...")
            model_path = model_name

        try:
            configure_torch_serialization()
            self.model = YOLO(model_path)
            print("✅ Modelo carregado com configuração centralizada de serialization")
            self.model_path = model_name
            
            print(f"✅ Modelo YOLO carregado: {model_name}")
            return self.model
            
        except Exception as e:
            print(f"❌ Erro ao carregar modelo YOLO: {str(e)}")
            raise
            
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o modelo carregado
        """
        if self.model is None:
            return {"status": "not_loaded"}
            
        return {
            "status": "loaded",
            "model_path": self.model_path,
            "device": str(self.model.device),
            "task": getattr(self.model, 'task', 'unknown')
        }
        
    def unload_model(self):
        """
        Descarrega o modelo da memória
        """
        if self.model is not None:
            del self.model
            self.model = None
            self.model_path = None
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            print("🗑️  Modelo YOLO descarregado da memória")


class YOLOInference:
    """
    Classe responsável por executar inferência com modelos YOLO
    """
    
    def __init__(self, model_loader: YOLOModelLoader):
        self.model_loader = model_loader
        
    def predict(
        self,
        source: Any,
        confidence: float = 0.25,
        iou_threshold: float = 0.45,
        max_detections: int = 1000,
        classes: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executa predição em uma imagem ou vídeo
        
        Args:
            source: Fonte da imagem (caminho, URL, array numpy, PIL Image, etc.)
            confidence: Threshold de confiança mínima
            iou_threshold: Threshold de IoU para NMS
            max_detections: Número máximo de detecções
            classes: Lista de classes específicas para detectar
            
        Returns:
            Lista de detecções formatadas
        """
        if self.model_loader.model is None:
            raise ValueError("Modelo não carregado. Chame load_model() primeiro.")
            
        try:
            results = self.model_loader.model(
                source,
                conf=confidence,
                iou=iou_threshold,
                max_det=max_detections,
                classes=classes,
                verbose=False
            )

            detections = []
            for result in results:
                if result.boxes is not None:
                    boxes = result.boxes
                    for i in range(len(boxes)):
                        detection = {
                            "class_id": int(boxes.cls[i]),
                            "class_name": result.names[int(boxes.cls[i])],
                            "confidence": float(boxes.conf[i]),
                            "bbox": {
                                "x1": float(boxes.xyxy[i][0]),
                                "y1": float(boxes.xyxy[i][1]),
                                "x2": float(boxes.xyxy[i][2]),
                                "y2": float(boxes.xyxy[i][3])
                            },
                            "bbox_normalized": {
                                "x": float(boxes.xywhn[i][0]),
                                "y": float(boxes.xywhn[i][1]),
                                "width": float(boxes.xywhn[i][2]),
                                "height": float(boxes.xywhn[i][3])
                            }
                        }
                        detections.append(detection)
                        
            return detections
            
        except Exception as e:
            print(f"❌ Erro durante inferência: {str(e)}")
            raise
            
    def predict_batch(
        self,
        sources: List[Any],
        **kwargs
    ) -> List[List[Dict[str, Any]]]:
        """
        Executa predição em lote para múltiplas imagens
        
        Args:
            sources: Lista de fontes de imagem
            **kwargs: Argumentos para predict()
            
        Returns:
            Lista de listas de detecções
        """
        results = []
        for source in sources:
            detections = self.predict(source, **kwargs)
            results.append(detections)
        return results
