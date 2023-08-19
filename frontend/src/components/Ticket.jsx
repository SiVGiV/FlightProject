import React, { useState, useContext, useEffect } from "react";
import { Spinner } from "react-bootstrap";
import { APIContext } from "../contexts/api_contexts";
import { ValidationButton } from "../../utilities/helpers";

export default function Ticket({ ticket, forceReload }) {
    const API = useContext(APIContext);
    const [flight, setFlight] = useState(null);
    const [origin, setOrigin] = useState(null);
    const [destination, setDestination] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        setError(null);
        API.flight
            .get(ticket.flight)
            .then(res => {
                setFlight(res?.data?.data);
                Promise.all([
                    API.country.get(res?.data?.data?.origin_country),
                    API.country.get(res?.data?.data?.destination_country),
                ])
                    .then(([originResponse, destinationResponse]) => {
                        setOrigin(originResponse?.data?.data);
                        setDestination(destinationResponse?.data?.data);
                        // console.log(originResponse);
                        setLoading(false);
                    })
                    .catch(err => {
                        // console.log(err);
                        setLoading(false);
                        setError(err?.response?.data);
                    });
            })
            .catch(err => {
                // console.log(err);
                setLoading(false);
                setError(err?.response?.data);
            });
    }, []);

    function handleCancel() {
        API.ticket
            .delete(ticket.id)
            .then(res => {
                alert("Ticket cancelled successfully.");
                forceReload(Math.random());
            })
            .catch(err => {
                alert(
                    "Error cancelling ticket: " + err?.response?.data?.message
                );
            });
    }
    console.log(ticket);

    return (
        <div
            className={"ticketRow" + (ticket.is_cancelled ? " cancelledTicketRow" : "")}
        >
            {loading ? (
                <div
                    style={{
                        display: "flex",
                        justifyContent: "center",
                        padding: "50px",
                    }}
                >
                    <Spinner animation="border" />
                </div>
            ) : error ? (
                <h3>Error: {error}</h3>
            ) : (
                <>
                    <div className="ticketIdField">#{ticket.id}</div>
                    <div className="ticketSeatField">
                        {ticket.seat_count} seat
                        {ticket.seat_count > 1 ? "s" : ""}
                    </div>
                    <div className="ticketOriginField">
                        <b>{origin.name}</b>
                        <div>
                            {new Date(flight.departure_datetime).toDateString()}
                        </div>
                    </div>
                    <div className="ticketDestinationField">
                        <b>{destination.name}</b>
                        <p>
                            {new Date(flight.arrival_datetime).toDateString()}
                        </p>
                    </div>
                    <ValidationButton
                        className="cancelTicketButton"
                        variant="danger"
                        disabled={ticket.is_cancelled}
                        onClick={handleCancel}
                    >
                        Cancel
                    </ValidationButton>
                </>
            )}
        </div>
    );
}
