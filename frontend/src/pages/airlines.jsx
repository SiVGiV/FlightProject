import React, { useEffect, useState } from "react";
import Airline from "./airline";
import { Accordion, Form, Col, Row } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { Typeahead } from "react-bootstrap-typeahead";
import API from "../api";

import { makePagination } from "../utils"

export default function AirlinesPage(){
    const [filters, setFilters] = useState({});
    
    const [loading, setLoading] = useState(true);
    const [airlines, setAirlines] = useState([]);
    const [airlinesError, setAirlinesError] = useState();
    
    const [loadingCountries, setLoadingCountries] = useState(true)
    const [countries, setCountries] = useState([])

    const [pagination, setPagination] = useState();
    const { airlinesPage } = useParams();

    useEffect(()=>{ // Refresh airlines
        setLoading(true);
        API.airlines.get({limit: 10, page: airlinesPage ?? 1, ...filters})
        .then(response => {
            setAirlines(response.data.data ?? []);
            setPagination(response.data.pagination ?? []);
        })
        .catch(error => {
            setAirlinesError(error.response.data);
        })
        .finally(() => {
            setLoading(false);
        })
    }, [ airlinesPage, filters ]);

    if (loading){
        return (
            <h1> Loading... </h1>
        );
    }

    if (airlinesError){
        console.log("Error: " + airlinesError)
        return (
            <h1 style={{color: 'red'}}>{airlinesError ?? airlinesError.map((err) => <p>{err}</p>)}</h1>
        );
    }

    return (
        <>
            <div className="airlinesPageContainer">
                <div className="airlinesPageFilters">
                    <Form>
                            <Form.Control
                                type="text"
                                placeholder="Airline Name..."
                            />
                    </Form>
                </div>
                {
                    loading ? <h1>Loading...</h1> : (
                        <Accordion>
                            {
                                airlines.length === 0 ? <h1>No airlines found...</h1> : airlines.map( (airline, index) =>
                                    <Airline airlineData={airline}/>
                                )
                            }
                        </Accordion>
                    )
                }
                { makePagination(pagination.page, Math.ceil(pagination.total / pagination.limit), "/airlines") }
            </div>
        </>
    );
}