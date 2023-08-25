CONTAINER_FIRST_STARTUP="CONTAINER_FIRST_STARTUP"
if [ ! -e /$CONTAINER_FIRST_STARTUP ]; then
    touch /$CONTAINER_FIRST_STARTUP
    # This will only run on the 1st run
    mkdir -p ./exposed/logs
    mkdir -p ./exposed/generated_data
    touch ./exposed/logs/app.log
    python manage.py migrate
    python manage.py loaddata countries
    python manage.py collectstatic
    python manage.py createsuperuser --noinput
    python setup_db.py make_superuser_admin
fi
# This will run every time
gunicorn FlightProject.wsgi:application --bind 0.0.0.0:8000