import React, { useState, useEffect, useContext } from "react";
import { Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import API from "../../api";
import { LoginContext } from "../../contexts/auth_contexts";


export default function Welcome() {
    const [loadingLogin, setLoadingLogin] = useState(true);
    const [loginError, setLoginError] = useState(false);
    const navigate = useNavigate();

    const [loginValue, setLogin] = useContext(LoginContext);

    useEffect(() => {
        API.auth.whoami()
            .then(response => { setLogin(response.data); console.log(response.data); })
            .catch(error => { setLoginError(true); console.log(error); })
            .finally(() => setLoadingLogin(false))
    }, []);


    return (
        loadingLogin ? <></> :
            loginError ? <></> :
                <div className="welcomeBar">
                    {
                        loginValue.logged_in ? (`Welcome, ${loginValue.username}! `) : (`Welcome! Please login to continue.`)
                    }
                    &nbsp;&nbsp;
                    <Button onClick={loginValue.logged_in ? () => logout(navigate, setLogin) : () => login(navigate)} className="navbar-button">
                        {loginValue.logged_in ? "Logout" : "Login"}
                    </Button>
                </div>
    );
}


function login(navigate) {
    navigate("/login")
}

function logout(navigate, setLogin) {
    API.auth.logout()
        .then(response => {
            API.auth.whoami()
            .then(identity => {
                setLogin(identity.data)
            })
            .catch(error => {
                console.log(error)
            })
            navigate("/login")
        }
        )
        .catch(error => {
            console.log(error)
        })
}