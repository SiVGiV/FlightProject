import React, { useContext, useState, useEffect, useCallback } from "react";
import { LoginContext } from "../contexts/auth_contexts";
import { APIContext } from "../contexts/api_contexts";
import { Tabs, Tab, Button } from "react-bootstrap";
import "../css/usersPage.css";


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
                console.log(userType)
                console.log(res.data.data);
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
                        <UserList users={users} userType={"customers"} forceReload={forceReloadMethod} />}
            </Tab>
            <Tab eventKey="airlines" title="Airlines">
                {loading ? <></> :
                    error ? <></> :
                        <UserList users={users} userType={"airlines"} forceReload={forceReloadMethod} />}
            </Tab>
            <Tab eventKey="admins" title="Admins">
                {loading ? <></> :
                    error ? <></> :
                        <UserList users={users} userType={"admins"} forceReload={forceReloadMethod} />}
            </Tab>
        </Tabs>
    );
}


function UserList({ users, userType, forceReload }) {
    var userConverter;
    console.log(userType);
    console.log(users);
    switch (userType) {
        case "admins":
            userConverter = (user) => {return {
            type: "admin",
            userid: user?.id,
            name: user?.admin?.first_name + " " + user?.admin?.last_name,
            username: user?.username,
            email: user?.email,
            entityid: user?.admin?.id,
        }}
        break;
        case "airlines":
            userConverter = (user) => {return {
            type: "airline",
            userid: user?.id,
            name: user?.airline?.name,
            username: user?.username,
            email: user?.email,
            entityid: user?.airline?.id,
        }}
        break;
        case "customers":
            userConverter = (user) => {return {
            type: "customer",
            userid: user?.id,
            name: user?.customer?.first_name + " " + user?.customer?.last_name,
            username: user?.username,
            email: user?.email,
            entityid: user?.customer?.id,
        }}
        break;
        default:
            userConverter = (user) => {return {}}
            break;
    }

    

    return (
        <div className="userGrid">
                <>
                <div className="columnHeader column-1" >
                    User ID
                </div>
                <div className="columnHeader column-2" >
                    Username
                </div>
                <div className="columnHeader column-3" >
                    Name
                </div>
                <div className="columnHeader column-4">
                    E-Mail
                </div>
                <div className="columnHeader column-5">
                    {userType === "customers" ? "Customer" : userType === "admins" ? "Admin" : "Airline"} ID
                </div>
                <div className="columnHeader column-6">
                    Deactivate
                </div>

                {users.map((user, index) =>
                    <User profile={userConverter(user)} forceReload={forceReload} key={index} />
                )}
                </>
        </div>
    );
}

function User({ profile, forceReload }) {
    const handleCancel = useCallback(() => { }, []);
    const login = useContext(LoginContext);
    // TODO
    return (
        <>
            <div className="userItem column-1" >
                {profile.userid}
            </div>
            <div className="userItem column-2" >
                {profile.username}
            </div>
            <div className="userItem column-3" >
                {profile.name}
            </div>
            <div className="userItem column-4">
                {profile.email}
            </div>
            <div className="userItem column-5">
                {profile.entityid}
            </div>
            <div className="userItem column-6">
                <Button onClick={handleCancel} variant="danger" disabled={login.id === profile.userid}>Deactivate</Button>
            </div>
        </>
    );
}