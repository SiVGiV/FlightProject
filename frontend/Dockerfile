# base image
FROM node:18.17.0

# set work directory
ENV ProjectDir=/app
RUN mkdir -p $ProjectDir
WORKDIR $ProjectDir
COPY . $ProjectDir

RUN npm ci --omit=optional

# PRODUCTION ---------------------------------
# RUN npm run build

# set environment variables
ENV NODE_ENV=development

EXPOSE 3000

CMD [ "npm", "start" ]

# PRODUCTION ---------------------------------
# CMD [ "npx", "serve", "build" ]