import React, { useState, useEffect, useContext } from "react";
import { Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { LoginContext } from "../../contexts/auth_contexts";
import { APIContext } from "../../contexts/api_context";


export default function Welcome() {
    const API = useContext(APIContext);
    const navigate = useNavigate();

    const loginValue = useContext(LoginContext);
    return (
        <div className="welcomeBar">
            {
                loginValue.logged_in ? (`Welcome, ${loginValue.entity_name}! `) : (`Welcome! Please login to continue.`)
            }
            &nbsp;&nbsp;
            <Button onClick={loginValue.logged_in ? () => logout(API, navigate) : () => login(navigate)} className="navbar-button">
                {loginValue.logged_in ? "Logout" : "Login"}
            </Button>
        </div>
    );
}


function login(navigate) {
    navigate("/login")
}

function logout(API, navigate) {
    API.auth.logout()
        .then(response => {
            navigate("/login")
        }).catch(error => {
            console.log(error)
        })
}