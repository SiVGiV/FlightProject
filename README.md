# Flight Manager Project - Backend

This image contains the backend of my project. 

## Getting Started

These instructions will cover usage information and for the docker container 

## Prerequisities

#### Docker
In order to run this container you'll need docker installed.

* [Windows](https://docs.docker.com/windows/started)
* [OS X](https://docs.docker.com/mac/started/)
* [Linux](https://docs.docker.com/linux/started/)

#### Database requirements

This image requires a MYSQL container running in the same network on the port 3306, and some environment variables from that database.

## Usage

It is recommended to run this image as part of [this docker-compose](https://github.com/SiVGiV/FlightProject/blob/b07030804af6e818783ecc9a5074f65708b4f17b/docker-compose.yml), but it is also possible (although not recommended) to run it without it.

#### [API Documentation](http://project-docs.sivgiv.com/) (Might be unavailable at some point)

#### Required environment variables

##### Database Settings
* `MYSQL_HOST` - The MySQL network address
* `MYSQL_NAME` - The MySQL scheme name to be created and used
* `MYSQL_ROOT_PASSWORD` - Password for the MySQL 'root' user

##### Django superuser settings
* `DJANGO_SUPERUSER_USERNAME` - The Backend's superuser username
* `DJANGO_SUPERUSER_PASSWORD` -  The Backend's superuser password
* `DJANGO_SUPERUSER_EMAIL` -  The Backend's superuser email

#### Volumes
It is recommended to create a volume that binds to `/app/exposed/` for access to the logs and any generated data, but it is not necessary.

#### Useful File Locations

* `/app/` - The project's main directory

* `/app/exposed/logs` - App logs
  
* `/app/generate_data.py` - A Python CLI script for generating random sample data.

* `/app/exposed/generated_data` - Generated data from `generate_data.py` (If executed)

## Built With

* Python 3.11
* Django 4.2.1 - As the foundational framework
* Django REST Framework 3.14.0 - For API functionality
* Gunicorn 20.1.0 - For serving the app in production
* Whitenoise 6.5.0 - For serving static files
* randomuser - For the `generate_data.py` script
* click - For the CLI functionality in the `generate_data.py` script


## Author

* **Sivan Givati** - [GitHub](https://github.com/sivgiv), [Website](https://sivgiv.com/)