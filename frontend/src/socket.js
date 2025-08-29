import io from 'socket.io-client';

// require('dotenv').config();

// <Retriever>
const socket_retriever = io.connect('wss://localhost:5022', {
    path: "/socket.io/",
    transports: [ "websocket" ],
});
// </Retriever>

// <Classifier>
const socket_classifier = io.connect('wss://localhost:5023', {
    path: "/socket.io/",
    transports: [ "websocket" ],
});
// </Classifier>

export { socket_retriever, socket_classifier };

