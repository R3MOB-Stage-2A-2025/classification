# Publication Classification Tool

This tool is a *keyword* analysis based on *TF-IDF* and *Similarity Cosine*.

It permits to classify a text among the themes that you can found in
`classification/bakcend/data/themes_keywords.json`.

## Parsing module

You will need to clone the *parsing module* using this command:

```bash
cd classification/
git submodule update --init --recursive
```

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

## Launch the classification tests

You can do this:

```bash
cd classification/backend
# (.venv) $
python tests.py
```

### Result observations

In the repertory `classification/backend/results`, you will find:

- **classification_results.json**: the details for each tested publication.

- **comparaison_results.json**: the metrics like *precision*, *accuracy*,
*recall* and *F1 scores*.

- **theme_summary.json** the total numbers of publications for each themes.

### EOF

