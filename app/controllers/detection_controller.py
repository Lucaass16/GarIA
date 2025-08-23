"""Endpoints de detecção de resíduos recicláveis.

SPDX-License-Identifier: AGPL-3.0-only
Copyright (c) 2025 Lucas da Silva
"""

import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from PIL import Image
import numpy as np
from typing import Dict, Any, List
from flasgger import swag_from

from app.services.ml.object_detection_service import ObjectDetectionService
from app.domain.ml.entities import ModelConfiguration


detection_bp = Blueprint('detection', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

detection_service: ObjectDetectionService = None


def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_detection_service() -> ObjectDetectionService:
    global detection_service
    
    if detection_service is None:
        from app.infrastructure.config.settings import Config
        detection_service = ObjectDetectionService(Config())
        
        default_config = ModelConfiguration(
            model_name="GarIA.pt",
            model_path=os.getenv("MODEL_PATH", "models/GarIA.pt"),
            confidence_threshold=0.25,
            iou_threshold=0.45,
            max_detections=1000
        )
        
        detection_service.initialize_model(default_config)
        
    return detection_service


@detection_bp.route('/detect', methods=['POST'])
def detect_objects():
  """
  Detecta objetos em uma imagem enviada
  ---
  tags:
    - Detection
  summary: Detecta objetos em imagem
  description: Endpoint para detecção de objetos usando modelo YOLO. Aceita imagem via upload e parâmetros de configuração.
  consumes:
    - multipart/form-data
  parameters:
    - name: image
      in: formData
      type: file
      required: true
      description: Arquivo de imagem (PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP)
    - name: confidence
      in: formData
      type: number
      format: float
      minimum: 0.0
      maximum: 1.0
      default: 0.25
      description: Threshold mínimo de confiança para detecções
    - name: iou_threshold
      in: formData
      type: number
      format: float
      minimum: 0.0
      maximum: 1.0
      default: 0.45
      description: Threshold de IoU para Non-Maximum Suppression
    - name: max_detections
      in: formData
      type: integer
      minimum: 1
      default: 1000
      description: Número máximo de detecções
  responses:
    200:
      description: Detecção realizada com sucesso
      schema:
        type: object
        properties:
          success:
            type: boolean
            example: true
          detections:
            type: array
            items:
              type: object
              properties:
                class_id:
                  type: integer
                  description: ID da classe detectada
                class_name:
                  type: string
                  description: Nome da classe detectada
                confidence:
                  type: number
                  format: float
                  description: Confiança da detecção (0.0-1.0)
                bbox:
                  type: object
                  properties:
                    x1:
                      type: number
                      description: Coordenada X do canto superior esquerdo
                    y1:
                      type: number
                      description: Coordenada Y do canto superior esquerdo
                    x2:
                      type: number
                      description: Coordenada X do canto inferior direito
                    y2:
                      type: number
                      description: Coordenada Y do canto inferior direito
                    width:
                      type: number
                      description: Largura da bounding box
                    height:
                      type: number
                      description: Altura da bounding box
                    center:
                      type: array
                      items:
                        type: number
                      description: Coordenadas do centro [x, y]
          statistics:
            type: object
            properties:
              total_detections:
                type: integer
              unique_classes:
                type: array
                items:
                  type: string
              avg_confidence:
                type: number
              processing_time:
                type: number
          processing_time:
            type: number
            description: Tempo de processamento em segundos
          timestamp:
            type: string
            format: date-time
            description: Timestamp da detecção
    400:
      description: Erro nos parâmetros de entrada
      schema:
        type: object
        properties:
          error:
            type: string
          code:
            type: string
    500:
      description: Erro interno do servidor
  """
  try:
      if 'image' not in request.files:
          return jsonify({
              'error': 'Nenhum arquivo de imagem fornecido',
              'code': 'NO_IMAGE_FILE'
          }), 400
          
      file: FileStorage = request.files['image']
      
      if file.filename == '':
          return jsonify({
              'error': 'Nenhum arquivo selecionado',
              'code': 'NO_FILE_SELECTED'
          }), 400
          
      if not allowed_file(file.filename):
          return jsonify({
              'error': f'Tipo de arquivo não suportado. Tipos permitidos: {", ".join(ALLOWED_EXTENSIONS)}',
              'code': 'INVALID_FILE_TYPE'
          }), 400
          
      custom_config = {}
      
      if 'confidence' in request.form:
          try:
              custom_config['confidence'] = float(request.form['confidence'])
          except ValueError:
              return jsonify({
                  'error': 'Parâmetro confidence deve ser um número',
                  'code': 'INVALID_CONFIDENCE'
              }), 400
              
      if 'iou_threshold' in request.form:
          try:
              custom_config['iou_threshold'] = float(request.form['iou_threshold'])
          except ValueError:
              return jsonify({
                  'error': 'Parâmetro iou_threshold deve ser um número',
                  'code': 'INVALID_IOU_THRESHOLD'
              }), 400
              
      if 'max_detections' in request.form:
        try:
          custom_config['max_detections'] = int(request.form['max_detections'])
        except ValueError:
          return jsonify({
            'error': 'Parâmetro max_detections deve ser um número inteiro',
            'code': 'INVALID_MAX_DETECTIONS'
          }), 400

      try:
        image = Image.open(file.stream)
        if image.mode != 'RGB':
          image = image.convert('RGB')
      except Exception as e:
        return jsonify({
          'error': f'Erro ao processar imagem: {str(e)}',
          'code': 'IMAGE_PROCESSING_ERROR'
        }), 400

      service = get_detection_service()

      detection_config = {
        'confidence': custom_config.get('confidence', 0.25),
        'iou_threshold': custom_config.get('iou_threshold', 0.45),
        'max_detections': custom_config.get('max_detections', 1000)
      }

      result = service.detect_objects(image, detection_config)

      counts = {}
      for d in result.detections:
        counts[d.class_name] = counts.get(d.class_name, 0) + 1
      return jsonify({
        'success': True,
        'total_detections': len(result.detections),
        'counts': counts,
        'unique_classes': list(counts.keys()),
        'processing_time': round(result.processing_time, 4),
        'timestamp': result.timestamp.isoformat()
      })
      
  except Exception as e:
    current_app.logger.error(f"Erro na detecção de objetos: {str(e)}")
    return jsonify({
        'error': 'Erro interno do servidor',
        'code': 'INTERNAL_ERROR',
        'details': str(e) if current_app.debug else None
    }), 500


@detection_bp.route('/detect/url', methods=['POST'])
def detect_objects_from_url():
  """
  Detecta objetos a partir de URL de imagem
  ---
  tags:
    - Detection
  summary: Detecta objetos via URL
  description: Endpoint para detecção de objetos usando URL de imagem externa
  consumes:
    - application/json
  parameters:
    - name: body
      in: body
      required: true
      schema:
        type: object
        required:
          - image_url
        properties:
          image_url:
            type: string
            format: uri
            description: URL da imagem para análise
            example: "https://example.com/image.jpg"
          config:
            type: object
            properties:
              confidence:
                type: number
                format: float
                minimum: 0.0
                maximum: 1.0
                default: 0.25
              iou_threshold:
                type: number
                format: float
                minimum: 0.0
                maximum: 1.0
                default: 0.45
              max_detections:
                type: integer
                minimum: 1
                default: 1000
  responses:
    200:
      description: Detecção realizada com sucesso
      schema:
        $ref: '#/definitions/DetectionResponse'
    400:
      description: URL inválida ou parâmetros incorretos
    500:
      description: Erro interno do servidor
  """
  try:
    data = request.get_json()
        
    if not data or 'image_url' not in data:
      return jsonify({
          'error': 'URL da imagem não fornecida',
          'code': 'NO_IMAGE_URL'
      }), 400
            
    image_url = data['image_url']
    custom_config = data.get('config', {})
        
    service = get_detection_service()

    result = service.detect_objects(image_url, custom_config)

    counts = {}
    for d in result.detections:
      counts[d.class_name] = counts.get(d.class_name, 0) + 1
    return jsonify({
      'success': True,
      'total_detections': len(result.detections),
      'garbage_detected': [
         {'name': d.class_name, 'confidence': d.confidence}
         for d in result.detections
      ],
      'counts': counts,
      'unique_classes': list(counts.keys()),
      'processing_time': round(result.processing_time, 4),
      'timestamp': result.timestamp.isoformat()
    })
        
  except Exception as e:
      current_app.logger.error(f"Erro na detecção de objetos por URL: {str(e)}")
      return jsonify({
          'error': 'Erro interno do servidor',
          'code': 'INTERNAL_ERROR',
          'details': str(e) if current_app.debug else None
      }), 500


@detection_bp.route('/model/status', methods=['GET'])
def get_model_status():
    """
    Verifica status do modelo YOLO
    ---
    tags:
      - Model
    summary: Status do modelo
    description: Retorna informações sobre o estado atual do modelo YOLO carregado
    responses:
      200:
        description: Status obtido com sucesso
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            status:
              type: object
              properties:
                model_loaded:
                  type: boolean
                  description: Se o modelo está carregado
                model_config:
                  type: object
                  description: Configuração atual do modelo
                model_info:
                  type: object
                  properties:
                    status:
                      type: string
                      example: "loaded"
                    model_path:
                      type: string
                      example: "GarIA.pt"
                    device:
                      type: string
                      example: "cpu"
                    task:
                      type: string
                      example: "detect"
      500:
        description: Erro interno do servidor
    """
    try:
        service = get_detection_service()
        status = service.get_model_status()
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter status do modelo: {str(e)}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'code': 'INTERNAL_ERROR',
            'details': str(e) if current_app.debug else None
        }), 500
