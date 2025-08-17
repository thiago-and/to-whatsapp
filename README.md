# Conversor para WhatsApp

Este projeto fornece uma interface web simples para fazer upload e converter vídeos otimizados para o WhatsApp.

## Principais componentes
- Backend: Python + Flask
- Frontend: Bootstrap + XHR upload + polling
- Ferramentas: ffmpeg

## Instalação local

1. Instale Python 3 + ffmpeg:

   ```bash
   sudo apt update; sudo apt install -y python3 python3-venv python3-pip ffmpeg
   git clone https://github.com/thiago-and/to-whatsapp
   cd to-whatsapp
   ```

   Windows:

   Instale Python e ffmpeg e entre na pasta to-whatsapp.

2. Crie um venv e instale dependências:

   ```bash
   python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
   ```

3. Rode o servidor:

   ```bash
   python app.py
   ```

4. Abra http://localhost:5000

## Instalação no Docker

### Linux

1. Rode o script:

```bash
curl -sSL https://raw.githubusercontent.com/thiago-and/to-whatsapp/main/install.sh | bash
```
2. Abra http://seu-ip:5000

### Windows

1. Instale Docker Desktop.

2. Baixar o projeto:
```bash
git clone https://github.com/thiago-and/to-whatsapp
```

3. Rode o servidor:
```bash
cd to-whatsapp
docker-compose up -d
```

2. Abra http://localhost:5000