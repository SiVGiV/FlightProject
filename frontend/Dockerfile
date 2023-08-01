# base image
FROM node:18.17.0

# set work directory
ENV ProjectDir=/app
RUN mkdir -p $ProjectDir
WORKDIR $ProjectDir
COPY . $ProjectDir

RUN npm ci
RUN npm run build

# set environment variables
ENV NODE_ENV production

EXPOSE 3000

CMD [ "npx", "serve", "build" ]