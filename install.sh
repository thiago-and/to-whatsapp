#!/bin/bash

# Script de instalação automática do to-whatsapp
# Uso: curl -sSL https://raw.githubusercontent.com/thiago-and/to-whatsapp/main/install.sh | bash

set -e

echo "🚀 Instalando to-whatsapp..."

# Verificar se docker está instalado
if ! command -v docker &> /dev/null; then
    echo "📦 Instalando Docker..."
    sudo apt update
    sudo apt install -y docker.io docker-compose git
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker $USER
    echo "⚠️  Você precisará fazer logout/login para usar Docker sem sudo"
fi

# Verificar se docker-compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Instalando Docker Compose..."
    sudo apt install -y docker-compose
fi

# Clonar repositório se não existir
if [ ! -d "to-whatsapp" ]; then
    echo "📥 Clonando repositório..."
    git clone https://github.com/thiago-and/to-whatsapp
fi

cd to-whatsapp

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p uploads output logs

# Definir permissões corretas
chmod 755 uploads output logs

# Subir aplicação
echo "🐳 Iniciando aplicação..."
docker-compose up -d

# Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 10

# Verificar status
if docker-compose ps | grep -q "Up"; then
    echo "✅ Aplicação instalada com sucesso!"
    echo "🌐 Acesse: http://$(hostname -I | awk '{print $1}'):5000"
    echo "📋 Para ver logs: docker-compose logs -f app"
    echo "🛑 Para parar: docker-compose down"
else
    echo "❌ Erro na inicialização. Verifique os logs:"
    docker-compose logs app
fi
