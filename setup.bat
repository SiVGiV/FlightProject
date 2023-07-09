python setup_db.py
python manage.py migrate
python manage.py loaddata countries
:: Requires the following as environment variables:
:: DJANGO_SUPERUSER_USERNAME
:: DJANGO_SUPERUSER_PASSWORD
:: DJANGO_SUPERUSER_EMAIL
set DJANGO_SUPERUSER_USERNAME=admin
set DJANGO_SUPERUSER_PASSWORD=admin
set DJANGO_SUPERUSER_EMAIL=a@a.com
python manage.py createsuperuser --noinput
python setup_db.py make_superuser_admin %DJANGO_SUPERUSER_USERNAME%