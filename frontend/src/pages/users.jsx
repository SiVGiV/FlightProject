import React, { useContext, useState, useEffect, useCallback } from "react";
import { LoginContext } from "../contexts/auth_contexts";
import { APIContext } from "../contexts/api_contexts";
import { Tabs, Tab } from "react-bootstrap";


export default function UsersPage() {
    const login = useContext(LoginContext);
    const API = useContext(APIContext);
    const [userType, setUserType] = useState('customers');
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [forceReload, forceReloadMethod] = useState(0);


    useEffect(() => {
        setLoading(true);
        API.users.get(userType)
        .then((res) => {
            setUsers(res.data.data);
        })
        .catch((err) => {
            setError(err.response.data.error);
        })
        .finally(() => {
            setLoading(false);
        });
    }, [userType, forceReload]);

    if (login.type !== "admin") {
        return <></>;
    }

    return (
        <Tabs
            id="uncontrolled-tab-example"
            className="mb-3"
            activeKey={userType}
            onSelect={(k) => setUserType(k)}
        >
            <Tab eventKey="customers" title="Customers">
                {loading ? <></> :
                error ? <></> :
                <UserList users={users} forceReload={forceReloadMethod} />}
            </Tab>
            <Tab eventKey="airlines" title="Airlines">
                {loading ? <></> :
                error ? <></> :
                <UserList users={users} forceReload={forceReloadMethod} />}
            </Tab>
            <Tab eventKey="admins" title="Admins">
                {loading ? <></> :
                error ? <></> :
                <UserList users={users} forceReload={forceReloadMethod} />}
            </Tab>
        </Tabs>
    );
}


function UserList({ users, forceReload }) {
    // TODO

    return (
        <div className="userGrid">
            {
                users.map((user, index) =>
                    <div className="userRow">
                        <User profile={user} forceReload={forceReload} key={index} />
                    </div>
                )}
        </div>
    );
}

function User({ profile, forceReload }) {
    const handleCancel = useCallback(() => { }, []);
    // TODO
    return (
        <></>
    );
}