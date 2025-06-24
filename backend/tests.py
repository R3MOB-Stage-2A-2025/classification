import json
import os

from functions import load_json
from functions import update_metrics_for_theme, get_all_metrics, get_metrics_for_each_theme

from functions import classify_abstract_by_keywords
from functions import classify_abstract_by_spaCy
from functions import classify_abstract_TF_IDF
from functions import classify_abstract_combined

# Choix de la fonction de classification à tester
fonction_tested = classify_abstract_combined

# Chargement des données
data = load_json('data/data.json')
themes_keywords = load_json('data/themes_keywords.json')


# Fonction de lancement des tests
def main():

    tp = {theme: 0 for theme in themes_keywords.keys()}
    fp = {theme: 0 for theme in themes_keywords.keys()}
    fn = {theme: 0 for theme in themes_keywords.keys()}
    tn = {theme: 0 for theme in themes_keywords.keys()}
    
    theme_counts = {theme: 0 for theme in themes_keywords.keys()}
    theme_correct_count = {theme: 0 for theme in themes_keywords.keys()}
    exact_match_count = 0

    classification_results = []

    for entry in data:
        abstract_text = entry["abstract"]
        true_themes = set(entry.get("themes", []))
        classified_themes = set(fonction_tested(abstract_text, themes_keywords))

        for theme in true_themes:
            theme_counts[theme] += 1

        if true_themes == classified_themes:
            exact_match_count += 1

        for theme in themes_keywords.keys():
            update_metrics_for_theme(theme, true_themes, classified_themes, tp, fp, fn, tn)
            if theme in true_themes and theme in classified_themes:
                theme_correct_count[theme] += 1

        classification_results.append({
            'abstract': abstract_text,
            'true_themes': list(true_themes),
            'classified_themes': list(classified_themes)
        })

    # Calculer les métriques
    precisions, recalls, f1_scores, accuracies = get_metrics_for_each_theme(tp, fp, fn, tn, theme_counts, theme_correct_count)
    global_precision, global_recall, global_f1, global_accuracy = get_all_metrics(tp, fp, fn, tn)

    # Sauvegarder les résultats dans le dossier "results"
    os.makedirs('results', exist_ok=True)
    with open('results/comparison_results.json', 'w') as f:
        json.dump({'precisions': precisions, 'recalls': recalls, 'f1_scores': f1_scores, 'accuracies': accuracies}, f, indent=4)
    with open('results/classification_results.json', 'w') as f:
        json.dump(classification_results, f, indent=4)
    with open('results/theme_summary.json', 'w') as f:
        json.dump({'theme_counts': theme_counts, 'theme_correct_count': theme_correct_count}, f, indent=4)

    # Afficher un résumé des résultats
    print(f"Number of abstracts: {len(data)}")
    print(f"Exact Match Count: {exact_match_count}")
    print("")
    print(f"Global Precision: {global_precision * 100:.2f}%")
    print(f"Global Recall: {global_recall * 100:.2f}%")
    print(f"Global F1-Score: {global_f1 * 100:.2f}%")
    print(f"Global Accuracy: {global_accuracy * 100:.2f}%")


# Exécuter la fonction principale
if __name__ == '__main__':
    main()

