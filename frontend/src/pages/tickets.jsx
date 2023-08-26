import React, { useState, useContext, useEffect } from "react";
import { LoginContext } from "../contexts/auth_contexts";
import { APIContext } from "../contexts/api_contexts";
import "../css/ticketsPage.css";
import Ticket from "../components/Ticket";
import settings from "../settings";

export default function TicketsPage() {
    useEffect(() => {
        document.title = settings.base_title + settings.title_separator + "Tickets";
    }, []);

    const login = useContext(LoginContext);
    const API = useContext(APIContext);
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [forceReload, forceReloadMethod] = useState(0);

    useEffect(() => {
        setLoading(true);
        if (login.type !== "customer") {
            return;
        }
        API.tickets
            .get({ limit: 100, page: 1 })
            .then(res => {
                setTickets(res?.data?.data);
            })
            .catch(err => {
                setError(err?.response?.data);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [forceReload]);

    if (login.type !== "customer") {
        return <></>;
    }
    return loading ? (
        <h1>Loading...</h1>
    ) : error ? (
        <h1>Error: {error}</h1>
    ) : (
        <div className="ticketRowContainer">
            <h1>Tickets</h1>
            {tickets?.map((ticket, index) => (
                <Ticket
                    ticket={ticket}
                    key={index}
                    forceReload={forceReloadMethod}
                />
            ))}
        </div>
    );
}