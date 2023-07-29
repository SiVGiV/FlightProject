import React, { useState, useEffect } from "react";
import { Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import API from "../../api";


export default function Welcome() {
    const [loggedIn, setLoggedIn] = useState({});
    const [loadingLogin, setLoadingLogin] = useState(true);
    const [loginError, setLoginError] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        API.auth.csrf().then(response => {console.log(response.data)}).catch(error => {console.log(error)});
        API.auth.whoami()
        .then(response => {setLoggedIn(response.data); console.log(response.data);})
        .catch(error => {setLoginError(true); console.log(error);})
        .finally(() => setLoadingLogin(false))
    }, []);
    

    return (
        loadingLogin ? <></> :
        loginError ? <></> :
        <div className="welcomeBar">
            {
                loggedIn.logged_in ? (`Welcome, ${loggedIn.username}! `) : (`Welcome! Please login to continue.`)
            }
            &nbsp;&nbsp;
            <Button onClick={ loggedIn.logged_in ? () => logout(navigate) : () => login(navigate) } className="navbar-button">
                {loggedIn.logged_in ? "Logout" : "Login"}
            </Button>
        </div>
    );
}


function login(navigate){
    navigate("/login")
}

function logout(navigate){
    API.auth.logout()
    .then(response => {
        navigate("/")
    })
    .catch(error => {
        console.log(error)
    })
}