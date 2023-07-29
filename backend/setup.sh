CONTAINER_FIRST_STARTUP="CONTAINER_FIRST_STARTUP"
if [ ! -e /$CONTAINER_FIRST_STARTUP ]; then
    touch /$CONTAINER_FIRST_STARTUP
    # This will only run on the 1st run
    python setup_db.py
    python manage.py migrate
    python manage.py loaddata countries
    python manage.py collectstatic
    python manage.py createsuperuser --noinput
    python setup_db.py make_superuser_admin $DJANGO_SUPERUSER_USERNAME
fi
# This will run every time
gunicorn FlightProject.wsgi:application --bind 0.0.0.0:8000 --certfile=server.crt --keyfile=server.key