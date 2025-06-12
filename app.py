from flask import Flask, request, jsonify, send_from_directory
from functions import classify_abstract_combined, load_json

app = Flask(__name__)

# Charger les mots-clés des thèmes
themes_keywords = load_json('data/themes_keywords.json')

@app.route('/classify', methods=['POST'])
def classify():
    data = request.json
    abstract_text = data.get('text', '')
    
    # Classification
    themes = classify_abstract_combined(abstract_text, themes_keywords)
    
    return jsonify({'themes': themes})


@app.route('/')
def index():
    return send_from_directory('static', 'classification.html')

if __name__ == '__main__':
    app.run(debug=True)

