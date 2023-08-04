import React, { useEffect, useState, useContext } from "react";
import Flight from "../components/flight";
import { Form, Col, Row, Button } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { Typeahead } from "react-bootstrap-typeahead";
import { APIContext } from "../contexts/api_context";
import { LoginContext } from "../contexts/auth_contexts";

import { makePagination } from "../utils"

export default function FlightsPage() {
    const API = useContext(APIContext);
    const login = useContext(LoginContext);
    const [filters, setFilters] = useState({});

    const [loading, setLoading] = useState(true);
    const [flights, setFlights] = useState([]);
    const [flightsError, setFlightsError] = useState();


    const [selectedOrigin, setSelectedOrigin] = useState([])
    const [selectedDestination, setSelectedDestination] = useState([])
    const [selectedAirline, setSelectedAirline] = useState([])
    const [onlyMine, setOnlyMine] = useState(false)
    const [selectedDate, setSelectedDate] = useState()

    const [pagination, setPagination] = useState();
    const { flightPage } = useParams();

    const [loadingCountries, setLoadingCountries] = useState(true)
    const [countries, setCountries] = useState([])
    useEffect(() => { // OnLoad

        setLoadingCountries(true)
        API.countries.get({ limit: 200, page: 1 })
            .then(response => {
                setCountries(response.data.data)
            })
            .catch(error => {
                console.log(error)
            })
            .finally(() => {
                setLoadingCountries(false)
            })
        refreshFlights();
    }, [])


    const [airlineNameInput, setAirlineNameInput] = useState('');
    const [airlines, setAirlines] = useState([]);
    const [airlinesLoading, setAirlinesLoading] = useState(false);
    useEffect(() => { // Get airlines
        if (airlineNameInput !== '') {
            setAirlinesLoading(true);
            API.airlines.get({ limit: 50, page: 1, name: airlineNameInput })
                .then(response => {
                    setAirlines(response.data.data ?? [])
                })
                .catch(error => {
                    console.log(error)
                })
                .finally(() => {
                    setAirlinesLoading(false)
                })
        }
    }, [airlineNameInput]);


    function refreshFlights() { // Refresh flights
        setLoading(true);
        var forceAirline = {};
        if (onlyMine) {
            forceAirline.airline = login.entity_id;
        }
        API.flights.get({ limit: 10, page: flightPage ?? 1, ...filters, ...forceAirline })
            .then(response => {
                setFlights(response.data?.data ?? []);
                setPagination(response.data?.pagination ?? []);
            })
            .catch(error => {
                setFlightsError(error.response.data);
            })
            .finally(() => {
                setLoading(false);
            })
    }

    function handleFilter(e) {
        e.preventDefault();
        e.stopPropagation();
        refreshFlights();
    }

    function handleOnlyMine(e){
        if(e.target.checked){
            setOnlyMine(true);
        }else{
            setOnlyMine(false);
        }
    }
    useEffect(()=> refreshFlights(), [onlyMine])

    useEffect(() => { // Modify filters
        var tempFilters = {
            origin: selectedOrigin[0]?.id,
            destination: selectedDestination[0]?.id,
            date: selectedDate?.target.value,
            airline: selectedAirline[0]?.id
        }

        for (var key in tempFilters) {
            if (tempFilters[key] === undefined) {
                delete tempFilters[key];
            }
        }

        setFilters(tempFilters)
    }, [selectedOrigin, selectedDestination, selectedAirline, selectedDate])

    const [activeKey, setActiveKey] = useState(null);
    const handleToggle = (e) => {
        e.stopPropagation();
        console.log(e)
        // setActiveKey( === eventKey ? null : eventKey);
    };

    return (
        <>
            <div className="flightPageContainer">
                <div className="flightPageFilters">
                    <Form>
                        <Row>
                            <h5>
                                Filter by
                            </h5>
                            <Form.Group as={Col}>
                                <Form.Label>Origin</Form.Label>
                                <Typeahead
                                    id="basic-typeahead-single"
                                    labelKey="name"
                                    onChange={setSelectedOrigin}
                                    options={countries}
                                    placeholder="Choose a country..."
                                    selected={selectedOrigin}
                                    isLoading={loadingCountries}
                                />
                            </Form.Group>
                            <Form.Group as={Col}>
                                <Form.Label>Destination</Form.Label>
                                <Typeahead
                                    id="basic-typeahead-single"
                                    labelKey="name"
                                    onChange={setSelectedDestination}
                                    options={countries}
                                    placeholder="Choose a country..."
                                    selected={selectedDestination}
                                    isLoading={loadingCountries}
                                />
                            </Form.Group>
                        </Row>
                        <Form.Group>
                            <Form.Label>Departure Date</Form.Label>
                            <Form.Control
                                type="date"
                                onChange={setSelectedDate}
                                defaultValue={filters.date ?? ""}
                            />
                        </Form.Group>
                        <Row>
                            <Form.Group>
                                <Form.Label>Airline Name</Form.Label>
                                <Typeahead
                                    id="remote-api-typeahead"
                                    labelKey="name" // replace 'name' with the key in your data objects
                                    onInputChange={(text) => setAirlineNameInput(text)}
                                    onChange={setSelectedAirline}
                                    options={airlines}
                                    placeholder="Start typing..."
                                    selected={selectedAirline}
                                    isLoading={airlinesLoading}
                                />
                            </Form.Group>
                            {
                                login.type === "airline" ?
                                <Form.Group>
                                    <Form.Check
                                        type="switch"
                                        id="mine-switch"
                                        label="Only show my flights"
                                        onChange={handleOnlyMine}
                                    />
                                </Form.Group> : <></>
                            }
                        </Row>
                        <Button variant="primary" type="submit" onClick={handleFilter}>Filter</Button>
                    </Form>
                </div>
                {
                    loading ? <h1>Loading...</h1> :
                        flights.length === 0 ? <h1>No flights found...</h1> : flights.map((flight, index) =>
                            <Flight flightData={flight} key={index} onClick={ handleToggle } />
                        )
                }
                {makePagination(pagination?.page, Math.ceil(pagination?.total / pagination?.limit), "/flights")}
            </div>
        </>
    );
}