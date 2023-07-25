import React, { useEffect, useState } from "react";
import Airline from "../components/airline";
import { Form } from "react-bootstrap";
import { useParams } from "react-router-dom";
import API from "../api";

import '../css/airlinesPage.css';


import { makePagination } from "../utils"

export default function AirlinesPage(){
    const [filters, setFilters] = useState({});
    
    const [loading, setLoading] = useState(true);
    const [airlines, setAirlines] = useState([]);
    const [airlinesError, setAirlinesError] = useState();
    
    const [pagination, setPagination] = useState();
    const { airlinesPage } = useParams();

    useEffect(()=>{ // Refresh airlines
        setLoading(true);
        API.airlines.get({limit: 20, page: airlinesPage ?? 1, ...filters})
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
                        <Form.Label>Filter by airline name:</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="Airline Name..."
                            onBlur={ (e) => {if (filters.name !== e.target.value){ setFilters({
                                ...filters,
                                name: e.target.value
                            })}} }
                        />
                    </Form>
                </div>
                {
                    loading ? <h1>Loading...</h1> : (
                        airlines.length === 0 ? <h1>No airlines found...</h1> : airlines.map( (airline, index) =>
                            <Airline airlineData={airline}/>
                        )
                    )
                }
                { makePagination(pagination.page, Math.ceil(pagination.total / pagination.limit), "/airlines") }
            </div>
        </>
    );
}