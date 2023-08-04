import React, { useEffect, useState, useContext } from "react";
import { Card, Collapse, Form, Row, Button } from "react-bootstrap";

import { APIContext } from '../contexts/api_context';
import { LoginContext } from '../contexts/auth_contexts';
import { formatDate } from "../utils";

import '../css/flightsPage.css';

export default function Flight({ flightData, handleToggle }) {
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
        Promise.all([
            API.airline.get(flightData.airline),
            API.country.get(flightData.origin_country),
            API.country.get(flightData.destination_country),
        ]).then(([airlineResponse, originResponse, destinationResponse]) => {
            setAirline(airlineResponse.data.data)
            setOrigin(originResponse.data.data);
            setDestination(destinationResponse.data.data)
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
    }, [flightData, login])

    function handleExpand(e) {
        setExpanded((!expanded) && expandable);
    }

    return (
        loadingData ? <div>Loading flight...</div> : <>
            <Card >
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
                                    <AirlineFlightActions flightData={flightData} /> :
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

function AirlineFlightActions({ flightData }) {

    return (<>Airline Actions</>);
}