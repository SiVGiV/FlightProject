import React, { useEffect, useState } from "react";
import { Accordion } from "react-bootstrap";

import API from "../api";
import { formatDate } from "../utils";
import { BASE_URL } from "../config";

import '../css/flightsPage.css';

export default function Flight({flightData}){

    const [origin, setOrigin] = useState();
    const [destination, setDestination] = useState();
    const [airline, setAirline] = useState();
    const [loadingData, setLoadingData] = useState(true);

    useEffect(()=>{
        setLoadingData(true)
        Promise.all([
            API.airline.get(flightData.airline),
            API.country.get(flightData.origin_country),
            API.country.get(flightData.destination_country),
        ]).then(([airlineResponse, originResponse, destinationResponse]) => {
            setAirline(airlineResponse.data.data)
            setOrigin(originResponse.data.data);
            setDestination(destinationResponse.data.data)
        }).finally(() => {
            setLoadingData(false)
        })
    }, [ flightData ])
    
    return (
            loadingData ? <div>Loading flight...</div> : <>
                <Accordion.Header>
                    <div className="flightHeaderDiv">
                        <div className="airlineName">{ airline.name }</div>
                        <div className="flexBreak"/>
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
                <img src={country ? BASE_URL + country.flag : ""} alt=""/>
                <div className="countryName">{ country ? country.name : ""}</div>
            </div>
            <div className="date">{ formatDate(isoDate) }</div>
        </div>
    );
}
