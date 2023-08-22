# base image
FROM node:18.17.0

# set work directory
ENV ProjectDir=/app
RUN mkdir -p $ProjectDir
WORKDIR $ProjectDir
COPY . $ProjectDir

RUN npm ci --omit=optional

# PRODUCTION ---------------------------------
RUN npm run build
RUN npm install -g serve

# set environment variables
ENV NODE_ENV=production

EXPOSE 3000

# CMD [ "npm", "start" ]

# PRODUCTION ---------------------------------
CMD [ "serve", "-s", "build", "-l", "tcp://0.0.0.0:3000" ]