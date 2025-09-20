# Base image Python
FROM python:3.11-slim

# Variables d'environnement pour Django
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Création du répertoire de l'app
WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copie du code
COPY . .

# Commande par défaut pour lancer le serveur
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]

