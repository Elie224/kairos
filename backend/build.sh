#!/bin/bash
# Script de build pour Render

echo "🔨 Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build terminé avec succès!"
