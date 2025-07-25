import './Classifier.css';

import { useState, useEffect } from 'react';

import { socket_classifier } from './socket';

function Classifier() {
    const [input, setInput] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    // ----------------------------------------------------------------------
    // Retrieve the Challenges, Themes, Scientific Themes and Mobility Types.
    // ----------------------------------------------------------------------

    // Challenges.
    const [challenges, setChallenges] = useState(null);
    // Themes.
    const [themes, setThemes] = useState(null);
    // Scientific themes.
    const [scientificThemes, setScientificThemes] = useState(null);
    // Mobility Types.
    const [mobilityTypes, setMobilityTypes] = useState(null);
    // Axes/ Leverage for actions.
    const [axes, setAxes] = useState(null);
    // Usages.
    const [usages, setUsages] = useState(null);

    const setVariablesToFalse = () => {
        setChallenges(false);
        setThemes(false);
        setScientificThemes(false);
        setMobilityTypes(false);
        setAxes(false);
        setUsages(false);
    };

    const setVariablesToData = (data) => {
        setChallenges(JSON.parse(data.challenges));
        setThemes(JSON.parse(data.themes));
        setScientificThemes(JSON.parse(data.scientificThemes));
        setMobilityTypes(JSON.parse(data.mobilityTypes));
        setAxes(JSON.parse(data.axes));
        setUsages(JSON.parse(data.usages));
    };

    // ----------------------------------------------------------------------

    useEffect(() => {
        socket_classifier.on("classification_error", (data) => {
            setError(data.error || "Unknown Error detected.");
            setLoading(false);
            //setVariablesToFalse();
        });

        socket_classifier.on("text_classification_results", (data) => {
            setLoading(false);
            setError(null);
            setVariablesToData(data);
        });

        socket_classifier.on("json_classification_results", (data) => {
            setLoading(false);
            setError(null);
            setVariablesToData(data);
        });

        return () => {
            socket_classifier.off("classification_error");
            socket_classifier.off("text_classification_results");
            socket_classifier.off("json_classification_results");
        };
    }, []);

    const classifyText = () => {
        if (!loading) {
            setVariablesToFalse();
            setLoading(true);
            setError(false);
            socket_classifier.emit("text_classification", input);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter")
            classifyText();
    };

    // ----------------------------------------------------------------------
    // JSON Upload.
    // ----------------------------------------------------------------------

    const handleJsonUpload = (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();

        reader.onload = (e) => {
            try {
                const jsonContent = JSON.parse(e.target.result);
                setLoading(true);
                setError(null);
                setVariablesToFalse();
                socket_classifier.emit("json_classification", JSON.stringify(jsonContent));
            } catch (err) {
                setError("JSON is invalid.");
            }
        };

        reader.readAsText(file);
    };

    // ----------------------------------------------------------------------

    return (
        <div className="Classifier">

            { error &&
                <div className="error-wrapper-classifier">
                    { error.message }
                </div>
            }

            <h1>Classification des publications</h1>
            {loading && <span className="loading">Searching...</span>}

            <div id="data">
                <form id="classificationForm" onSubmit={(e) => e.preventDefault()}>
                    <textarea
                        id="textInput"
                        rows="10"
                        cols="50"
                        placeholder="Entrez l'abstract ici (en anglais)..."
                        value={input}
                        onKeyDown={handleKeyDown}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={loading}
                    />
                    <button type="button" onClick={classifyText}>Valider</button>
                </form>
            </div>

            <div className="Upload">
                <label htmlFor="jsonUpload">
                    <strong>Importer une publication JSON :</strong>
                </label>
                <input
                    type="file"
                    id="jsonUpload"
                    accept=".json"
                    onChange={handleJsonUpload}
                    disabled={loading}
                    style={{ marginTop: '0.5rem', fontSize: '1rem' }}
                />
            </div>

            <div id="result">
                {challenges && challenges.length > 0 && (
                    <>
                        <h2>Enjeux associés :</h2>
                        <ul>
                            {challenges.map((challenge, index) => (
                                <li key={index}>{challenge}</li>
                            ))}
                        </ul>
                    </>
                )}

                {themes && themes.length > 0 && (
                    <>
                        <h2>Thèmes associés :</h2>
                        <ul>
                            {themes.map((theme, index) => (
                                <li key={index}>{theme}</li>
                            ))}
                        </ul>
                    </>
                )}

                {scientificThemes && scientificThemes.length > 0 && (
                    <>
                        <h2>Thèmes scentifiques associés :</h2>
                        <ul>
                            {scientificThemes.map((theme, index) => (
                                <li key={index}>{theme}</li>
                            ))}
                        </ul>
                    </>
                )}

                {mobilityTypes && mobilityTypes.length > 0 && (
                    <>
                        <h2>Types de mobilité associés :</h2>
                        <ul>
                            {mobilityTypes.map((type, index) => (
                                <li key={index}>{type}</li>
                            ))}
                        </ul>
                    </>
                )}

                {axes && axes.length > 0 && (
                    <>
                        <h2>Axes/ leviers d'actions associés :</h2>
                        <ul>
                            {axes.map((axe, index) => (
                                <li key={index}>{axe}</li>
                            ))}
                        </ul>
                    </>
                )}

                {usages && usages.length > 0 && (
                    <>
                        <h2>Usages associés :</h2>
                        <ul>
                            {usages.map((usage, index) => (
                                <li key={index}>{usage}</li>
                            ))}
                        </ul>
                    </>
                )}

            </div>
        </div>
    );
}

export default Classifier;

