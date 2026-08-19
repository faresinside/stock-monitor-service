#!/bin/bash

# Script d'installation automatique pour Raspberry Pi
# Portasplit Monitor

set -e

echo "🚀 Installation de Portasplit Monitor sur votre Raspberry Pi..."

# Dossier d'installation
INSTALL_DIR=$(pwd)

# Verification de Python3
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 n'est pas installé. Installation..."
    sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip
fi

# Création de l'environnement virtuel si non existant
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel Python..."
    python3 -m venv venv
fi

echo "🔄 Installation / Mise à jour des dépendances..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Création du fichier .env si absent
if [ ! -f ".env" ]; then
    echo "📝 Création du fichier .env à partir du modèle..."
    cp .env.example .env
fi

# Configuration du service Systemd
SERVICE_FILE="/etc/systemd/system/portasplit-monitor.service"

echo "⚙️ Configuration du service systemd : $SERVICE_FILE..."

sudo bash -c "cat <<EOF > $SERVICE_FILE
[Unit]
Description=Portasplit Stock Monitor Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

echo "🔄 Rechargement de systemd..."
sudo systemctl daemon-reload
echo "🚀 Activation et démarrage du service..."
sudo systemctl enable portasplit-monitor.service
sudo systemctl restart portasplit-monitor.service

echo ""
echo "✅ Installation terminée avec succès !"
echo "🌐 Accédez au Dashboard sur votre réseau local : http://$(hostname -I | awk '{print $1}'):8000"
echo "📜 Pour voir les logs du service : sudo journalctl -u portasplit-monitor.service -f"
