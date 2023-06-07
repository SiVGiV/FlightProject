python setup_db.py create_schema
python manage.py migrate
python manage.py loaddata static/setupdata/countries.json
python manage.py loaddata static/setupdata/userroles.json