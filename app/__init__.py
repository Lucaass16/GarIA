"""Inicialização da aplicação Flask.

SPDX-License-Identifier: AGPL-3.0-only
Copyright (c) 2025 Lucas da Silva

Este arquivo faz parte do GarIA e está licenciado sob GPL-3.0.
"""

from flask import Flask
from flasgger import Swagger
from app.infrastructure.config.settings import Config
from app.infrastructure.ml.torch_setup import configure_for_app


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "GarIA API - Object Detection",
            "description": "API para detecção de lixo usando YOLO",
            "version": "0.0.1",
        },
        "host": "localhost:5000",
        "basePath": "/api",
        "schemes": ["http", "https"],
        "consumes": ["application/json", "multipart/form-data"],
        "produces": ["application/json"],
        "tags": [
            {
                "name": "Detection",
                "description": "Endpoints para detecção de objetos"
            },
            {
                "name": "Model",
                "description": "Gerenciamento de modelos YOLO"
            },
            {
                "name": "Health",
                "description": "Status e monitoramento"
            }
        ]
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)

    # Configuração Torch/Ultralytics centralizada (executa 1x)
    try:
        configure_for_app(app.config)
    except Exception as e:
        app.logger.warning(f"Falha ao configurar Torch serialization: {e}")
    
    from app.controllers import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
