import React, { useState, useEffect, useContext } from "react";
import { Form, Button } from "react-bootstrap";
import { Typeahead } from "react-bootstrap-typeahead";
import { useNavigate } from "react-router-dom";
import { LoginContext, RefreshLoginContext } from "../contexts/auth_contexts";
import { APIContext } from "../contexts/api_contexts";
import { ParseErrorObjects } from "../utils";
import { Validations } from "../validations";

export default function Register() {
    const API = useContext(APIContext);
    const loginData = useContext(LoginContext);
    const refreshLoginData = useContext(RefreshLoginContext);

    const [fields, setFields] = useState({});
    const [fieldErrors, setFieldErrors] = useState({});
    const [validated, setValidated] = useState(false);
    const [formError, setFormError] = useState("");
    const [formSuccess, setFormSuccess] = useState("");
    const navigate = useNavigate();

    const setAndValidateField = (field, value, validationFunctions) => {
        var passedValidation = true;
        validationFunctions.forEach(validator => {
            passedValidation &&= validator(value);
        });
        if (passedValidation) {
            setFields({ ...fields, [field]: value });
            setFieldErrors({ ...fieldErrors, [field]: false });
        } else {
            setFields({ ...fields, [field]: undefined });
            setFieldErrors({ ...fieldErrors, [field]: true });
        }
    };

    const [selectUserTypeVisibility, setSelectUserTypeVisibility] = useState({
        display: "none",
    });
    const [userType, setUserType] = useState("customer");

    useEffect(() => {
        switch (loginData.type) {
            case "admin":
                setSelectUserTypeVisibility({});
                break;
            case "anon":
                setSelectUserTypeVisibility({ display: "none" });
                break;
            case "airline":
            case "customer":
                navigate("/");
                break;
            default:
                break;
        }
    }, [loginData]);

    const handleSubmit = event => {
        setFormError(undefined);
        const form = event.currentTarget;
        event.preventDefault();
        if (form.checkValidity() === false) {
            event.stopPropagation();
            return;
        }
        setValidated(true);
        var promise = API.customers.post;
        switch (userType) {
            case "airline":
                promise = API.airlines.post(fields);
                break;
            case "admin":
                promise = API.admins.post(fields);
                break;
            default:
                promise = API.customers.post(fields);
                break;
        }
        promise
            .then(response => {
                if(loginData.type === "anon"){
                    API.auth.login({username: fields.username, password: fields.password})
                    .then(response => {
                        navigate("/");
                    }).catch(error => {
                        console.log(error);
                        setFormError(
                            ParseErrorObjects(error?.response?.data).join("\n")
                        );
                    });
                }else{
                    // Add success message
                    setFormSuccess("Registration successful!");
                    // Clear form
                    setFields({});
                    setFieldErrors({});
                    setValidated(false);

                }
            })
            .catch(error => {
                console.log(error);
                setFormError(
                    ParseErrorObjects(error?.response.data).join("\n")
                );
            });
    };

    function onUserTypeChange(e) {
        setUserType(e.target.value);
    }
    return (
        <>
            <div
                id="usertype-radio"
                style={selectUserTypeVisibility}
                onChange={onUserTypeChange}
            >
                <input
                    type="radio"
                    value="customer"
                    name="userType"
                    id="customerUserTypeRadio"
                    selected
                />
                <label htmlFor="customerUserTypeRadio">Customer</label>
                <br />
                <input
                    type="radio"
                    value="airline"
                    name="userType"
                    id="airlineUserTypeRadio"
                />
                <label htmlFor="airlineUserTypeRadio">Airline</label>
                <br />
                <input
                    type="radio"
                    value="admin"
                    name="userType"
                    id="adminUserTypeRadio"
                />
                <label htmlFor="adminUserTypeRadio">Admin</label>
                <br />
            </div>
            <Form validated={validated} onSubmit={handleSubmit}>
                <h3 className="error">{formError}</h3>
                <h3 className="message">{formSuccess}</h3>
                <Form.Group controlId="formUsername">
                    <Form.Label>Username</Form.Label>
                    <Form.Control
                        type="text"
                        placeholder="Enter username"
                        onChange={e =>
                            setAndValidateField("username", e.target.value, [
                                Validations.validateUsername,
                                Validations.validateRequired,
                            ])
                        }
                        isInvalid={fieldErrors.username}
                        required
                    />
                    <Form.Control.Feedback type="invalid">
                        Username must be alphanumeric and at least 3 characters
                        long
                    </Form.Control.Feedback>
                </Form.Group>
                <Form.Group controlId="formPassword">
                    <Form.Label>Password</Form.Label>
                    <Form.Control
                        type="password"
                        placeholder="Password"
                        onChange={e =>
                            setAndValidateField("password", e.target.value, [
                                Validations.validatePassword,
                                Validations.validateRequired,
                            ])
                        }
                        isInvalid={fieldErrors.password}
                        required
                    />
                    <Form.Control.Feedback type="invalid">
                        Password must be at least 8 characters long and contain
                        at least one uppercase letter, one lowercase letter, and
                        one number or special character
                    </Form.Control.Feedback>
                </Form.Group>
                <Form.Group controlId="formPassword2">
                    <Form.Label>Confirm Password</Form.Label>
                    <Form.Control
                        type="password"
                        placeholder="Confirm Password"
                        onChange={e =>
                            setAndValidateField("password2", e.target.value, [
                                password2 => password2 === fields.password,
                                Validations.validateRequired,
                            ])
                        }
                        isInvalid={fieldErrors.password2}
                        required
                    />
                    <Form.Control.Feedback type="invalid">
                        Passwords do not match
                    </Form.Control.Feedback>
                </Form.Group>
                <Form.Group controlId="formEmail">
                    <Form.Label>Email</Form.Label>
                    <Form.Control
                        type="email"
                        placeholder="Email"
                        onChange={e =>
                            setAndValidateField("email", e.target.value, [
                                Validations.validateEmail,
                                Validations.validateRequired,
                            ])
                        }
                        isInvalid={fieldErrors.email}
                        required
                    />
                    <Form.Control.Feedback type="invalid">
                        Please enter a valid email address
                    </Form.Control.Feedback>
                </Form.Group>
                <RegistrationRouter
                    userType={userType}
                    fields={fields}
                    setFields={setFields}
                    fieldErrors={fieldErrors}
                    setAndValidateField={setAndValidateField}
                    setFormError={setFormError}
                />
                <br />
                <Button variant="primary" type="submit">
                    Register
                </Button>
            </Form>
        </>
    );
}

