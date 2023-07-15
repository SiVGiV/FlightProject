# base image
FROM python:3.11

# set work directory
ENV ProjectDir=/home/app/webapp
RUN mkdir -p $ProjectDir
WORKDIR $ProjectDir

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY . $ProjectDir
RUN pip install -r requirements.txt
EXPOSE 8000

CMD [ "sh", "setup.sh" ]