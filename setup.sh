python setup_db.py create_schema
python manage.py migrate
python manage.py loaddata FlightsApi/fixtures/countries.json