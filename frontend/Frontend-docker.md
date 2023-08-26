# Flight Manager Project - Frontend
This image contains the frontend of my project. 

## Getting Started
These instructions will cover usage information and for the docker container 

## Prerequisities
#### Docker
In order to run this container you'll need docker installed.

* [Windows](https://docs.docker.com/windows/started)
* [OS X](https://docs.docker.com/mac/started/)
* [Linux](https://docs.docker.com/linux/started/)

#### Backend requirements

This image requires [this backend image](https://hub.docker.com/repository/docker/sivgiv/flightproject-backend/general) running on the same network.
## Usage

It is recommended to run this image as part of [this docker-compose](https://github.com/SiVGiV/FlightProject/blob/master/docker-compose.yml), but it is also possible (although not recommended) to run it without it.

#### Required environment variables
* `BACKEND_URL` - The base URL for the backend - `/api/` is appended within the image.

## Built With
* React
* Axios
* React-bootstrap
* React-bootstrap-typeahead
* React-router-dom
* JS-Cookie

## Author
* **Sivan Givati** - [GitHub](https://github.com/sivgiv), [Website](https://sivgiv.com/)