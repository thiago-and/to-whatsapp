# Conversor para WhatsApp

Este projeto fornece uma interface web simples para fazer upload e converter vídeos otimizados para o WhatsApp.

## Principais componentes
- Backend: Flask (app.py)
- Frontend: templates/index.html (Bootstrap + XHR upload + polling)
- Requisitos: Python 3.8+, ffmpeg/ffprobe

## Quick start (local)

1. Instale Python 3 e ffmpeg no Ubuntu:

   ```powershell
   # no Ubuntu (bash):
   sudo apt update; sudo apt install -y python3 python3-venv python3-pip ffmpeg
   
   # no Windows: instale Python e ffmpeg via choco/scoop/instalador
   ```

2. Crie um venv e instale dependências:

   ```powershell
   python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
   ```

3. Rode o servidor (desenvolvimento):

   ```powershell
   python app.py
   ```

4. Abra http://localhost:5000

## Docker (construir e rodar)

1. Construa a imagem:

   ```powershell
   docker build -t to-whatsapp .
   ```

2. Rode com volumes (mantém uploads/ e output/ no host):

   ```powershell
   docker run -p 5000:5000 -v %cd%/uploads:/app/uploads -v %cd%/output:/app/output to-whatsapp
   ```

3. Ou use docker-compose (recomendado):

   ```powershell
   docker-compose up -d
   ```

## Observações de produção
- A imagem já cria um usuário não-root e expõe healthcheck.
- Para produção preferível executar com um servidor WSGI (gunicorn) e configurar supervisão / systemd.

## Deploy no Ubuntu (passos rápidos)

1. Na máquina Ubuntu:

   ```bash
   sudo apt update; sudo apt install -y docker.io docker-compose git
   git clone <repo-url>
   cd to-whatsapp
   docker-compose up -d
   ```

## GitHub

1. Inicialize e envie:

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <git-url>
   git push -u origin main
   ```

## Arquivos importantes
- `app.py` — servidor Flask (endpoints: /, /upload, /progress/<job_id>, /download/<file>, /cancel/<job_id>)
- `templates/index.html` — frontend responsivo com upload XHR e polling
- `Dockerfile` e `docker-compose.yml` — configuração para containerização
- `uploads/`, `output/` — diretórios montados como volumes no Docker
- `logs/` — logs por job gerados pelo backend

## Próximos passos recomendados
- Adicionar `requirements.txt` (já incluído)
- Adicionar CI (GitHub Actions) para lint/build/tests
- Persistir `jobs` em DB se precisar sobreviver reinícios do servidor

## Licença / notas
- Não inclua uploads nem outputs no repo (.gitignore já configurado)
