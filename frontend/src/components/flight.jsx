import React, { useEffect, useState, useContext } from "react";
import { Accordion } from "react-bootstrap";

import { APIContext } from '../contexts/api_context';
import { formatDate } from "../utils";

import '../css/flightsPage.css';

export default function Flight({flightData}){
    const API = useContext(APIContext);
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
        }).catch(error => {
            console.log(error.data)
        }).finally(() => {
            setLoadingData(false)
        })
    }, [ flightData ])
    
    return (
        loadingData ? <div>Loading flight...</div> : <>
            <Accordion.Header>
                <div className="flightHeaderDiv">
                    <div className="airlineName">{ airline?.name }</div>
                    <div className="flexBreak"/>
                    <LocationListing country={ origin } isoDate={ formatDate(flightData.departure_datetime) } baseUrl={API.BASE_URL}/>
                    <b className="destinationArrow">➜</b>
                    <LocationListing country={ destination } isoDate={ formatDate(flightData.arrival_datetime) } baseUrl={API.BASE_URL}/>
                </div>
            </Accordion.Header>
            <Accordion.Body>
            </Accordion.Body>
        </>
    );
}

function LocationListing({country, isoDate, baseUrl}){
    return (
        <div className="locationListing">
            <div className="country">
                <img src={country ? baseUrl + "/" + country.flag : ""} alt=""/>
                <div className="countryName">{ country ? country.name : ""}</div>
            </div>
            <div className="date">{ formatDate(isoDate) }</div>
        </div>
    );
}
