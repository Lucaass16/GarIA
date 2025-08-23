

## ♻️ GarIA – API de Detecção de Resíduos Recicláveis

Uma API open source que usa visão computacional (YOLO) para identificar tipos de lixo reciclável (plastic, metal, paper, glass) em imagens. O objetivo é promover educação ambiental de forma lúdica e tecnológica, facilitando que apps, jogos, dashboards e experiências interativas conversem sobre reciclagem com dados reais de detecção.  

"GarIA" = Garbage + IA – detecta, classifica e inspira mudança.


---

## 🌍 Visão & Propósito

| Dimensão | Descrição |
|----------|-----------|
| Educação | Fornecer feedback imediato sobre tipos de recicláveis presentes em uma imagem para apoiar jogos educativos, apps escolares e hackathons verdes. |
| Sustentabilidade | Facilitar experiências que estimulem a correta separação de resíduos. |
| Acessibilidade Tecnológica | Expor um endpoint simples (REST + Swagger) para qualquer linguagem consumir. |
| Extensibilidade | Base pensada em DDD para evoluir para novos materiais, métricas e integrações. |

## 🧠 O que a API faz hoje

Entrada: imagem (upload ou URL).  
Saída: lista de detecções com bounding boxes, classe, confiança, estatísticas agregadas e metadados da imagem.

Classes suportadas (modelo padrão `GarIA.pt`):
- plastic
- metal
- paper
- glass

Cada detecção inclui: `class_id`, `class_name`, `confidence`, `bbox (x1, y1, x2, y2, width, height, center)`, `bbox_normalized` e estatísticas globais (total, classes únicas, média de confiança, tempo de processamento).

---

# 🔧 Arquitetura (Flask + DDD Inspirado)

Este projeto implementa uma arquitetura Flask inspirada em Domain-Driven Design (DDD) e segregação de responsabilidades.

## 🏗️ Estrutura da Arquitetura

```
app/
├── domain/                 # Camada de Domínio
│   ├── entities/          # Entidades de negócio
│   ├── repositories/      # Interfaces de repositório
│   └── services/          # Serviços de domínio
├── infrastructure/        # Camada de Infraestrutura
│   ├── config/           # Configurações
│   ├── database/         # Configuração do banco
│   └── external/         # Serviços externos
├── services/             # Serviços de aplicação
├── repositories/         # Implementações de repositório
├── controllers/          # Controladores HTTP
├── dto/                  # Data Transfer Objects
├── middlewares/          # Middlewares customizados
└── utils/               # Utilitários
```

## 📋 Responsabilidades das Camadas

### Domain Layer (`app/domain/`)
- **Entities**: Objetos de negócio que encapsulam regras e comportamentos
- **Repositories**: Interfaces que definem contratos para acesso a dados
- **Services**: Lógica de negócio complexa que não pertence a uma entidade específica

### Infrastructure Layer (`app/infrastructure/`)
- **Config**: Configurações da aplicação (desenvolvimento, produção, teste)
- **Database**: Configuração e conexão com banco de dados
- **External**: Integrações com APIs e serviços externos

### Application Layer
- **Services** (`app/services/`): Orquestram operações e coordenam entre camadas
- **Controllers** (`app/controllers/`): Endpoints HTTP e manipulação de requisições
- **DTO** (`app/dto/`): Objetos para transferência de dados entre camadas
- **Repositories** (`app/repositories/`): Implementações concretas dos repositórios

### Support Layer
- **Middlewares** (`app/middlewares/`): Interceptadores de requisições
- **Utils** (`app/utils/`): Funções utilitárias e helpers

## 🚀 Como Executar (Quick Start)

