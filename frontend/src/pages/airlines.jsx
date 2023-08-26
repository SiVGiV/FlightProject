import React, { useEffect, useState, useContext, useCallback } from "react";
import Airline from "../components/airline";
import { Form, Spinner, Button } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { APIContext } from "../contexts/api_contexts";
import settings from "../settings";

import "../css/airlinesPage.css";

import { makePagination } from "../utilities/helpers";

export default function AirlinesPage() {
    useEffect(() => {
        document.title = settings.base_title + settings.title_separator + "Airlines";
    }, []);


    const API = useContext(APIContext);
    const [filters, setFilters] = useState({});

    const [loading, setLoading] = useState(true);
    const [airlines, setAirlines] = useState([]);
    const [airlinesError, setAirlinesError] = useState();

    const [pagination, setPagination] = useState();
    const { airlinesPage } = useParams();

    useEffect(() => {refreshAirlines()}, [airlinesPage]);

    const refreshAirlines = useCallback(() => {
        // Refresh airlines
        setLoading(true);
        API.airlines
            .get({ limit: 20, page: airlinesPage ?? 1, ...filters })
            .then(response => {
                setAirlines(response.data.data ?? []);
                setPagination(response.data.pagination ?? []);
            })
            .catch(error => {
                setAirlinesError(error.response.data);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [airlinesPage, filters])

    if (loading) {
        return (
            <div
                style={{
                    display: "flex",
                    justifyContent: "center",
                    padding: "50px",
                }}
            >
                <Spinner animation="border" />
            </div>
        );
    }

    if (airlinesError) {
        console.log("Error: " + airlinesError);
        return (
            <h1 style={{ color: "red" }}>
                {airlinesError ?? airlinesError.map(err => <p>{err}</p>)}
            </h1>
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
                            onChange={e => setFilters({ ...filters, name: e.target.value })}
                        />
                        <Button onClick={refreshAirlines}>Filter</Button>
                    </Form>
                </div>
                {loading ? (
                    <h1>Loading...</h1>
                ) : airlines.length === 0 ? (
                    <h1>No airlines found...</h1>
                ) : (
                    airlines.map((airline, index) => (
                        <Airline airlineData={airline} />
                    ))
                )}
                {makePagination(
                    pagination.page,
                    Math.ceil(pagination.total / pagination.limit),
                    "/airlines"
                )}
            </div>
        </>
    );
}
