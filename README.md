# Flight Manager Project
**John Bryce - Project #2**

## Backend

### Framework choice
I chose to use Django for the backend, as it is a framework that answers some of my needs:
- Authentication and authorization
- Simple API creation (with the help of Django REST framework)
- Built in authentication handling
- Ready made ORM for database access
- Fixture imports for easy database seeding
- Easy configuration and serving of static files (Using gunicorn and whitenoise)

### Choices

#### Authentication
I initially chose to use BasicAuth for API access, as it is as its name suggests - basic. However - I decided that session authentication would be better suited for my needs. Therefore, I implemented a simple login and logout views. In addition to those views, I wanted to create a way for the front end to find out what type of user is viewing the page, so I can display the right menus and features. For this I created the 'whoami' endpoint, which returns some very basic information about the user - so that I know to display everything properly.

#### Authorization
Despite the requirement being a user_role table in the database, I chose to use Django's built in group system instead. This is since the functionality would've been the same, and Django's group system is already integrated with the authentication system and has some ready functions to support the group functionality. 

#### Credit Card Number

##### Omition
For my customer table, I chose to omit the credit_card_number field, as it is a sensitive field that should not be stored in plain text. Since the addition of a credit card number field would've been a simple string field, I decided it is an arbitrary field that wouldn't add much to the project.

##### What I would've done instead
If I was required to add support for a payment system, I would've used an external service that specializes in payment processing, such as Stripe or PayPal. This would've allowed me to store a secure token for the customer's payment method, and use it to charge the customer when needed. 

#### Get All Flights & Get All Airlines
A choice I made in the implementation of these functions was to use the filtration methods (Flights by parameters & Airline by name) to implement these functions. This allowed me to reuse code in its entirety, and not have to write any additional code for these functions. 

#### Testing data and fixtures
Since Django has a built in method for seeding the database, I chose to use it for the Countries table, since it's static information that wouldn't change very often.
However, since I wanted the testing data to be meaningful data that can be used to demonstrate a production environment, I chose to use a Python script to generate the data, and since I built an API for the project, I used the API to seed the database with the generated data.

### Built With

* [Python](https://www.python.org/) 3.11
* [Django](https://pypi.org/project/Django/) 4.2.1 - As the foundational framework
* [Django REST Framework](https://pypi.org/project/djangorestframework/) 3.14.0 - For API functionality
* [Gunicorn](https://pypi.org/project/gunicorn/) 20.1.0 - For serving the app in production
* [Whitenoise](https://pypi.org/project/whitenoise/) 6.5.0 - For serving static files
* [randomuser](https://pypi.org/project/randomuser/) - For the `generate_data.py` script
* [click](https://pypi.org/project/click/) - For the CLI functionality in the `generate_data.py` script

## Author

* **Sivan Givati** - [GitHub](https://github.com/sivgiv), [Website](https://sivgiv.com/)
