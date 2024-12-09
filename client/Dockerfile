FROM node:21-alpine

WORKDIR /client

COPY package.json package-lock.json ./
COPY webpack.config.js ./
COPY css ./css
COPY dist/register_jquery.js ./dist/register_jquery.js
COPY img ./img
COPY js ./js
COPY templates ./templates

RUN npm install
RUN npm run build

CMD [ "npm", "run", "watch" ]
