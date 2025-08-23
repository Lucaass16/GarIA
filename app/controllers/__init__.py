"""Blueprint raiz da API GarIA.

SPDX-License-Identifier: AGPL-3.0-only
Copyright (c) 2025 Lucas da Silva
"""

from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

from .detection_controller import detection_bp
api_bp.register_blueprint(detection_bp, url_prefix='/detection')


@api_bp.route('/', methods=['GET'])
def api_info():
    """
    Informações da API
    ---
    tags:
      - Info
    summary: Informações da API
    description: Retorna informações básicas sobre a API de detecção de objetos
    responses:
      200:
        description: Informações da API
        schema:
          type: object
          properties:
            name:
              type: string
              example: "GarIA API - Object Detection"
            version:
              type: string
              example: "1.0.0"
            description:
              type: string
              example: "API para detecção de objetos usando YOLO"
            endpoints:
              type: object
              properties:
                detection:
                  type: string
                  example: "/api/detection/detect"
                docs:
                  type: string
                  example: "/docs/"
            status:
              type: string
              example: "online"
    """
    return jsonify({
        "name": "GarIA API - Object Detection",
        "version": "0.0.1", 
        "description": "API para detecção de lixo usando YOLO",
        "endpoints": {
            "detection": "/api/detection/detect",
            "detection_url": "/api/detection/detect/url",
            "model_status": "/api/detection/model/status",
            "health": "/api/detection/health",
            "docs": "/docs/"
        },
        "status": "online"
    })