# Conversor para WhatsApp

Este projeto fornece uma interface web simples para fazer upload e converter vídeos otimizados para o WhatsApp.

## Principais componentes
- Backend: Flask (app.py)
- Frontend: templates/index.html (Bootstrap + XHR upload + polling)
- Requisitos: Python 3.8+, ffmpeg/ffprobe

## Quick start local

1. Instale Python 3:

   ```powershell
   sudo apt update; sudo apt install -y python3 python3-venv python3-pip ffmpeg
   ```

   No windows, instale Python e ffmpeg

2. Crie um venv e instale dependências:

   ```powershell
   python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
   ```

3. Rode o servidor (desenvolvimento):

   ```powershell
   python app.py
   ```

4. Abra http://localhost:5000

## Deploy no Docker

1. Na máquina Ubuntu:

   ```bash
   sudo apt update; sudo apt install -y docker.io docker-compose git
   git clone https://github.com/thiago-and/to-whatsapp
   cd to-whatsapp
   docker-compose up -d
   ```

## Arquivos importantes
- `app.py` — servidor Flask (endpoints: /, /upload, /progress/<job_id>, /download/<file>, /cancel/<job_id>)
- `templates/index.html` — frontend responsivo com upload XHR e polling
- `Dockerfile` e `docker-compose.yml` — configuração para containerização
- `uploads/`, `output/` — diretórios montados como volumes no Docker
- `logs/` — logs por job gerados pelo backend

## Licença / notas
