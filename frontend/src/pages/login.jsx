import React, { useState, useContext } from 'react';
import { Button, Form } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { APIContext } from '../contexts/api_contexts';
import { RefreshLoginContext } from '../contexts/auth_contexts';

export default function LoginPage(){
    const API = useContext(APIContext);
    const RefreshLogin = useContext(RefreshLoginContext);
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [validated, setValidated] = useState(false);
    const [formError, setFormError] = useState("");

    const navigate = useNavigate();

    const handleSubmit = (event) => {
        event.preventDefault();
        API.auth.login({username, password})
        .then(response => {
            RefreshLogin();
            setValidated(true);
            navigate("/")
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