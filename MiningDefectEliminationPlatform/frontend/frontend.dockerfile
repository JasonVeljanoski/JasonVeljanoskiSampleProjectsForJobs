FROM node:16

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

#.dockerignore will exclude folders
COPY . .

ARG API_URL
ARG REDIRECT_URL
ARG OAUTH_CLIENT_ID
ARG OAUTH_URL
ARG ENV
# ENV NODE_OPTIONS=--openssl-legacy-provider

RUN npm run build

EXPOSE 3000

ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000
