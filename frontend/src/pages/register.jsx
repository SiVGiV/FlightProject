import React from "react";
import { Form } from "react-bootstrap";
import { Typeahead } from "react-bootstrap-typeahead";
import { redirect } from "react-router-dom";

export default function Register(userType) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [password2, setPassword2] = useState("");
    const [email, setEmail] = useState("");
    const [fields, setFields] = useState({});

    const [formError, setFormError] = useState("");

    const handleSubmit = () => {
        if (password !== password2){
            setFormError("Passwords do not match!")
            return
        }
        switch (userType){
            case "customer":
                API.customers.post({username, password, password2, email, ...fields})
                    .then(response => {
                        redirect("/")
                    })
                    .catch(error => {
                        setFormError(error.response.data)
                    })
                break;
            case "airline":
                API.airlines.post({username, password, password2, email, ...fields})
                .then(response => {
                    redirect("/")
                })
                .catch(error => {
                    setFormError(error.response.data)
                })
                break;
            case "admin":
                API.admins.post({username, password, password2, email, ...fields})
                .then(response => {
                    redirect("/")
                })
                .catch(error => {
                    setFormError(error.response.data)
                })
                break;
            default:
                return null;
        }
    }

    return (
        <Form>
            <div id="formError">{formError}</div>
            <Form.Group controlId="formUsername">
                <Form.Label>Username</Form.Label>
                <Form.Control type="text" placeholder="Enter username" pattern="^[a-zA-Z0-9]+$" onChange={(e) => setUsername(e.target.value)} />
            </Form.Group>
            <Form.Group controlId="formPassword">
                <Form.Label>Password</Form.Label>
                <Form.Control type="password" placeholder="Password" pattern="(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$" onChange={(e) => setPassword(e.target.value)} />'
            </Form.Group>
            <Form.Group controlId="formPassword2">
                <Form.Label>Confirm Password</Form.Label>
                <Form.Control type="password" placeholder="Confirm Password" pattern="(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$" onChange={(e) => setPassword2(e.target.value)} />
            </Form.Group>
            <Form.Group controlId="formEmail">
                <Form.Label>Email</Form.Label>
                <Form.Control type="email" placeholder="Enter email" pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$" onChange={(e) => setEmail(e.target.value)} />
            </Form.Group>
            <RegistrationRouter userType={ userType } fields={ fields } setFields={ setFields } setFormError={ setFormError }/>
            <Button variant="primary" type="submit" onClick={ handleSubmit }/>
        </Form>

    );
}


function RegistrationRouter({userType, fields, setFields, setFormError}){
    switch(userType){
        case "customer":
            return customerFields({fields, setFields, setFormError});
        case "airline":
            return airlineFields({fields, setFields, setFormError});
        case "admin":
            return adminFields({fields, setFields, setFormError});
        default:
            return <></>;
    }
}

function customerFields({fields, setFields, setFormError}){
    return(
        <div id="additionalFields">
            <Form.Group controlId="formFirstName">
                <Form.Label>First Name</Form.Label>
                <Form.Control type="text" placeholder="Enter first name" onChange={(e) => setFields({...fields ,"first_name": e.target.value})} />
            </Form.Group>
            <Form.Group controlId="formLastName">
                <Form.Label>Last Name</Form.Label>
                <Form.Control type="text" placeholder="Enter last name" onChange={(e) => setLastName({...fields ,"last_name": e.target.value})} />
            </Form.Group>
            <Form.Group controlId="formAddress">
                <Form.Label>Address</Form.Label>
                <Form.Control type="text" placeholder="Enter address" onChange={(e) => setAddress({...fields ,"address": e.target.value})} />
            </Form.Group>
            <Form.Group controlId="formPhone">
                <Form.Label>Phone</Form.Label>
                <Form.Control type="text" placeholder="Enter phone" onChange={(e) => setPhone({...fields ,"phone_number": e.target.value})} />
            </Form.Group>
        </div>
    );
}

function airlineFields({fields, setFields, setFormError}){
    const [countries, setCountries] = useState([]);
    const [selectedAirlineCountry, setSelectedAirlineCountry] = useState([]);
    const [loadingCountries, setLoadingCountries] = useState(true);

    useEffect(()=>{ // Get countries
        setLoadingCountries(true)
        API.countries.get({limit: 200, page: 1})
        .then(response => {
            setCountries(response.data.data)
        })
        .catch(error => {
            console.log(error.response.data.data)
            setFormError("Error loading country list...")
        })
        .finally(() => {
            setLoadingCountries(false)
        })
    }, []);

    useEffect(()=>{
        setFields({...fields, "country": selectedAirlineCountry[0].id})
    }, [selectedAirlineCountry]);

    return (
        <div id="additionalFields">
            <Form.Group controlId="formAirlineName">
                <Form.Label>Airline Name</Form.Label>
                <Form.Control type="text" placeholder="Enter airline name" onChange={(e) => setFields({...fields, "airlineName": e.target.value})} />
            </Form.Group>
            <Form.Group controlId="formAirlineCountry">
                <Form.Label>Airline Country</Form.Label>
                <Typeahead
                    id="basic-typeahead-single"
                    labelKey="name"
                    onChange={ setSelectedAirlineCountry }
                    options={countries}
                    placeholder={ loadingCountries ? "Loading..." : "Select a country"}
                    selected={ selectedAirlineCountry }
                    disabled={ loadingCountries }
                />
            </Form.Group>
        </div>
    );
}

function adminFields({fields, setFields, setFormError}){
    return(
        <div id="additionalFields">
            <Form.Group controlId="formFirstName">
                <Form.Label>First Name</Form.Label>
                <Form.Control type="text" placeholder="Enter first name" onChange={(e) => setFields({...fields ,"first_name": e.target.value})} />
            </Form.Group>
            <Form.Group controlId="formLastName">
                <Form.Label>Last Name</Form.Label>
                <Form.Control type="text" placeholder="Enter last name" onChange={(e) => setLastName({...fields ,"last_name": e.target.value})} />
            </Form.Group>
        </div>
    );
}