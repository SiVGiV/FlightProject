import React, { useEffect, useState } from "react";
import Flight from "./flight";
import { Accordion, Pagination } from "react-bootstrap";
import { useParams } from "react-router-dom";
import API from "../api";

export default function FlightsPage(){
    const [flights, setFlights] = useState([]);
    const [error, setError] = useState();
    const [loading, setLoading] = useState(true);

    const { flightPage } = useParams();
    
    useEffect(()=>{
        API.flights.get({limit: 10, page: 1})
        .then(response => {
            setFlights(response.data['data']);
        }, console.log)
        .catch(error => {
            console.log("error: " + error);
            setError(error);
        })
        .finally(() => {
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
        { 
            flights.map( (flight, index) =>{
                return (
                    <Accordion.Item eventKey={"flight" + flight.id.toString()} key={index}>
                        <Flight flightData={flight}/>
                    </Accordion.Item>
                );
                }
            )
        }
        </Accordion>
    );
}