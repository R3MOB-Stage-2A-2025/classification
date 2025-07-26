FROM node:alpine

WORKDIR /app

COPY frontend/package*.json .

RUN npm install

COPY frontend/ .

EXPOSE 5180

CMD ["npm", "run", "dev"]

