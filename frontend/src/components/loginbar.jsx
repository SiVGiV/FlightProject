import React, { useContext, useEffect, useState } from "react";
import { Button, Modal, Form } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { LoginContext } from "../contexts/auth_contexts";
import { APIContext } from "../contexts/api_contexts";
import { AirlineFields, CustomerFields } from "../pages/register";
import { ParseErrorObjects } from "../../utilities/helpers";

export default function Welcome() {
    const API = useContext(APIContext);
    const navigate = useNavigate();

    const [showUpdateProfile, setShowUpdateProfile] = useState(false);

    const loginValue = useContext(LoginContext);
    return (
        <div className="welcomeBar">
            {loginValue.logged_in
                ? `Welcome, ${loginValue.entity_name}! `
                : `Welcome! Please login to continue.`}
            &nbsp;&nbsp;
            {loginValue.type === "admin" || loginValue.type === "anon" ? (
                <></>
            ) : (
                <Button
                    onClick={() => {
                        setShowUpdateProfile(true);
                    }}
                >
                    Edit Profile
                </Button>
            )}
            &nbsp;&nbsp;
            <Button
                onClick={
                    loginValue.logged_in
                        ? () => logout(API, navigate)
                        : () => login(navigate)
                }
                className="navbar-button"
            >
                {loginValue.logged_in ? "Logout" : "Login"}
            </Button>
            {/*<RegistrationModal/>*/}
            {/*<LoginModal/>*/}
            <UpdateProfileModal
                show={showUpdateProfile}
                handleClose={() => setShowUpdateProfile(false)}
            />
        </div>
    );
}

function login(navigate) {
    navigate("/login");
}

function logout(API, navigate) {
    API.auth
        .logout()
        .then(response => {
            navigate("/login");
        })
        .catch(error => {
            console.log(error);
        });
}

function UpdateProfileModal({ show, handleClose }) {
    const API = useContext(APIContext);
    const LoginData = useContext(LoginContext);

    const [fields, setFields] = useState({});
    const [formError, setFormError] = useState("");
    const [fieldErrors, setFieldErrors] = useState({});
    const [placeholders, setPlaceholders] = useState({});
    const [validated, setValidated] = useState(false);

    useEffect(() => {
        var promise;
        switch (LoginData.type) {
            case "airline":
                promise = API.airline.get(LoginData.entity_id);
                break;
            case "customer":
                promise = API.customer.get(LoginData.entity_id);
                break;
            default:
                return;
        }
        promise
            .then(response => {
                setPlaceholders(response.data.data);
            })
            .catch(error => {
                console.log(error);
            });
    }, [LoginData]);

    const setAndValidateField = (field, value, validationFunctions) => {
        var passedValidation = true;
        validationFunctions.forEach(validator => {
            passedValidation &&= validator(value);
        });
        if (passedValidation) {
            setFields({ ...fields, [field]: value });
            setFieldErrors({ ...fieldErrors, [field]: false });
        } else {
            setFieldErrors({ ...fieldErrors, [field]: true });
        }
    };

    function update(e) {
        setFormError(undefined);
        e.preventDefault();
        const form = e.currentTarget;
        if (!form.checkValidity()) {
            e.stopPropagation();
            return;
        }
        var promise;
        if (LoginData.type === "airline") {
            promise = API.airline.patch(LoginData.entity_id, { ...fields });
        } else if (LoginData.type === "customer") {
            promise = API.customer.patch(LoginData.entity_id, fields);
        } else {
            return;
        }
        promise
            .then(response => {
                setFormError(undefined);
                setFieldErrors({});
                setValidated(true);
                window.location.reload();
                handleClose();
            })
            .catch(error => {
                setValidated(false);
                var errors = ParseErrorObjects(error?.response.data);
                setFormError(errors.join("\n"));
            });
    }

    return (
        <Modal show={show} onHide={handleClose}>
            <Form Form validated={validated} onSubmit={update}>
                <Modal.Header closeButton>
                    <Modal.Title>Update Profile</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <p className="error">{formError}</p>
                    {LoginData.type === "airline" ? (
                        <AirlineFields
                            setAndValidateField={setAndValidateField}
                            fieldErrors={fieldErrors}
                            setFormError={setFormError}
                            placeholders={placeholders}
                        />
                    ) : LoginData.type === "customer" ? (
                        <CustomerFields
                            setAndValidateField={setAndValidateField}
                            fieldErrors={fieldErrors}
                            placeholders={placeholders}
                        />
                    ) : (
                        <></>
                    )}
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={handleClose}>
                        Close
                    </Button>
                    <Button variant="primary" type="submit">
                        Save Changes
                    </Button>
                </Modal.Footer>
            </Form>
        </Modal>
    );
}
