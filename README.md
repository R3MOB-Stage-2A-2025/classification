# Outils de classification des publications

Cet outil permet de classifier les publications selon les 10 thèmes scientifiques définis par le réseau. La méthode utilisée repose sur une recherche de mots-clés dans l'abstract (en anglais) de chaque publication, afin de les classer automatiquement dans la catégorie appropriée.

## Starting the Flask server

Use it for **python3.13**:

```bash
cd classification/code/
python3 -m venv .env_classification
source .env_classification/bin/activate
pip install -r requirements.txt
```

where the *requirements.txt* file is:

```python
spacy==3.8.7
flask==3.1.1
nltk==3.9.1
scikit-learn==1.6.1
```

Then do:

```bash
python -m spacy download en_core_web_lg
./start_classification.sh
```

If there is the error ``port 5000 already used``, just do:

```bash
ps aux | grep app.py
kill -9 <app.py pid>
```

## Architecture du code

├── app.py     # Fichier permettant d'éxecuter l'outil de classification
|
├── data     ## Répertoire contenant les données nécessaires à la classification
│   ├── data.json
│   └── themes_keywords.json
|
├── functions.py     # Fichier contenant les fonctions utilitaires pour la classification
|
├── README.md
|
├── results     ## Répertoire stockant les fichiers produits par l'éxecution des tests
│   ├── classification_results.json
│   ├── comparison_results.json
│   └── theme_summary.json
|
├── start_classification.sh     # Script pour démarrer facilement l'outil de classification
|
├── static      ## Répertoire contenant les fichiers front-end de l'outil de classification
│   ├── classification.css
│   ├── classification.html
│   └── classification.js
|
└── tests.py    # Fichier permettant d'éxecuter les tests

## Lancer l'outils de classification

Pour lancer l'outil de classification, suivez les étapes ci-dessous :

    1. Ouvrir votre terminal

    2. Naviguer vers le répertoire du code en utilisant la commande :
        cd chemin_vers_le_repertoire_contenant_le_code/

    3. Exécuter le script de classification :
        ./start_classification.sh

## Lancer les tests 

Pour lancer les tests de performance de l'outil de classification, suivez les étapes ci-dessous :

    1. Ouvrir votre terminal

    2. Naviguer vers le répertoire du code en utilisant la commande :
        cd chemin_vers_le_repertoire_contenant_le_code/

    3. Exécuter les tests :
        python3 tests.py

## Observer les resultats des tests

Après avoir lancer les tests de performance, les fichiers suivants sont créés dans le repertoire results/ : 

    - classification_results.json contient les résultats détaillés de la classification pour chaque publication. Pour chaque abstract, sont affichés : les thèmes réels attribués à la publication, et ceux trouvés par l'outil de classification.
    
    - comparaison_results.json contient les métriques de performance (precision, recall, accuracy, f1-scores) pour chaque thème scientifique utilisé dans la classification.
    
    - theme_summary.json contient le nombre total de publications, assignées à chaque thème, testés et le nombre de classification parfaitement correctes (i.e. l'ensemble des thémes trouvés correspond exactement à l'ensemble de thème réels) pour chaque thème.