function RegistrationRouter({
    userType,
    setFormError,
    fieldErrors,
    setAndValidateField,
}) {
    switch (userType) {
        case "airline":
            return AirlineFields({
                fieldErrors,
                setAndValidateField,
                required: true,
            });
        case "admin":
            return AdminFields({
                fieldErrors,
                setAndValidateField,
                required: true,
            });
        default:
            return CustomerFields({
                setFormError,
                fieldErrors,
                setAndValidateField,
                required: true,
            });
    }
}

export function CustomerFields({
    setAndValidateField,
    fieldErrors,
    placeholders,
    required,
}) {
    if (placeholders === undefined) placeholders = {};
    if (required === undefined) required = false;
    return (
        <div id="additionalFields">
            <Form.Group controlId="formFirstName">
                <Form.Label>First Name</Form.Label>
                <Form.Control
                    type="text"
                    placeholder={placeholders["first_name"] ?? "First name"}
                    onChange={e =>
                        setAndValidateField("first_name", e.target.value, [
                            required
                                ? Validations.validateRequired
                                : () => true,
                        ])
                    }
                    isInvalid={fieldErrors.first_name}
                    required={required}
                />
            </Form.Group>
            <Form.Group controlId="formLastName">
                <Form.Label>Last Name</Form.Label>
                <Form.Control
                    type="text"
                    placeholder={placeholders["last_name"] ?? "Last name"}
                    onChange={e =>
                        setAndValidateField("last_name", e.target.value, [
                            required
                                ? Validations.validateRequired
                                : () => true,
                        ])
                    }
                    isInvalid={fieldErrors.last_name}
                    required={required}
                />
            </Form.Group>
            <Form.Group controlId="formAddress">
                <Form.Label>Address</Form.Label>
                <Form.Control
                    type="text"
                    placeholder={placeholders["address"] ?? "Address"}
                    onChange={e =>
                        setAndValidateField("address", e.target.value, [
                            required
                                ? Validations.validateRequired
                                : () => true,
                        ])
                    }
                    isInvalid={fieldErrors.address}
                    required={required}
                />
            </Form.Group>
            <Form.Group controlId="formPhone">
                <Form.Label>Phone</Form.Label>
                <Form.Control
                    type="text"
                    placeholder={placeholders["phone_number"] ?? "Phone"}
                    onChange={e =>
                        setAndValidateField("phone_number", e.target.value, [
                            Validations.validatePhone,
                            required
                                ? Validations.validateRequired
                                : () => true,
                        ])
                    }
                    isInvalid={fieldErrors.phone_number}
                    required={required}
                />
                <Form.Control.Feedback type="invalid">
                    Please enter a valid Israeli phone number
                </Form.Control.Feedback>
            </Form.Group>
        </div>
    );
}