1. **Ativar o ambiente virtual**:
   ```bash
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

2. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variáveis de ambiente**:
   ```bash
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   ```

4. **Executar a aplicação**:
   ```powershell
   python .\main.py
   ```

5. **Abrir documentação interativa (Swagger)**:  
   http://localhost:5000/docs/

### Opcional (Sugestão Docker – ainda não incluído)
Adicionar um `Dockerfile` permitiria empacotar o modelo e a API facilmente. (Roadmap.)

## 🛠️ Configuração de Ambiente

### Variáveis de Ambiente
- `FLASK_ENV`: ambiente (development, production, testing)
- `FLASK_DEBUG`: modo debug (True/False)
- `SECRET_KEY`: chave secreta para sessões
- `DATABASE_URL`: URL de conexão com banco de dados

### Ambientes Disponíveis
- **Development**: Configuração para desenvolvimento local
- **Production**: Configuração otimizada para produção
- **Testing**: Configuração para execução de testes

## 📦 Dependências Principais

- **Flask**: Framework web
- **Flask-SQLAlchemy**: ORM para banco de dados
- **Flask-CORS**: Suporte a CORS
- **Flask-JWT-Extended**: Autenticação JWT
- **Marshmallow**: Serialização e validação de dados
- **python-dotenv**: Gerenciamento de variáveis de ambiente

## 🎯 Princípios Aplicados

1. **Domain-Driven Design (DDD)**
   - Separação clara entre domínio e infraestrutura
   - Entidades ricas em comportamento
   - Serviços de domínio para lógica complexa

2. **Segregação de Responsabilidades**
   - Cada camada tem uma responsabilidade específica
   - Inversão de dependência entre camadas
   - Interfaces bem definidas

3. **Clean Architecture**
   - Dependências apontam para dentro (domínio)
   - Camadas externas dependem das internas
   - Testabilidade e manutenibilidade

## 🤖 Detecção com YOLO

O projeto inclui integração completa com modelos YOLO para detecção de objetos:

### 📁 Estrutura ML
```
app/
├── domain/ml/              # Entidades de ML
│   └── entities.py        # Detection, BoundingBox, ModelConfiguration
├── infrastructure/ml/     # Infraestrutura ML
│   ├── models/           # Cache de modelos carregados
│   └── yolo_model.py     # Carregamento e inferência YOLO
├── services/ml/          # Serviços de aplicação ML
│   └── object_detection_service.py
└── controllers/
    └── ml_controller.py  # API endpoints para ML
models/                   # Armazenamento de modelos (.pt files)
├── README.md            # Guia de uso dos modelos
└── [seus_modelos.pt]    # Coloque seus modelos aqui
```

### 🚀 Endpoints Principais

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/detection/detect` | Upload de imagem (multipart/form-data) para detecção |
| POST | `/api/detection/detect/url` | Detecção a partir de URL de imagem |
| GET | `/api/detection/model/status` | Status e metadados do modelo YOLO carregado |
| POST | `/api/detection/model/config` | Atualiza configuração do modelo (thresholds / classes) |
| GET | `/api/detection/health` | Health check do serviço |

Obs: Os prefixos reais podem variar conforme o blueprint (`/api` + namespaces). Verifique no Swagger.

### 🧪 Exemplo de Requisição (Upload)

```bash
curl -X POST http://localhost:5000/api/detection/detect \
   -F "image=@exemplo.jpg" \
   -F "confidence=0.30" \
   -F "iou_threshold=0.45"
```

### 🌐 Exemplo via URL

```bash
curl -X POST http://localhost:5000/api/detection/detect/url \
   -H "Content-Type: application/json" \
   -d '{
      "image_url": "https://exemplo.com/imagem.jpg",
      "config": {"confidence": 0.3, "max_detections": 200}
   }'
```

### 📦 Exemplo de Resposta

```json
{
   "success": true,
   "detections": [
      {
         "class_id": 0,
         "class_name": "plastic",
         "confidence": 0.87,
         "bbox": {
            "x1": 34.2,
            "y1": 18.7,
            "x2": 140.9,
            "y2": 220.4,
            "width": 106.7,
            "height": 201.7,
            "center": [87.55, 119.55]
         },
         "bbox_normalized": {"x": 0.34, "y": 0.42, "width": 0.21, "height": 0.38}
      }
   ],
   "statistics": {
      "total_detections": 1,
      "unique_classes": ["plastic"],
      "avg_confidence": 0.87,
      "max_confidence": 0.87,
      "min_confidence": 0.87,
      "processing_time": 0.1532
   },
   "image_info": {"width": 640, "height": 480, "mode": "RGB", "source_type": "pil_image"},
   "processing_time": 0.1532,
   "timestamp": "2025-01-01T12:00:00.000000"
}
```

### � Uso em Python

```python
import requests

with open("exemplo.jpg", "rb") as f:
      resp = requests.post(
            "http://localhost:5000/api/detection/detect",
            files={"image": f},
            data={"confidence": 0.3}
      )
print(resp.json())
```

---

## 🧩 Entidades de Domínio (Simplificadas)

| Entidade | Papel |
|----------|-------|
| BoundingBox | Representa a área do objeto (coord. absolutas + width / height / center). |
| Detection | Uma detecção única com classe, confiança e bbox. |
| DetectionResult | Agregado de detecções + estatísticas + metadados. |
| ModelConfiguration | Configurações de inferência (confidence / IoU / max_detections / target_classes). |

