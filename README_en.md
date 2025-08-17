# WhatsApp Video Converter

This project provides a simple web interface to upload and convert videos optimized for WhatsApp.

## Main components
- Backend: Python + Flask
- Frontend: Bootstrap + XHR upload + polling
- Tools: ffmpeg

## Local installation

1. Install Python 3 and ffmpeg:

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip ffmpeg
git clone https://github.com/thiago-and/to-whatsapp
cd to-whatsapp
```

Windows:

Install Python and ffmpeg, then open the `to-whatsapp` folder.

2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Run the server:

```bash
python app.py
```

4. Open http://localhost:5000 in your browser.

## Docker installation

### Linux (recommended)

1. Run the installer script:

```bash
curl -sSL https://raw.githubusercontent.com/thiago-and/to-whatsapp/main/install.sh | bash
```

2. Open http://your-server-ip:5000

### Windows (Docker Desktop)

1. Install Docker Desktop.

2. Clone the project:

```bash
git clone https://github.com/thiago-and/to-whatsapp
```

3. Start the service:

```bash
cd to-whatsapp
docker compose up -d
```

4. Open http://localhost:5000
