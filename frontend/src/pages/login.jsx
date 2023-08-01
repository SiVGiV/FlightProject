import React, { useState } from 'react';
import { Button, Form } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useContext } from 'react';
import { LoginContext } from '../contexts/auth_contexts';
import API from '../api';

export default function LoginPage(){
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [validated, setValidated] = useState(false);
    const [formError, setFormError] = useState("");

    const [login, setLogin] = useContext(LoginContext);

    const navigate = useNavigate();

    const handleSubmit = (event) => {
        event.preventDefault();
        API.auth.login({username, password})
        .then(response => {
            console.log(response)
            setValidated(true);
            API.auth.whoami()
            .then(response => {
                setLogin(response.data.data)
            })
            .catch(error => {
                console.log(error)
            })
            .finally(() => {
                navigate("/")
            })
        })
        .catch(error => {
            console.log(error)
            setFormError(error.response.data)
        })
    }
    
    return(
        <div className="main-container">
            <Form onSubmit={ handleSubmit } validated={validated} noValidate>
                <div id="formError">{formError.toString()}</div>
                <Form.Group controlId="formUsername">
                    <Form.Label>Username</Form.Label>
                    <Form.Control type="username" placeholder="Enter username" onChange={(e) => setUsername(e.target.value)} required />
                    <Form.Control.Feedback type="invalid">
                        Please enter your username.
                    </Form.Control.Feedback>
                </Form.Group>

                <Form.Group controlId="formPassword">
                    <Form.Label>Password</Form.Label>
                    <Form.Control type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} required />
                    <Form.Control.Feedback type="invalid">
                        Please enter your password.
                    </Form.Control.Feedback>
                </Form.Group>
                <Button variant="primary" type="submit">Sign in</Button>
                <p>Don't have a user yet? <a href='/register'>Register.</a></p>
            </Form>
        </div>
    )
}