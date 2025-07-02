import io from 'socket.io-client';

// require('dotenv').config();
export const socket = io.connect('http://localhost:5001');

