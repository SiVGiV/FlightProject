import React from "react";
import { formatDate } from "../../utils/dateUtils";
import AccordionItem from "react-bootstrap/esm/AccordionItem";
import { Accordion } from "react-bootstrap";

export default function Flight(id){
    return (
        <AccordionItem>
            <Accordion.Header>
                <LocationListing country="Israel" isoDate="2020-05-12T23:50:21.817Z"/>
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
            <h3>{formatDate(isoDate)}</h3>
            <h3></h3>
        </div>
    );
}
