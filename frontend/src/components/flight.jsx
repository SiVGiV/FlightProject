import React, { useEffect, useState, useContext } from "react";
import { Card, Collapse, Form, Row, Col, Button } from "react-bootstrap";
import "react-datetime/css/react-datetime.css";
import Datetime from "react-datetime";

import { APIContext } from '../contexts/api_contexts';
import { LoginContext } from '../contexts/auth_contexts';
import { formatDate } from "../utils";

import { Typeahead } from "react-bootstrap-typeahead";

import '../css/flightsPage.css';

export default function Flight({ flightData, allCountries, forceRender }) {
    const API = useContext(APIContext);
    const login = useContext(LoginContext);

    const [origin, setOrigin] = useState();
    const [destination, setDestination] = useState();
    const [airline, setAirline] = useState();
    const [loadingData, setLoadingData] = useState(true);
    const [expanded, setExpanded] = useState(false);
    const [expandable, setExpandable] = useState(false);
    useEffect(() => {
        setLoadingData(true)
        setOrigin(allCountries.find(country => country.id === flightData.origin_country))
        setDestination(allCountries.find(country => country.id === flightData.destination_country))
        API.airline.get(flightData.airline)
            .then((airlineResponse) => {
                setAirline(airlineResponse.data.data)
            }).catch(error => {
                console.log(error.data)
            }).finally(() => {
                setLoadingData(false)
            })

        switch (login.type) {
            case "airline":
                if (flightData.airline === login.entity_id) {
                    setExpandable(true);
                }
                break;
            case "customer":
                setExpandable(true);
                break;
            default:
                setExpandable(false);
                break;
        }
    }, [flightData, login, allCountries])

    function handleExpand(e) {
        setExpanded((!expanded) && expandable);
    }

    return (
        loadingData ? <div>Loading flight...</div> : <>
            <Card key={flightData.id} className={(flightData.is_cancelled ? "cancelled" : "normal") + "FlightCard flightCard" + (expandable ? " expandableCard" : "")}>
                <div className="flightHeaderDiv" aria-expanded={expanded} onMouseUp={handleExpand} aria-controls={`flight${flightData.id}`}>
                    <div className="airlineName">{airline?.name}</div>
                    <div className="flexBreak" />
                    <LocationListing country={origin} isoDate={formatDate(flightData.departure_datetime)} baseUrl={API.BASE_URL} />
                    <b className="destinationArrow">➜</b>
                    <LocationListing country={destination} isoDate={formatDate(flightData.arrival_datetime)} baseUrl={API.BASE_URL} />
                </div>

                <Collapse in={expanded}>
                    <div className="actions">
                        {
                            login.type === "customer" ?
                                <CustomerFlightActions flightData={flightData} /> :
                                login.type === "airline" ?
                                    <AirlineFlightActions flightData={flightData} allCountries={allCountries} forceRender={forceRender} /> :
                                    <></>
                        }
                    </div>
                </Collapse>
            </Card>
        </>
    );
}

function LocationListing({ country, isoDate, baseUrl }) {
    return (
        <div className="locationListing">
            <div className="country">
                <img src={country ? baseUrl + "/" + country.flag : ""} alt="" />
                <div className="countryName">{country ? country.name : ""}</div>
            </div>
            <div className="date">{formatDate(isoDate)}</div>
        </div>
    );
}


function CustomerFlightActions({ flightData }) {
    const [seatCount, setSeatCount] = useState(1);
    const API = useContext(APIContext);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    function purchase() {
        API.tickets.post({ flight_id: flightData.id, seat_count: seatCount }).then(response => {
            setMessage("Purchased ticket")
            setError("")
            console.log(response)
        }).catch(err => {
            setMessage("")
            console.log(err.response)
            if (err?.response?.data?.errors) {
                if (err?.response?.data?.errors?.indexOf("duplicate_ticket")) {
                    setError("You already have a ticket for this flight")
                }
                else {
                    setError(err.response.data.errors[0])
                }
            }
            else if (err?.response?.data?.error) {
                setError(err.response.data.error)
            }
            else {
                setError("Unknown error")
            }
        })
    }
    return (
        <Form>
            <Row>
                <p style={{ color: 'green' }}>{message}</p>
                <p style={{ color: 'red' }}>{error}</p>
                <Form.Group controlId="formSeatCount">
                    <Form.Label>Number of seats</Form.Label>
                    <Form.Control type="number" placeholder="1" min={1} onChange={(e) => { setSeatCount(e.target.value) }} />
                </Form.Group>
                <Form.Group controlId="formPurchase">
                    <Button onClick={() => purchase()}>Purchase</Button>
                </Form.Group>
            </Row>
        </Form>
    );
}

