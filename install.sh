#!/bin/bash

# Script de instalação automática do to-whatsapp
# Uso: curl -sSL https://raw.githubusercontent.com/thiago-and/to-whatsapp/main/install.sh | bash

set -e

echo "🚀 Instalando to-whatsapp..."

# Verificar se docker está instalado
if ! command -v docker &> /dev/null; then
    echo "📦 Instalando Docker..."
    sudo apt update
    sudo apt install -y docker.io docker-compose-plugin git
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker $USER
    echo "⚠️  Você precisará fazer logout/login para usar Docker sem sudo"
fi

# Verificar se docker compose está instalado
if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
    echo "📦 Instalando Docker com Compose..."
    sudo apt update
    sudo apt install -y docker.io docker-compose-plugin git
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker $USER
    echo "⚠️  Você precisará fazer logout/login para usar Docker sem sudo"
fi

# Clonar repositório se não existir
if [ ! -d "to-whatsapp" ]; then
    echo "📥 Clonando repositório..."
    git clone https://github.com/thiago-and/to-whatsapp
fi

cd to-whatsapp

# Detectar UID/GID do usuário atual
CURRENT_UID=$(id -u)
CURRENT_GID=$(id -g)

echo "👤 Detectado usuário: UID=$CURRENT_UID GID=$CURRENT_GID"

# Criar arquivo .env com UID/GID do usuário atual
cat > .env << EOF
USER_UID=$CURRENT_UID
USER_GID=$CURRENT_GID
FLASK_ENV=production
EOF

# Criar diretórios necessários com permissões corretas
echo "📁 Criando diretórios..."
mkdir -p uploads output logs
chown -R $CURRENT_UID:$CURRENT_GID uploads output logs
chmod 755 uploads output logs

# Subir aplicação
echo "🐳 Iniciando aplicação..."
docker compose up -d --build

# Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 15

# Verificar status
if docker compose ps | grep -q "Up"; then
    echo "✅ Aplicação instalada com sucesso!"
    echo "🌐 Acesse: http://$(hostname -I | awk '{print $1}'):5000"
    echo "📋 Para ver logs: docker compose logs -f app"
    echo "🛑 Para parar: docker compose down"
else
    echo "❌ Erro na inicialização. Verifique os logs:"
    docker compose logs app
fi
