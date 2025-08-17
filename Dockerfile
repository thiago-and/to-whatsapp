FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Argumentos para UID/GID dinâmicos
ARG USER_UID=1000
ARG USER_GID=1000

# dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg curl ca-certificates && rm -rf /var/lib/apt/lists/*

# criar usuário não-root com UID/GID fornecidos
RUN groupadd -r appuser -g $USER_GID && useradd -r -g appuser -u $USER_UID -m -s /bin/bash appuser

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# criar diretórios e definir permissões
RUN mkdir -p /app/uploads /app/output /app/logs && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 CMD curl -f http://127.0.0.1:5000/ || exit 1

CMD ["python", "app.py"]
