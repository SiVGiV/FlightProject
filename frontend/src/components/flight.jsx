import React, { useEffect, useState, useContext } from "react";
import { Card, Collapse } from "react-bootstrap";

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
    return (<>Customer Actions</>);
}

function AirlineFlightActions({ flightData }) {

    return (<>Airline Actions</>);
}