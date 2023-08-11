export default function HomePage() {
    return (
        <div>
            <h1 id="flight-manager-project">Flight Manager Project</h1>
            <p>
                <strong>John Bryce - Project #2</strong>
            </p>
            <h2 id="backend">Backend</h2>
            <h3 id="framework-choice">Framework choice</h3>
            <p>
                I chose to use Django for the backend, as it is a framework that
                answers some of my needs:
            </p>
            <ul>
                <li>Authentication and authorization</li>
                <li>
                    Simple API creation (with the help of Django REST framework)
                </li>
                <li>BasicAuth for API access</li>
                <li>Ready made ORM for database access</li>
                <li>Fixture imports for easy database seeding</li>
                <li>
                    Easy configuration and serving of static files (Using
                    gunicorn and whitenoise)
                </li>
            </ul>
            <h3 id="choices">Choices</h3>
            <h4 id="authentication">Authentication</h4>
            <p>
                I chose to use BasicAuth for API access, as it is a simple and
                easy to use authentication method, is supported by djagno rest
                framework out of the box, and does not require users to generate
                tokens.
            </p>
            <h4 id="authorization">Authorization</h4>
            <p>
                Despite the requirement being a user_role table in the database,
                I chose to pass on it and use Django&#39;s built in group
                system. This is since the functionality would&#39;ve been the
                same, and Django&#39;s group system is already integrated with
                the authentication system.
            </p>
            <h4 id="credit-card-number">Credit Card Number</h4>
            <h5 id="omition">Omition</h5>
            <p>
                For my customer table, I chose to omit the credit_card_number
                field, as it is a sensitive field that should not be stored in
                plain text. Since the addition of a credit card number field
                would&#39;ve been a simple string field, I decided it is an
                arbitrary field that wouldn&#39;t add much to the project.
            </p>
            <h5 id="what-i-would-ve-done-instead">
                What I would&#39;ve done instead
            </h5>
            <p>
                If I was required to add support for a payment system, I
                would&#39;ve used an external service that specializes in
                payment processing, such as Stripe or PayPal. This would&#39;ve
                allowed me to store a secure token for the customer&#39;s
                payment method, and use it to charge the customer when needed.{" "}
            </p>
            <h4 id="get-all-flights-get-all-airlines">
                Get All Flights &amp; Get All Airlines
            </h4>
            <p>
                A clever choice I made in the implementation of these functions
                was to use the filtration methods (Flights by parameters &amp;
                Airline by name) to implement these functions. This allowed me
                to reuse code in its entirety, and not have to write any
                additional code for these functions.{" "}
            </p>
            <h4 id="testing-data-and-fixtures">Testing data and fixtures</h4>
            <p>
                Since Django has a built in method for seeding the database, I
                chose to use it for the Countries table, since it&#39;s static
                information that wouldn&#39;t change very often. However, since
                I wanted the testing data to be meaningful data that can be used
                to demonstrate a production environmentm I chose to use a Python
                script to generate the data, and since I built an API for the
                project, I chose to use the API to seed the database with the
                generated data.
            </p>
            <h3 id="built-with">Built With</h3>
            <ul>
                <li>
                    <a href="https://www.python.org/">Python</a> 3.11
                </li>
                <li>
                    <a href="https://pypi.org/project/Django/">Django</a> 4.2.1
                    - As the foundational framework
                </li>
                <li>
                    <a href="https://pypi.org/project/djangorestframework/">
                        Django REST Framework
                    </a>{" "}
                    3.14.0 - For API functionality
                </li>
                <li>
                    <a href="https://pypi.org/project/gunicorn/">Gunicorn</a>{" "}
                    20.1.0 - For serving the app in production
                </li>
                <li>
                    <a href="https://pypi.org/project/whitenoise/">
                        Whitenoise
                    </a>{" "}
                    6.5.0 - For serving static files
                </li>
                <li>
                    <a href="https://pypi.org/project/randomuser/">
                        randomuser
                    </a>{" "}
                    - For the <code>generate_data.py</code> script
                </li>
                <li>
                    <a href="https://pypi.org/project/click/">click</a> - For
                    the CLI functionality in the <code>generate_data.py</code>{" "}
                    script
                </li>
            </ul>
            <h2 id="frontend">Frontend</h2>
            <h3 id="choices">Choices</h3>
            <h4 id="role-based-access">Role Based Access</h4>
            <p>
                When deciding how to display pages and components suited for
                some roles, I had to consider the security limitations presented
                by React. Since React is a client side framework, it is not
                possible to hide components from the user, as the user can
                simply inspect the page and see the code. Instead of keeping the
                user&#39;s role in the state, I chose to ask the server for the
                user&#39;s role on every role based render, to make sure the
                user can&#39;t change their role by changing the state. This
                method reminds me of the TCP handshake, where the client and
                server exchange information before starting the connection.
                While it makes my code more redundant, I feel it&#39;s the right
                method to use in this case.
            </p>
            <h2 id="author">Author</h2>
            <ul>
                <li>
                    <strong>Sivan Givati</strong> -{" "}
                    <a href="https://github.com/sivgiv">GitHub</a>,{" "}
                    <a href="https://sivgiv.com/">Website</a>
                </li>
            </ul>
        </div>
    );
}
