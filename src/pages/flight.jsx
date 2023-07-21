import React, { useEffect, useState } from "react";
import { formatDate } from "../utils/dateUtils";
import { Accordion } from "react-bootstrap";

import API from "../api";
import { BASE_URL } from "../config";

import '../css/flightsPage.css';

export default function Flight({flightData}){

    const [origin, setOrigin] = useState();
    const [destination, setDestination] = useState();
    useEffect(()=>{
        Promise.all([
            API.country.get(flightData.origin_country),
            API.country.get(flightData.destination_country),
        ]).then(([originResponse, destinationResponse]) => {
            setOrigin(originResponse.data['data']);
            setDestination(destinationResponse.data['data'])
        })
    }, [])
    
    return (
            <>
                <Accordion.Header>
                    <div className="flightHeaderDiv">
                        <LocationListing country={ origin } isoDate={ formatDate(flightData.departure_datetime) }/>
                        <b className="destinationArrow">➜</b>
                        <LocationListing country={ destination } isoDate={ formatDate(flightData.arrival_datetime) }/>
                    </div>
                </Accordion.Header>
                <Accordion.Body>
                </Accordion.Body>
            </>
    );
}

function LocationListing({country, isoDate}){
    return (
        <div className="locationListing">
            <div className="country">
                <img src={BASE_URL + country?.flag} alt={country?.name + "_flag"} style={{maxHeight: "50px"}}/>
                <h1>{ country?.name }</h1>
            </div>
            <div><h3>{ formatDate(isoDate) }</h3></div>
        </div>
    );
}
