// Fonction pour classifier le texte
async function classifyText() {

    const textInput = document.getElementById('textInput').value;
    const resultDiv = document.getElementById('result');

    // Vérifiez si le champ de texte n'est pas vide
    if (textInput.trim() === "") {
        resultDiv.innerHTML = "<p>Veuillez entrer un texte pour la classification.</p>";
        return;
    }

    // Envoyer le texte au serveur pour la classification
    try {
        const response = await fetch('/classify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: textInput })
        });

        if (!response.ok) {
            throw new Error('Erreur lors de la classification du texte.');
        }

        const result = await response.json();

        // Afficher les résultats
        if (result.themes.length > 0) {
            themesList = "<h2>Thèmes scentifiques associés :</h2><ul>";
            for (let index = 0; index < result.themes.length; index++)
                themesList += `<li>${result.themes[index]}</li>`;
            themesList += "</ul>";

            resultDiv.innerHTML = themesList;
        } else {
            resultDiv.innerHTML = "<p>Aucun thème associé trouvé.</p>";
        }
    } catch (error) {
        resultDiv.innerHTML = `<p>${error.message}</p>`;
    }
}

