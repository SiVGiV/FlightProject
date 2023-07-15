import React from "react";
import Flight from "./flight";
import { Accordion } from "react-bootstrap";

export default function FlightsPage(){

    return (
        <Accordion>
            <Flight id={1}></Flight>
        </Accordion>
    );
}