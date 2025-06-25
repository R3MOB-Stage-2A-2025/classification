import json
import os

from functions import load_json
from functions import unsupervised_cosine_similarity

# Choix de la fonction de classification à tester
fonction_tested = unsupervised_cosine_similarity

# Chargement des données
data = load_json('data/data.json')
themes_keywords = load_json('data/scientificTheme_keywords.json')

##############################################################################
## METRIC FUNCTIONS
##############################################################################

def update_metrics_for_theme(theme, true_themes, classified_themes, tp, fp, fn, tn):
    if theme in true_themes and theme in classified_themes:
        tp[theme] += 1
    elif theme in true_themes and theme not in classified_themes:
        fn[theme] += 1
    elif theme not in true_themes and theme in classified_themes:
        fp[theme] += 1
    else:
        tn[theme] += 1


def get_metrics_for_each_theme(tp, fp, fn, tn, theme_counts, theme_correct_count):
    precisions = {}
    recalls = {}
    f1_scores = {}
    accuracies = {}

    for theme in tp.keys():
        if tp[theme] + fp[theme] > 0:
            precision = tp[theme] / (tp[theme] + fp[theme])
        else:
            precision = 0.0

        if tp[theme] + fn[theme] > 0:
            recall = tp[theme] / (tp[theme] + fn[theme])
        else:
            recall = 0.0

        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0

        if theme_counts[theme] > 0:
            accuracy = theme_correct_count[theme] / theme_counts[theme]
        else:
            accuracy = 0.0

        precisions[theme] = precision
        recalls[theme] = recall
        f1_scores[theme] = f1
        accuracies[theme] = accuracy

    return precisions, recalls, f1_scores, accuracies


def get_all_metrics(tp, fp, fn, tn):
    all_tp = sum(tp.values())
    all_fp = sum(fp.values())
    all_fn = sum(fn.values())
    all_tn = sum(tn.values())

    total_predictions = all_tp + all_fp + all_fn + all_tn

    if all_tp + all_fp > 0:
        global_precision = all_tp / (all_tp + all_fp)
    else:
        global_precision = 0.0

    if all_tp + all_fn > 0:
        global_recall = all_tp / (all_tp + all_fn)
    else:
        global_recall = 0.0

    if global_precision + global_recall > 0:
        global_f1 = 2 * (global_precision * global_recall) / (global_precision + global_recall)
    else:
        global_f1 = 0.0

    if total_predictions > 0:
        global_accuracy = (all_tp + all_tn) / total_predictions
    else:
        global_accuracy = 0.0

    return global_precision, global_recall, global_f1, global_accuracy

##############################################################################
## LAUNCHE THE TESTS
##############################################################################

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

