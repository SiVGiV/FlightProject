import React, { useEffect, useState } from "react";
import Flight from "./flight";
import { Accordion, Form, Col, Row } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { Typeahead } from "react-bootstrap-typeahead";
import API from "../api";

import { makePagination } from "../utils"

export default function FlightsPage(){
    const [filters, setFilters] = useState({});
    
    const [loading, setLoading] = useState(true);
    const [flights, setFlights] = useState([]);
    const [flightsError, setFlightsError] = useState();
    
    const [loadingCountries, setLoadingCountries] = useState(true)
    const [countries, setCountries] = useState([])
    const [formError, setFormError] = useState()
    
    const [selectedOrigin, setSelectedOrigin] = useState([])
    const [selectedDestination, setSelectedDestination] = useState([])

    const [pagination, setPagination] = useState();
    const { flightPage } = useParams();

    
    useEffect(()=>{ // Get countries
        setLoadingCountries(true)
        API.countries.get({limit: 200, page: 1})
        .then(response => {
            setCountries(response.data.data)
        })
        .catch(error => {
            console.log(error.response.data.data)
            setFormError("Error loading country list...")
        })
        .finally(() => {
            setLoadingCountries(false)
        })
    }, [])

    useEffect(()=>{ // Refresh flights
        setLoading(true);
        API.flights.get({limit: 10, page: flightPage ?? 1, ...filters})
        .then(response => {
            setFlights(response.data.data ?? []);
            setPagination(response.data.pagination ?? []);
        })
        .catch(error => {
            setFlightsError(error.response.data);
        })
        .finally(() => {
            setLoading(false);
        })
    }, [ flightPage, filters ]);

    useEffect(() => { // Modify filters
        if(selectedOrigin[0] !== undefined){
            setFilters({
                ...filters,
                origin: selectedOrigin[0].id,
            })
        }
        else{
            if('origin' in filters){
                setFilters({
                    ...filters,
                    origin: undefined
                })
            }
        }
        if(selectedDestination[0] !== undefined){
            setFilters({
                ...filters,
                destination: selectedDestination[0].id,
            })
        }
        else{
            if('destination' in filters){
                setFilters({
                    ...filters,
                    destination: undefined
                })
            }
        }
    }, [selectedOrigin, selectedDestination])


    if (loading){
        return (
            <h1> Loading... </h1>
        );
    }

    if (flightsError){
        console.log("Error: " + flightsError)
        return (
            <h1 style={{color: 'red'}}>{flightsError ?? flightsError.map((err) => <p>{err}</p>)}</h1>
        );
    }

    return (
        <>
            <div className="flightPageContainer">
                <div className="flightPageFilters">
                    <Form>
                        {
                            loadingCountries ? <></> : 
                            <Row>
                                <h5>
                                    Filter by
                                </h5>
                                <Form.Group as={Col}>
                                    <Form.Label>Origin</Form.Label>
                                    <Typeahead
                                        id="basic-typeahead-single"
                                        labelKey="name"
                                        onChange={ setSelectedOrigin }
                                        options={countries}
                                        placeholder="Choose a country..."
                                        selected={ selectedOrigin }
                                    />
                                </Form.Group>
                                <Form.Group as={Col}>
                                    <Form.Label>Destination</Form.Label>
                                    <Typeahead
                                        id="basic-typeahead-single"
                                        labelKey="name"
                                        onChange={ setSelectedDestination }
                                        options={countries}
                                        placeholder="Choose a country..."
                                        selected={ selectedDestination }
                                    />
                                </Form.Group>
                            </Row>
                        }
                        <Form.Group>
                            <Form.Label>Departure Date</Form.Label>
                            <Form.Control
                                type="date"
                                onBlur={(selected) => { setFilters({...filters, date: selected.target.value}) }}
                                onKeyUp={(selected) => { selected.preventDefault(); if (selected.code === "Enter" || selected.code === "NumpadEnter"){setFilters({...filters, date: selected.target.value})} }}
                                defaultValue={filters.date ?? ""}
                            />
                        </Form.Group>
                    </Form>
                </div>
                {
                    loading ? <h1>Loading...</h1> : (
                        <Accordion>
                            {
                                flights.length === 0 ? <h1>No flights found...</h1> : flights.map( (flight, index) =>
                                    <Accordion.Item eventKey={"flight" + flight.id} key={index}>
                                        <Flight flightData={flight}/>
                                    </Accordion.Item>
                                )
                            }
                        </Accordion>
                    )
                }
                { makePagination(pagination.page, Math.ceil(pagination.total / pagination.limit), "/flights") }
            </div>
        </>
    );
}