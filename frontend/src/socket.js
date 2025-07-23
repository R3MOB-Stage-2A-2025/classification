import io from 'socket.io-client';

// require('dotenv').config();

// <Retriever>
const socket_retriever = io.connect('http://localhost:5001');
// </Retriever>

// <Classifier>
const socket_classifier = io.connect('http://localhost:5011');
// </Classifier>

export { socket_retriever, socket_classifier };

