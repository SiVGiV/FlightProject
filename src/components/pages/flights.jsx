import React, { useEffect, useState } from "react";
import Flight from "./flight";
import { Accordion } from "react-bootstrap";
import axios from "axios";
import { BASE_URL } from "../../config";


export default function FlightsPage(){
    const [flights, setFlights] = useState([]);
    const [error, setError] = useState()
    const [loading, setLoading] = useState(true)

    
    useEffect(()=>{
        axios.get(`${BASE_URL}/flights/`, { params: { limit: 15, page: 1 } })
        .then(response => {
            console.log("response: " +  JSON.stringify(response.data));
            setFlights(response.data['data'])
        }, console.log)
        .catch(error => {
            console.log("error: " + error);
            setError(error);
        })
        .finally(() => {
            console.log('finally');
            setLoading(false);
        })
    }, []);

    if (loading){
        return (
            <h1> Loading... </h1>
        );
    }

    if (error){
        console.log("Error: " + error)
        return (
            <h1 style={{color: 'red'}}>{error.toString()}</h1>
        );
    }
    return (
        <Accordion>
            { flights.map( (flight, index) => <Flight flightData={flight} key={index}/> ) }
        </Accordion>
    );
}