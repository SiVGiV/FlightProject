import React, { useState, useEffect } from "react";
import { Form, Button } from "react-bootstrap";
import { Typeahead } from "react-bootstrap-typeahead";
import { redirect, useParams } from "react-router-dom";
import API from "../api";


export default function Register() {
    const userType = useParams()?.userType;

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [password2, setPassword2] = useState("");
    const [email, setEmail] = useState("");
    const [fields, setFields] = useState({});
    const [validated, setValidated] = useState(false);

    const [formError, setFormError] = useState("");

    const handleSubmit = (event) => {
        const form = event.currentTarget;
        if (form.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
        }
        setValidated(true);
        if (password !== password2){
            setFormError("Passwords do not match!")
        }
        switch (userType){
            case "airline":
                API.airlines.post({username, password, password2, email, ...fields})
                .then(response => {
                    setValidated(true);
                    redirect("/")
                })
                .catch(error => {
                    console.log(error)
                    setFormError(error)
                })
                break;
            case "admin":
                API.admins.post({username, password, password2, email, ...fields})
                .then(response => {
                    setValidated(true);
                    redirect("/")
                })
                .catch(error => {
                    console.log(error)
                    setFormError(error)
                })
                break;
            default:
                API.customers.post({username, password, password2, email, ...fields})
                    .then(response => {
                        setValidated(true);
                        redirect("/")
                    })
                    .catch(error => {
                        console.log(error)
                        setFormError(error)
                    })
                break;
        }
    }

    return (
        <Form noValidate validated={ validated } onSubmit={ handleSubmit }>
            <div id="formError">{formError}</div>
            <Form.Group controlId="formUsername">
                <Form.Label>Username</Form.Label>
                <Form.Control type="text" placeholder="Enter username" pattern="^[a-zA-Z0-9]+$" onChange={(e) => setUsername(e.target.value)} required />
                <Form.Control.Feedback type="invalid">Username must be alphanumeric</Form.Control.Feedback>
            </Form.Group>
            <Form.Group controlId="formPassword">
                <Form.Label>Password</Form.Label>
                <Form.Control type="password" placeholder="Password" pattern="(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$" onChange={(e) => setPassword(e.target.value)} required/>
                <Form.Control.Feedback type="invalid">Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number or special character</Form.Control.Feedback>
            </Form.Group>
            <Form.Group controlId="formPassword2">
                <Form.Label>Confirm Password</Form.Label>
                <Form.Control type="password" placeholder="Confirm Password" pattern="(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$" onChange={(e) => setPassword2(e.target.value)} required />
            </Form.Group>
            <Form.Group controlId="formEmail">
                <Form.Label>Email</Form.Label>
                <Form.Control type="email" placeholder="Enter email" pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$" onChange={(e) => setEmail(e.target.value)} required />
                <Form.Control.Feedback type="invalid">Please enter a valid email address</Form.Control.Feedback>
            </Form.Group>
            <RegistrationRouter userType={ userType } fields={ fields } setFields={ setFields } setFormError={ setFormError }/>
            <br/>
            <Button variant="primary" type="submit" onClick={ handleSubmit }>Register</Button>
        </Form>
    );
}


function RegistrationRouter({userType, fields, setFields, setFormError}){
    switch(userType){
        case "airline":
            return AirlineFields({fields, setFields, setFormError});
        case "admin":
            return AdminFields({fields, setFields, setFormError});
        default:
            return CustomerFields({fields, setFields, setFormError});
    }
}

function CustomerFields({fields, setFields, setFormError}){
    return(
        <div id="additionalFields">
            <Form.Group controlId="formFirstName">
                <Form.Label>First Name</Form.Label>
                <Form.Control type="text" placeholder="Enter first name" onChange={(e) => setFields({...fields ,"first_name": e.target.value})} />
            </Form.Group>
            <Form.Group controlId="formLastName">
                <Form.Label>Last Name</Form.Label>
                <Form.Control type="text" placeholder="Enter last name" onChange={(e) => setFields({...fields ,"last_name": e.target.value})} />
            </Form.Group>
            <Form.Group controlId="formAddress">
                <Form.Label>Address</Form.Label>
                <Form.Control type="text" placeholder="Enter address" onChange={(e) => setFields({...fields ,"address": e.target.value})} />
            </Form.Group>
            <Form.Group controlId="formPhone">
                <Form.Label>Phone</Form.Label>
                <Form.Control type="text" placeholder="Enter phone" onChange={(e) => setFields({...fields ,"phone_number": e.target.value})} />
            </Form.Group>
        </div>
    );
}

function AirlineFields({fields, setFields, setFormError}){
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
        setFields({...fields, "country": selectedAirlineCountry[0]?.id})
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

function AdminFields({fields, setFields, setFormError}){
    return(
        <div id="additionalFields">
            <Form.Group controlId="formFirstName">
                <Form.Label>First Name</Form.Label>
                <Form.Control type="text" placeholder="Enter first name" onChange={(e) => setFields({...fields ,"first_name": e.target.value})} />
            </Form.Group>
            <Form.Group controlId="formLastName">
                <Form.Label>Last Name</Form.Label>
                <Form.Control type="text" placeholder="Enter last name" onChange={(e) => setFields({...fields ,"last_name": e.target.value})} />
            </Form.Group>
        </div>
    );
}