function AirlineFlightActions({ flightData, allCountries, forceRender }) {
    const API = useContext(APIContext);

    const [selectedOrigin, setSelectedOrigin] = useState([])
    const [selectedDestination, setSelectedDestination] = useState([])
    const [selectedDepartureDate, setSelectedDepartureDate] = useState()
    const [selectedArrivalDate, setSelectedArrivalDate] = useState()
    const [seatCount, setSeatCount] = useState()
    const [flightCanceled, setFlightCanceled] = useState()

    const [formError, setFormError] = useState("")
    const [formSuccess, setFormSuccess] = useState("")

    useEffect(() => {
        setSelectedOrigin([allCountries.find(country => country.id === flightData.origin_country)])
        setSelectedDestination([allCountries.find(country => country.id === flightData.destination_country)])
        setSelectedDepartureDate(flightData.departure_datetime)
        setSelectedArrivalDate(flightData.arrival_datetime)
        setSeatCount(flightData.total_seats)
        setFlightCanceled(flightData.is_cancelled)
    }, [allCountries, flightData]);

    function handleSubmit(e) {
        e.preventDefault();
        e.stopPropagation();
        setFormError("")
        setFormSuccess("")
        API.flight.patch(flightData.id, {
            origin_country: selectedOrigin[0]?.id,
            destination_country: selectedDestination[0]?.id,
            departure_datetime: selectedDepartureDate,
            arrival_datetime: selectedArrivalDate,
            total_seats: seatCount,
            is_cancelled: flightCanceled
        }).then(response => {
            setFormSuccess("Flight updated! Refreshing...")
            setTimeout(() => {
                forceRender(Math.random())
            }, 1000)
        }).catch(error => {
            var error_details = error?.response?.data?.error ?? error?.response?.data?.errors?.join(", ") ?? ""
            setFormError("Error updating flights! " + error_details);
        })
    }

    function handleCancel(e) {
        e.preventDefault();
        e.stopPropagation();
        API.flight.delete(flightData.id).then(response => {
            setFormSuccess("Flight deleted! Refreshing...")
            setTimeout(() => {
                forceRender(Math.random())
            }, 1000)
        }).catch(response => {
            setFormError("Error deleting flight")
        })
    }
    return (
        <Form className="flightUpdateForm">
            <fieldset disabled={flightData.is_cancelled}>

            <p className="errorMessage">{formError}</p>
            <p className="successMessage">{formSuccess}</p>
            <Row>

                <Col>
                    <Form.Group controlId="formOrigin" as={Col}>
                        <Form.Label>Origin</Form.Label>
                        <Typeahead
                            id="basic-typeahead-single"
                            labelKey="name"
                            onChange={setSelectedOrigin}
                            options={allCountries}
                            placeholder="Choose a country..."
                            selected={selectedOrigin}
                        />
                    </Form.Group>
                    <Form.Group controlId="formDeparture" as={Col}>
                        <Form.Label>Departure Date and Time</Form.Label>
                        <Datetime timeFormat={"HH:mm"} value={new Date(selectedDepartureDate)} onChange={(e) => { if(e?._isValid) setSelectedDepartureDate(e._d.toJSON());}} />
                    </Form.Group>
                </Col>
                <Col>
                    <Form.Group controlId="formDestination">
                        <Form.Label>Destination</Form.Label>
                        <Typeahead
                            id="basic-typeahead-single"
                            labelKey="name"
                            onChange={setSelectedDestination}
                            options={allCountries}
                            placeholder="Choose a country..."
                            selected={selectedDestination}
                        />
                    </Form.Group>
                    <Form.Group controlId="formDeparture">
                        <Form.Label>Arrival Date and Time</Form.Label>
                        <Datetime timeFormat={"HH:mm"} value={new Date(selectedArrivalDate)} onChange={(e) => { if(e?._isValid) setSelectedArrivalDate(e._d.toJSON());}} />
                    </Form.Group>
                </Col>
            </Row>
            <Row>
                <Form.Group controlId="formSeatCount">
                    <Form.Label>Number of seats</Form.Label>
                    <Form.Control type="number" defaultValue={seatCount} min={1} onChange={(e) => { setSeatCount(e.target.value) }} />
                </Form.Group>
            </Row>
                <Form.Group controlId="formSubmit">
                    <Button onClick={handleSubmit}>Update</Button>
                </Form.Group>
                <Form.Group controlId="formCancel">
                    <Button variant="danger" onClick={handleCancel}>Cancel</Button>
                </Form.Group>
            </fieldset>
        </Form>
    );
}