Características técnicas:
- Normalização de bounding boxes (`xywhn`) para uso em interfaces responsivas.
- Estatísticas agregadas prontas para dashboards.
- Recarregamento dinâmico de modelo (config via endpoint).
- Suporte a diferentes fontes: upload, URL, PIL Image, numpy array.

---

## ⚙️ Variáveis de Ambiente Principais

| Variável | Descrição | Default |
|----------|-----------|---------|
| FLASK_ENV | Ambiente (`development`/`production`/`testing`) | development |
| FLASK_DEBUG | Ativa debug | False |
| FLASK_HOST | Host bind | 127.0.0.1 |
| FLASK_PORT | Porta da API | 5000 |
| SECRET_KEY | Sessões / segurança | dev-secret-key-change-in-production |
| DATABASE_URL | Futuro uso (ORM) | sqlite:///app.db |
| CORS_ORIGINS | Origens permitidas | * |

Sugestão: crie um arquivo `.env` baseado em `.env.example` (adicionar no futuro).

---

## 🛠️ Stack Técnica

- Flask + Flasgger (Swagger UI)  
- Ultralytics YOLO (`ultralytics`)  
- Pillow / NumPy para manipulação de imagens  
- Estrutura inspirada em DDD (domain / services / infrastructure)  
- Python 3.12+  

### Performance & Observações
- Tempo de inferência depende de CPU vs GPU (usa Torch automaticamente se disponível).  
- Modelo é carregado on-demand e reutilizado (cache simples em memória).  
- Para produção: considerar gunicorn + workers e pré-carregar modelo no startup.

---

## 🤝 Contribuindo

1. Faça um fork
2. Crie uma branch: `feat/nome-da-feature`
3. Commit: mensagens objetivas (ex: `feat: adiciona filtro por classe`)
4. Abra PR descrevendo motivação + screenshots/logs
5. Mantenha coerência com camadas (não pule domínio direto para controller)

Ideias bem-vindas: gamificação, ranking de reciclagem, export de métricas Prometheus, Docker, testes unitários, novos materiais.

---

## 🗺️ Roadmap (Resumo)

| Status | Item |
|--------|------|
| ✅ | Estrutura base Flask / Swagger |
| ✅ | Integração YOLO & entidades domínio |
| 🔄 | Refinar respostas e padronizar erros |
| ⏳ | Autenticação / autorização |
| ⏳ | Banco & repositórios (histórico de detecções) |
| ⏳ | Cache persistente de modelos / warmup |
| ⏳ | Docker + CI (lint + tests) |
| ⏳ | Métricas e observabilidade |
| ⏳ | Testes unitários e de carga |

---

## 📄 Licença

[![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](LICENSE.txt)

Este projeto está licenciado sob a **GNU Affero General Public License v3 (AGPL-3.0)**.

Resumo (informal, consulte o texto oficial):
- Código-fonte completo deve estar disponível para usuários que interagem via rede.
- Modificações e distribuições derivadas devem permanecer sob AGPL-3.0.
- Não há garantia – uso por sua conta e risco.
- Clientes externos consumindo apenas a API via HTTP NÃO são obrigados a abrir seu próprio código.

Exemplo de atribuição em fork:
```
Derivado de GarIA – https://github.com/Lucaass16/GarIA
Copyright (c) 2025 Lucas
Licença: AGPL-3.0. Veja LICENSE.txt.
```

### Cabeçalhos recomendados (SPDX)
```python
# SPDX-License-Identifier: AGPL-3.0-only
```

### Dependência Ultralytics
O uso de `ultralytics` (AGPL) motivou a adoção da mesma licença para manter conformidade. Para relicenciar de forma mais permissiva seria necessário substituir ou obter licença comercial apropriada.

---

## 💬 FAQ Rápido

| Pergunta | Resposta |
|----------|----------|
| Posso trocar o modelo? | Sim, via `/api/detection/model/config` (desde que o `.pt` esteja em `models/`). |
| Suporta GPU? | Se PyTorch detectar CUDA, o YOLO usará automaticamente. |
| Como escalar? | Container + gunicorn + preload + autoscaling horizontal. |
| Posso adicionar novas classes? | Re-treine um modelo YOLO com dataset contendo as novas classes e coloque o `.pt` em `models/`. |

---

## 🎯 Por que usar o GarIA?

- Simples de integrar (HTTP + JSON)  
- Foco em educação ambiental e impacto social  
- Flexível para ser base de hackathons, TCCs e protótipos verdes  
- Extensível para métricas, gamificação e aprendizagem contínua  

Se isso te ajudou, compartilhe ou contribua! 🙌

---

> Mantido com foco em impacto ambiental positivo. Boa reciclagem! ♻️

