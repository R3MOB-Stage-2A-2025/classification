import './App.css';

import { useState } from 'react';

import Retriever from './Retriever';
import Classifier from './Classifier';

function App()
{
    const [classify, setClassify] = useState(false);
    const [retrieve, setRetrieve] = useState(false);

    const retrieveText = () => {
        setRetrieve(true);
        setClassify(false);
    };

    const classifyText = () => {
        setRetrieve(false);
        setClassify(true);
    };

    if (retrieve)
        return <Retriever />;
    else if (classify)
        return <Classifier />;

    return (
        <div className="App">
            <button className="MainButton" type="button"
                onClick={retrieveText}>Retriever</button>
            <button className="MainButton"
                onClick={classifyText}>Classifier</button>
        </div>
    );
}

export default App;

