"""Entidades de domínio para detecção de resíduos recicláveis.

SPDX-License-Identifier: AGPL-3.0-only
Copyright (c) 2025 Lucas da Silva
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class BoundingBox:
    """
    Representa uma caixa delimitadora (bounding box)
    """
    x1: float
    y1: float
    x2: float
    y2: float
    
    @property
    def width(self) -> float:
        return self.x2 - self.x1
    
    @property
    def height(self) -> float:
        return self.y2 - self.y1
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    @property
    def center(self) -> tuple[float, float]:
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)


@dataclass
class Detection:
    """
    Representa uma detecção de objeto
    """
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox
    bbox_normalized: Optional[Dict[str, float]] = None
    
    def is_valid(self, min_confidence: float = 0.0) -> bool:
        """
        Verifica se a detecção é válida
        """
        return (
            self.confidence >= min_confidence and
            0 <= self.confidence <= 1.0 and
            self.bbox.width > 0 and
            self.bbox.height > 0
        )


@dataclass
class DetectionResult:
    """
    Representa o resultado completo de uma detecção
    """
    detections: List[Detection]
    image_info: Dict[str, Any]
    processing_time: float
    model_info: Dict[str, str]
    timestamp: datetime
    
    @property
    def detection_count(self) -> int:
        return len(self.detections)
    
    @property
    def unique_classes(self) -> List[str]:
        return list(set(detection.class_name for detection in self.detections))
    
    def filter_by_confidence(self, min_confidence: float) -> List[Detection]:
        """
        Filtra detecções por confiança mínima
        """
        return [d for d in self.detections if d.confidence >= min_confidence]
    
    def filter_by_class(self, class_names: List[str]) -> List[Detection]:
        """
        Filtra detecções por classes específicas
        """
        return [d for d in self.detections if d.class_name in class_names]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas das detecções
        """
        if not self.detections:
            return {
                "total_detections": 0,
                "unique_classes": [],
                "avg_confidence": 0.0,
                "max_confidence": 0.0,
                "min_confidence": 0.0
            }
        
        confidences = [d.confidence for d in self.detections]
        
        return {
            "total_detections": len(self.detections),
            "unique_classes": self.unique_classes,
            "avg_confidence": sum(confidences) / len(confidences),
            "max_confidence": max(confidences),
            "min_confidence": min(confidences),
            "processing_time": self.processing_time
        }


@dataclass
class ModelConfiguration:
    """
    Representa a configuração de um modelo ML
    """
    model_name: str
    model_path: str
    confidence_threshold: float = 0.25
    iou_threshold: float = 0.45
    max_detections: int = 1000
    target_classes: Optional[List[str]] = None
    
    def is_valid(self) -> bool:
        """
        Verifica se a configuração é válida
        """
        return (
            0.0 <= self.confidence_threshold <= 1.0 and
            0.0 <= self.iou_threshold <= 1.0 and
            self.max_detections > 0
        )
