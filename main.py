"""GarIA – API de Detecção de Resíduos Recicláveis

SPDX-License-Identifier: AGPL-3.0-only
Copyright (c) 2025 Lucas da Silva (Autor do projeto)

Este arquivo faz parte do GarIA e está licenciado sob os termos da
GNU General Public License v3.0. Consulte o arquivo LICENSE.txt para mais detalhes.
"""

import os
from app import create_app
from app.infrastructure.config.settings import config
from flasgger import Swagger

config_name = os.environ.get('FLASK_ENV', 'development')
config_class = config.get(config_name, config['default'])

app = create_app(config_class)

if __name__ == '__main__':
    debug_mode = False
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))

    if not debug_mode:
        from app.infrastructure.ml.download_model import download_model
        download_model()
    
    print(f"🚀 Iniciando aplicação em {config_name} mode")
    print(f"📍 URL: http://{host}:{port}")
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        use_reloader=debug_mode
    )
