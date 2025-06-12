#!/bin/bash

# Démarrer l'outil de classification
cd "$(dirname "$0")"
python3 app.py &
FLASK_PID=$!

# Ouvrir l'URL avec le navigateur par défaut
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://127.0.0.1:5000 &
elif [[ "$OSTYPE" == "darwin"* ]]; then
    open http://127.0.0.1:5000 &
else
    echo "OS non supporté"
    exit 1
fi

# Attendre que le processus soit arrêté
wait $FLASK_PID

# Arrêter l'outil de classification proprement
if ps -p $FLASK_PID > /dev/null; then
    kill $FLASK_PID
fi

