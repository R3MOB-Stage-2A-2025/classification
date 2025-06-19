# Publication Classification Tool

Cet outil permet de classifier les publications selon les 10 thèmes scientifiques définis par le réseau.
La méthode utilisée repose sur une recherche de mots-clés dans l'abstract (en anglais) de chaque publication, afin de les classer automatiquement dans la catégorie appropriée.

## Starting the Flask server

1. Use it for **python3.13**:

```bash
cd classification/backend/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

2. Then do in another terminal:

```bash
cd classification/backend/
python Server.py
```

3. Tests only, use the frontend:

```bash
# Open another terminal and do this:
cd frontend/
npm install
npm run dev
```

## Lancer les tests 

Pour lancer les tests de performance de l'outil de classification, suivez les étapes ci-dessous :

1. Ouvrir votre terminal

2. Naviguer vers le répertoire du code en utilisant la commande :

```bash
cd classification/backend
```

3. Exécuter les tests :

```bash
# (.venv) $
python tests.py
```

## Observer les resultats des tests

Après avoir lancer les tests de performance, les fichiers suivants sont créés dans le repertoire results/ : 

- classification_results.json contient les résultats détaillés de la classification pour chaque publication. Pour chaque abstract, sont affichés : les thèmes réels attribués à la publication, et ceux trouvés par l'outil de classification.

- comparaison_results.json contient les métriques de performance (precision, recall, accuracy, f1-scores) pour chaque thème scientifique utilisé dans la classification.

- theme_summary.json contient le nombre total de publications, assignées à chaque thème, testés et le nombre de classification parfaitement correctes (i.e. l'ensemble des thémes trouvés correspond exactement à l'ensemble de thème réels) pour chaque thème.

### EOF

