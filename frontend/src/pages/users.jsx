import React, { useContext, useState, useEffect, useCallback } from "react";
import { LoginContext } from "../contexts/auth_contexts";
import { APIContext } from "../contexts/api_contexts";
import { Button, Tabs, Tab } from "react-bootstrap";


export default function UsersPage() {
    const login = useContext(LoginContext);
    const API = useContext(APIContext);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [forceReload, forceReloadMethod] = useState(0);


    if (login.type !== "admin") {
        return <></>;
    }
    return (
        <Tabs
            defaultActiveKey="customers"
            id="uncontrolled-tab-example"
            className="mb-3"
        >
            <Tab eventKey="customers" title="Customers">
                Tab content for Home
            </Tab>
            <Tab eventKey="airlines" title="Airlines">
                Tab content for Profile
            </Tab>
            <Tab eventKey="admins" title="Admins">
                Tab content for Contact
            </Tab>
        </Tabs>
    );
}

function User({ profile, forceReload }) {
    const API = useContext(APIContext);
    const [flight, setFlight] = useState(null);
    const [origin, setOrigin] = useState(null);
    const [destination, setDestination] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    
    const handleCancel = useCallback(() => {}, []);

    return (
        <div className={"profileRow" + (!profile.is_active ? " cancelledUserRow" : "")}>
            {
                (loading) ? <h3>Loading profile...</h3> :
                    (error) ? <h3>Error: {error}</h3> :
                        <>
                            <div className="profileIdField">#{profile.id}</div>
                            <div className="profileSeatField">{profile.seat_count} seat{profile.seat_count > 1 ? "s" : ""}</div>
                            <div className="profileOriginField">
                                <b>{origin.name}</b>
                                <div>{new Date(flight.departure_datetime).toDateString()}</div>
                            </div>
                            <div className="profileDestinationField">
                                <b>{destination.name}</b>
                                <p>{new Date(flight.arrival_datetime).toDateString()}</p>
                            </div>
                            <Button className="cancelUserButton" variant="danger" disabled={profile.is_cancelled} onClick={handleCancel}>Cancel</Button>
                        </>
            }
        </div>
    );
}