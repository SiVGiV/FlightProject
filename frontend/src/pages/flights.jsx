import React, { useEffect, useState, useContext, useCallback } from "react";
import Flight from "../components/flight";
import { Form, Col, Row, Button, Modal, Spinner } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { Typeahead } from "react-bootstrap-typeahead";
import { APIContext } from "../contexts/api_contexts";
import { LoginContext } from "../contexts/auth_contexts";
import Datetime from "react-datetime";

import { makePagination } from "../utils";

export default function FlightsPage() {
    const API = useContext(APIContext);
    const login = useContext(LoginContext);
    const [filters, setFilters] = useState({});

    const [reRender, forceRender] = useState(0);

    const [loading, setLoading] = useState(true);
    const [flights, setFlights] = useState([]);
    const [flightsError, setFlightsError] = useState();

    const [selectedOrigin, setSelectedOrigin] = useState([]);
    const [selectedDestination, setSelectedDestination] = useState([]);
    const [selectedAirline, setSelectedAirline] = useState([]);
    const [onlyMine, setOnlyMine] = useState(false);
    const [selectedDate, setSelectedDate] = useState();

    const [pagination, setPagination] = useState();
    const { flightPage } = useParams();

    const [loadingCountries, setLoadingCountries] = useState(true);
    const [countries, setCountries] = useState([]);

    const refreshFlights = useCallback(() => {
        // Refresh flights
        setLoading(true);
        var forceAirline = {};
        if (onlyMine) {
            forceAirline.airline = login.entity_id;
        }
        API.flights
            .get({
                limit: 10,
                page: flightPage ?? 1,
                ...filters,
                ...forceAirline,
            })
            .then(response => {
                setFlights(response.data?.data ?? []);
                setPagination(response.data?.pagination ?? []);
            })
            .catch(error => {
                var error_details =
                    error?.response?.data?.error ??
                    error?.response?.data?.errors?.join(", ") ??
                    "";
                setFlightsError("Error getting flights! " + error_details);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [API, filters, flightPage, login.entity_id, onlyMine]);

    const handleFilter = useCallback(
        e => {
            e.preventDefault();
            e.stopPropagation();
            refreshFlights();
        },
        [refreshFlights]
    );

    useEffect(() => {
        // OnLoad

        setLoadingCountries(true);
        API.countries
            .get({ limit: 200, page: 1 })
            .then(response => {
                setCountries(response.data.data);
            })
            .catch(error => {
                console.log(error);
            })
            .finally(() => {
                setLoadingCountries(false);
            });
        refreshFlights();
    }, [API, refreshFlights]);

    const [airlineNameInput, setAirlineNameInput] = useState("");
    const [airlines, setAirlines] = useState([]);
    const [airlinesLoading, setAirlinesLoading] = useState(false);
    useEffect(() => {
        // Get airlines
        if (airlineNameInput !== "") {
            setAirlinesLoading(true);
            API.airlines
                .get({ limit: 50, page: 1, name: airlineNameInput })
                .then(response => {
                    setAirlines(response.data.data ?? []);
                })
                .catch(error => {
                    console.log(error);
                })
                .finally(() => {
                    setAirlinesLoading(false);
                });
        }
    }, [airlineNameInput, API]);

    function handleOnlyMine(e) {
        if (e.target.checked) {
            setOnlyMine(true);
        } else {
            setOnlyMine(false);
        }
    }
    useEffect(() => refreshFlights(), [onlyMine, reRender, refreshFlights]);

    useEffect(() => {
        // Modify filters
        var tempFilters = {
            origin: selectedOrigin[0]?.id,
            destination: selectedDestination[0]?.id,
            date: selectedDate?.target.value,
            airline: selectedAirline[0]?.id,
        };

        for (var key in tempFilters) {
            if (tempFilters[key] === undefined) {
                delete tempFilters[key];
            }
        }

        setFilters(tempFilters);
    }, [selectedOrigin, selectedDestination, selectedAirline, selectedDate]);

    const handleToggle = e => {
        e.stopPropagation();
        console.log(e);
        // setActiveKey( === eventKey ? null : eventKey);
    };

    const [showCreate, setShowCreate] = useState(false);

    function onHideCreationModal() {
        setShowCreate(false);
    }

    return (
        <>
            <div className="flightPageContainer">
                <div className="flightPageFilters">
                    <Form>
                        <Row>
                            <h5>Filter by</h5>
                            <Form.Group as={Col}>
                                <Form.Label>Origin</Form.Label>
                                <Typeahead
                                    id="basic-typeahead-single"
                                    labelKey="name"
                                    onChange={setSelectedOrigin}
                                    options={countries}
                                    placeholder="Choose a country..."
                                    selected={selectedOrigin}
                                    isLoading={loadingCountries}
                                />
                            </Form.Group>
                            <Form.Group as={Col}>
                                <Form.Label>Destination</Form.Label>
                                <Typeahead
                                    id="basic-typeahead-single"
                                    labelKey="name"
                                    onChange={setSelectedDestination}
                                    options={countries}
                                    placeholder="Choose a country..."
                                    selected={selectedDestination}
                                    isLoading={loadingCountries}
                                />
                            </Form.Group>
                        </Row>
                        <Form.Group>
                            <Form.Label>Departure Date</Form.Label>
                            <Form.Control
                                type="date"
                                onChange={setSelectedDate}
                                defaultValue={filters.date ?? ""}
                            />
                        </Form.Group>
                        <Row>
                            <Form.Group>
                                <Form.Label>Airline Name</Form.Label>
                                <Typeahead
                                    id="remote-api-typeahead"
                                    labelKey="name" // replace 'name' with the key in your data objects
                                    onInputChange={text =>
                                        setAirlineNameInput(text)
                                    }
                                    onChange={setSelectedAirline}
                                    options={airlines}
                                    placeholder="Start typing..."
                                    selected={selectedAirline}
                                    isLoading={airlinesLoading}
                                />
                            </Form.Group>
                            {login.type === "airline" ? (
                                <Form.Group>
                                    <Form.Check
                                        type="switch"
                                        id="mine-switch"
                                        label="Only show my flights"
                                        onChange={handleOnlyMine}
                                    />
                                </Form.Group>
                            ) : (
                                <></>
                            )}
                        </Row>
                        <Row className="filterButtons">
                            <Button
                                variant="primary"
                                type="submit"
                                onClick={handleFilter}
                            >
                                Filter
                            </Button>
                            {login.type === "airline" ? (
                                <Button
                                    variant="success"
                                    onClick={() => setShowCreate(true)}
                                >
                                    Create a new flight
                                </Button>
                            ) : (
                                <></>
                            )}
                        </Row>
                    </Form>
                    <FlightCreationModal
                        showCreate={showCreate}
                        onHide={onHideCreationModal}
                        countries={countries}
                        forceRender={forceRender}
                    />
                </div>
                {loading ? (
                    <div
                        style={{
                            display: "flex",
                            justifyContent: "center",
                            padding: "50px",
                        }}
                    >
                        <Spinner animation="border" />
                    </div>
                ) : flightsError ? (
                    <h1>{flightsError}</h1>
                ) : flights.length === 0 ? (
                    <h1>No flights found...</h1>
                ) : (
                    flights.map((flight, index) => (
                        <Flight
                            flightData={flight}
                            key={index}
                            onClick={handleToggle}
                            allCountries={countries}
                            forceRender={forceRender}
                        />
                    ))
                )}
                {makePagination(
                    pagination?.page,
                    Math.ceil(pagination?.total / pagination?.limit),
                    "/flights"
                )}
            </div>
        </>
    );
}

function FlightCreationModal({ showCreate, onHide, countries, forceRender }) {
    const login = useContext(LoginContext);
    const API = useContext(APIContext);

    const [selectedOrigin, setSelectedOrigin] = useState([]);
    const [selectedDestination, setSelectedDestination] = useState([]);
    const [selectedDepartureDate, setSelectedDepartureDate] = useState(
        new Date().toJSON()
    );
    const [selectedArrivalDate, setSelectedArrivalDate] = useState(
        new Date().toJSON()
    );
    const [seatCount, setSeatCount] = useState();

    const [formError, setFormError] = useState("");
    const [formSuccess, setFormSuccess] = useState("");

    function handleSubmit(e) {
        e.preventDefault();
        e.stopPropagation();
        setFormError("");
        setFormSuccess("");
        API.flights
            .post({
                airline: login.entity_id,
                origin_country: selectedOrigin[0]?.id,
                destination_country: selectedDestination[0]?.id,
                departure_datetime: selectedDepartureDate,
                arrival_datetime: selectedArrivalDate,
                total_seats: seatCount,
            })
            .then(response => {
                setFormSuccess("Flight updated! Refreshing...");
                setTimeout(() => {
                    forceRender(Math.random());
                    onHide();
                }, 1000);
            })
            .catch(response => {
                console.log(response);
                var error_details =
                    response?.response?.data?.error ??
                    response?.response?.data?.errors?.join(", ") ??
                    "";
                setFormError("Error updating flight! " + error_details);
            });
    }

    return (
        <>
            <Modal
                show={showCreate}
                onHide={onHide}
                backdrop="static"
                keyboard={false}
            >
                <Modal.Header closeButton>
                    <Modal.Title>Modal heading</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form className="flightUpdateForm">
                        <p className="formError">{formError}</p>
                        <p className="formSuccess">{formSuccess}</p>
                        <Row>
                            <Col>
                                <Form.Group controlId="formOrigin" as={Col}>
                                    <Form.Label>Origin</Form.Label>
                                    <Typeahead
                                        id="basic-typeahead-single"
                                        labelKey="name"
                                        onChange={setSelectedOrigin}
                                        options={countries}
                                        placeholder="Choose a country..."
                                        selected={selectedOrigin}
                                    />
                                </Form.Group>
                                <Form.Group controlId="formDeparture" as={Col}>
                                    <Form.Label>
                                        Departure Date and Time
                                    </Form.Label>
                                    <Datetime
                                        dateFormat={"MMMM Do, YYYY"}
                                        timeFormat={"[at] HH:mm"}
                                        value={new Date(selectedDepartureDate)}
                                        onChange={e => {
                                            if (e?._isValid)
                                                setSelectedDepartureDate(
                                                    e._d.toJSON()
                                                );
                                        }}
                                    />
                                </Form.Group>
                            </Col>
                            <Col>
                                <Form.Group controlId="formDestination">
                                    <Form.Label>Destination</Form.Label>
                                    <Typeahead
                                        id="basic-typeahead-single"
                                        labelKey="name"
                                        onChange={setSelectedDestination}
                                        options={countries}
                                        placeholder="Choose a country..."
                                        selected={selectedDestination}
                                    />
                                </Form.Group>
                                <Form.Group controlId="formDeparture">
                                    <Form.Label>
                                        Arrival Date and Time
                                    </Form.Label>
                                    <Datetime
                                        dateFormat={"MMMM Do, YYYY"}
                                        timeFormat={"[at] HH:mm"}
                                        value={new Date(selectedArrivalDate)}
                                        onChange={e => {
                                            if (e?._isValid)
                                                setSelectedArrivalDate(
                                                    e._d.toJSON()
                                                );
                                        }}
                                    />
                                </Form.Group>
                            </Col>
                        </Row>
                        <Row>
                            <Form.Group controlId="formSeatCount">
                                <Form.Label>Number of seats</Form.Label>
                                <Form.Control
                                    type="number"
                                    defaultValue={seatCount}
                                    min={1}
                                    onChange={e => {
                                        setSeatCount(e.target.value);
                                    }}
                                />
                            </Form.Group>
                        </Row>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={onHide}>
                        Close
                    </Button>
                    <Button variant="success" onClick={handleSubmit}>
                        Add Flight
                    </Button>
                </Modal.Footer>
            </Modal>
        </>
    );
}
