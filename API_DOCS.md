# 📖 Documentação da API GarIA

## 🎯 Visão Geral

O **GarIA** é uma API para detecção de resíduos recicláveis usando visão computacional com YOLO. A API identifica 4 tipos principais de materiais recicláveis: **plastic**, **metal**, **paper** e **glass**.

### 🌐 Informações Básicas
- **Base URL**: `http://localhost:5000`
- **Versão**: v0.0.1
- **Documentação Interativa**: `http://localhost:5000/docs/`
- **Formato de Resposta**: JSON
- **Licença**: AGPL-3.0

---

## 🚀 Como Iniciar

### 1. Configuração do Ambiente

```bash
# Ativar ambiente virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python main.py
```

### 2. Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `FLASK_ENV` | Ambiente (development/production/testing) | development |
| `FLASK_HOST` | Host da aplicação | 127.0.0.1 |
| `FLASK_PORT` | Porta da aplicação | 5000 |
| `MODEL_PATH` | Caminho para o modelo YOLO | models/GarIA.pt |
| `SECRET_KEY` | Chave secreta do Flask | dev-secret-key-change-in-production |

---

## 📋 Endpoints da API

### 🔍 1. Informações da API

**GET** `/api/`

Retorna informações básicas sobre a API e endpoints disponíveis.

#### Resposta
```json
{
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
}
```

---

### 🖼️ 2. Detecção por Upload de Imagem

**POST** `/api/detection/detect`

Detecta objetos em uma imagem enviada via upload.

#### Parâmetros (multipart/form-data)

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `image` | file | ✅ | Arquivo de imagem (PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP) |
| `confidence` | float | ❌ | Confiança mínima (0.0-1.0) - Padrão: 0.25 |
| `iou_threshold` | float | ❌ | IoU para NMS (0.0-1.0) - Padrão: 0.45 |
| `max_detections` | integer | ❌ | Máximo de detecções - Padrão: 1000 |

#### Exemplo com cURL
```bash
curl -X POST http://localhost:5000/api/detection/detect \
  -F "image=@exemplo.jpg" \
  -F "confidence=0.30" \
  -F "iou_threshold=0.45"
```

#### Exemplo com Python
```python
import requests

with open("exemplo.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:5000/api/detection/detect",
        files={"image": f},
        data={"confidence": 0.3}
    )
    
result = response.json()
print(result)
```

#### Exemplo com JavaScript/Fetch
```javascript
const formData = new FormData();
formData.append('image', imageFile);
formData.append('confidence', '0.3');

fetch('http://localhost:5000/api/detection/detect', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

#### Resposta de Sucesso (200)
```json
{
  "success": true,
  "total_detections": 3,
  "counts": {
    "plastic": 2,
    "metal": 1
  },
  "unique_classes": ["plastic", "metal"],
  "processing_time": 0.1532,
  "timestamp": "2025-01-15T12:30:45.123456"
}
```

---

### 🌐 3. Detecção por URL de Imagem

**POST** `/api/detection/detect/url`

Detecta objetos em uma imagem a partir de URL externa.

#### Parâmetros (JSON)
```json
{
  "image_url": "https://exemplo.com/imagem.jpg",
  "config": {
    "confidence": 0.3,
    "iou_threshold": 0.45,
    "max_detections": 1000
  }
}
```

#### Exemplo com cURL
```bash
curl -X POST http://localhost:5000/api/detection/detect/url \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://exemplo.com/imagem.jpg",
    "config": {"confidence": 0.3, "max_detections": 200}
  }'
```

#### Exemplo com Python
```python
import requests

data = {
    "image_url": "https://exemplo.com/imagem.jpg",
    "config": {
        "confidence": 0.3,
        "iou_threshold": 0.45
    }
}

response = requests.post(
    "http://localhost:5000/api/detection/detect/url",
    json=data
)