export function AirlineFields({
    setAndValidateField,
    setFormError,
    placeholders,
    required,
    fieldErrors,
}) {
    const API = useContext(APIContext);
    const [countries, setCountries] = useState([]);
    const [selectedAirlineCountry, setSelectedAirlineCountry] = useState([]);
    const [loadingCountries, setLoadingCountries] = useState(true);

    if (placeholders === undefined) placeholders = {};
    if (required === undefined) required = false;

    useEffect(() => {
        // Get countries
        setLoadingCountries(true);
        API.countries
            .get({ limit: 200, page: 1 })
            .then(response => {
                setCountries(response.data.data);
            })
            .catch(error => {
                console.log(error?.response.data.data);
                setFormError("Error loading country list...");
            })
            .finally(() => {
                setLoadingCountries(false);
            });
    }, []);

    useEffect(() => {
        setAndValidateField("country", selectedAirlineCountry[0]?.id, [
            required ? Validations.validateRequired : () => true,
        ]);
    }, [selectedAirlineCountry]);

    return (
        <div id="additionalFields">
            <Form.Group controlId="formAirlineName">
                <Form.Label>Airline Name</Form.Label>
                <Form.Control
                    type="text"
                    placeholder={placeholders["name"] ?? "Airline Name"}
                    onChange={e =>
                        setAndValidateField("name", e.target.value, [
                            required
                                ? Validations.validateRequired
                                : () => true,
                        ])
                    }
                    required={required}
                    isInvalid={fieldErrors.name}
                />
            </Form.Group>
            <Form.Group controlId="formAirlineCountry">
                <Form.Label>Airline Country</Form.Label>
                <Typeahead
                    id="basic-typeahead-single"
                    labelKey="name"
                    onChange={setSelectedAirlineCountry}
                    options={countries}
                    placeholder={
                        loadingCountries
                            ? "Loading..."
                            : countries.find(
                                  country =>
                                      country.id === placeholders["country"]
                              )?.name ?? "Select a country"
                    }
                    selected={selectedAirlineCountry}
                    disabled={loadingCountries}
                    required={required}
                    isInvalid={fieldErrors.country}
                />
            </Form.Group>
        </div>
    );
}

function AdminFields({ setAndValidateField, required }) {
    if (required === undefined) required = false;
    return (
        <div id="additionalFields">
            <Form.Group controlId="formFirstName">
                <Form.Label>First Name</Form.Label>
                <Form.Control
                    type="text"
                    placeholder="First name"
                    onChange={e =>
                        setAndValidateField("first_name", e.target.value, [
                            required
                                ? Validations.validateRequired
                                : () => true,
                        ])
                    }
                    required={required}
                />
            </Form.Group>
            <Form.Group controlId="formLastName">
                <Form.Label>Last Name</Form.Label>
                <Form.Control
                    type="text"
                    placeholder="Last name"
                    onChange={e =>
                        setAndValidateField("last_name", e.target.value, [
                            required
                                ? Validations.validateRequired
                                : () => true,
                        ])
                    }
                    required={required}
                />
            </Form.Group>
        </div>
    );
}
