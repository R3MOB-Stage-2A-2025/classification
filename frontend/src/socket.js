import io from 'socket.io-client';

// require('dotenv').config();

// <Retriever>
//const socket_retriever = io.connect('wss://localhost:5022', {
    //path: "/socket.io/",
    //transports: [ "websocket" ],
//});

const socket_retriever = io.connect('ws://localhost:5001');
// </Retriever>

// <Classifier>
//const socket_classifier = io.connect('wss://localhost:5023', {
    //path: "/socket.io/",
    //transports: [ "websocket" ],
//});

const socket_classifier = io.connect('ws://localhost:5011');
// </Classifier>

export { socket_retriever, socket_classifier };