result = response.json()
print(result)
```

#### Resposta de Sucesso (200)
```json
{
  "success": true,
  "total_detections": 2,
  "garbage_detected": [
    {"name": "plastic", "confidence": 0.87},
    {"name": "paper", "confidence": 0.76}
  ],
  "counts": {
    "plastic": 1,
    "paper": 1
  },
  "unique_classes": ["plastic", "paper"],
  "processing_time": 0.2134,
  "timestamp": "2025-01-15T12:30:45.123456"
}
```

---

### ⚙️ 4. Status do Modelo

**GET** `/api/detection/model/status`

Retorna informações sobre o estado atual do modelo YOLO.

#### Exemplo com cURL
```bash
curl -X GET http://localhost:5000/api/detection/model/status
```

#### Resposta de Sucesso (200)
```json
{
  "success": true,
  "status": {
    "model_loaded": true,
    "model_config": {
      "model_name": "GarIA.pt",
      "confidence_threshold": 0.25,
      "iou_threshold": 0.45,
      "max_detections": 1000
    },
    "model_info": {
      "status": "loaded",
      "model_path": "models/GarIA.pt",
      "device": "cpu",
      "task": "detect"
    }
  }
}
```

---

## 🎨 Classes Detectadas

A API detecta 4 tipos principais de resíduos recicláveis:

| ID | Classe | Descrição |
|----|--------|-----------|
| 0 | `plastic` | Materiais plásticos (garrafas, embalagens, etc.) |
| 1 | `metal` | Metais (latas, alumínio, etc.) |
| 2 | `paper` | Papéis (jornais, revistas, papelão, etc.) |
| 3 | `glass` | Vidros (garrafas, potes, etc.) |

---

## 📊 Estrutura de Dados

### BoundingBox
```json
{
  "x1": 34.2,          // Coordenada X do canto superior esquerdo
  "y1": 18.7,          // Coordenada Y do canto superior esquerdo
  "x2": 140.9,         // Coordenada X do canto inferior direito
  "y2": 220.4,         // Coordenada Y do canto inferior direito
  "width": 106.7,      // Largura da caixa
  "height": 201.7,     // Altura da caixa
  "center": [87.55, 119.55]  // Coordenadas do centro [x, y]
}
```

---

## ❌ Códigos de Erro

### 400 - Bad Request
```json
{
  "error": "Descrição do erro",
  "code": "CODIGO_ERRO"
}
```

#### Códigos Comuns
- `NO_IMAGE_FILE` - Nenhum arquivo de imagem fornecido
- `NO_FILE_SELECTED` - Nenhum arquivo selecionado
- `INVALID_FILE_TYPE` - Tipo de arquivo não suportado
- `INVALID_CONFIDENCE` - Parâmetro confidence inválido
- `INVALID_IOU_THRESHOLD` - Parâmetro iou_threshold inválido
- `INVALID_MAX_DETECTIONS` - Parâmetro max_detections inválido
- `IMAGE_PROCESSING_ERROR` - Erro ao processar imagem
- `NO_IMAGE_URL` - URL da imagem não fornecida

### 500 - Internal Server Error
```json
{
  "error": "Erro interno do servidor",
  "code": "INTERNAL_ERROR",
  "details": "Detalhes técnicos (apenas em modo debug)"
}
```

---

## 🔧 Configurações Avançadas

### Parâmetros de Detecção

#### Confidence (Confiança)
- **Range**: 0.0 - 1.0
- **Padrão**: 0.25
- **Descrição**: Define a confiança mínima necessária para considerar uma detecção válida. Valores menores incluem mais detecções (mas potencialmente menos precisas), valores maiores são mais restritivos.

#### IoU Threshold (Intersection over Union)
- **Range**: 0.0 - 1.0
- **Padrão**: 0.45
- **Descrição**: Usado no Non-Maximum Suppression (NMS) para remover detecções duplicadas/sobrepostas. Valores menores removem mais sobreposições.

#### Max Detections
- **Range**: 1 - ∞
- **Padrão**: 1000
- **Descrição**: Número máximo de detecções retornadas por imagem.

---

## 📱 Casos de Uso

### 1. Aplicativo Educativo
```python
def analisar_foto_reciclagem(imagem_path):
    with open(imagem_path, 'rb') as f:
        response = requests.post(
            'http://localhost:5000/api/detection/detect',
            files={'image': f},
            data={'confidence': 0.3}
        )
    
    resultado = response.json()
    
    # Feedback educativo
    if resultado['total_detections'] > 0:
        print(f"🎉 Detectei {resultado['total_detections']} itens recicláveis!")
        for classe in resultado['unique_classes']:
            print(f"♻️ {classe.title()}: {resultado['counts'][classe]} item(s)")
    else:
        print("😔 Nenhum material reciclável detectado na imagem")
    
    return resultado
```

### 2. Dashboard de Monitoramento
```javascript
async function monitorarReciclagem(urls_cameras) {
    const resultados = [];
    
    for (const url of urls_cameras) {
        const response = await fetch('/api/detection/detect/url', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                image_url: url,
                config: { confidence: 0.4 }
            })
        });
        
        const dados = await response.json();
        resultados.push({
            camera: url,
            deteccoes: dados.total_detections,
            tipos: dados.unique_classes,
            timestamp: dados.timestamp
        });
    }
    
    return resultados;
}
```

### 3. Jogo de Reciclagem
```python
def verificar_separacao_lixo(imagem_lixeira, tipo_esperado):
    """
    Verifica se o usuário separou corretamente o lixo
    """
    response = requests.post(
        'http://localhost:5000/api/detection/detect',
        files={'image': open(imagem_lixeira, 'rb')},
        data={'confidence': 0.4}
    )
    
    resultado = response.json()
    
    # Lógica do jogo
    tipos_detectados = resultado['unique_classes']
    
    if tipo_esperado in tipos_detectados:
        pontos = 10 * resultado['counts'][tipo_esperado]
        return {
            'correto': True,
            'pontos': pontos,
            'mensagem': f'🎉 Correto! +{pontos} pontos!'
        }
    else:
        return {
            'correto': False,
            'pontos': 0,
            'mensagem': f'❌ Ops! Era para ser {tipo_esperado}'
        }
```
---

## 🤝 Suporte e Contribuição

### Contribuindo
1. Fork do projeto
2. Crie feature branch: `git checkout -b feat/nova-feature`
3. Commit: `git commit -m "feat: adiciona nova feature"`
4. Push: `git push origin feat/nova-feature`
5. Abra Pull Request

---

## 📄 Licença

Este projeto está licenciado sob **AGPL-3.0** - veja o arquivo [LICENSE.txt](LICENSE.txt) para detalhes.

### ⚖️ Resumo da Licença
- ✅ Uso comercial e não-comercial
- ✅ Modificação e distribuição
- ✅ Uso via API HTTP (sem obrigação de código aberto para clientes)
- ❗ Modificações devem permanecer sob AGPL-3.0
- ❗ Código-fonte deve estar disponível para usuários de rede

---

> **Mantido com foco em impacto ambiental positivo. Boa reciclagem!** ♻️

---

## 📞 Contato

- **Projeto**: GarIA - Garbage + IA
- **Autor**: Lucas da Silva
- **Licença**: AGPL-3.0-only

Para mais informações, consulte o [README.md](README.md) principal do projeto.
