import React from "react";
import { formatDate } from "../../utils/dateUtils";
import AccordionItem from "react-bootstrap/esm/AccordionItem";
import { Accordion } from "react-bootstrap";



export default function Flight({flightData}){
    console.log("Flight:" + flightData)
    return (
        <>{ JSON.stringify(flightData) }</>
    );

    return (
        <AccordionItem>
            <Accordion.Header>
                <div style={{'display': 'flex'}}>
                <LocationListing country="Israel" isoDate="2020-05-12T23:50:21.817Z"/>

                <LocationListing country="Israel" isoDate="2020-05-12T23:50:21.817Z"/>
                </div>
            </Accordion.Header>
            <Accordion.Body>
            </Accordion.Body>
        </AccordionItem>
    );
}

function LocationListing({country, isoDate}){
    return (
        <div style={{"display": "flex", "flexDirection": 'column'}}>
            <h1>{country}</h1>
            <h3>{ formatDate(isoDate) }</h3>
        </div>
    );
}
