import React, { useContext, useState, useEffect } from "react";
import { LoginContext } from "../contexts/auth_contexts";
import { APIContext } from "../contexts/api_contexts";
import { Tabs, Tab, Spinner } from "react-bootstrap";
import { ValidationButton } from "../utils";
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
        <>
            <Tabs
                id="uncontrolled-tab-example"
                className="mb-3"
                activeKey={userType}
                onSelect={(k) => setUserType(k)}
            >
                <Tab eventKey="customers" title="Customers">
                    {loading ? <div style={{ display: "flex", justifyContent: "center", padding: "50px" }}><Spinner animation="border" /></div> :
                        error ? <></> :
                            <UserList users={users} userType={"customers"} forceReload={forceReloadMethod} />}
                </Tab>
                <Tab eventKey="airlines" title="Airlines">
                    {loading ? <div style={{ display: "flex", justifyContent: "center", padding: "50px" }}><Spinner animation="border" /></div> :
                        error ? <></> :
                            <UserList users={users} userType={"airlines"} forceReload={forceReloadMethod} />}
                </Tab>
                <Tab eventKey="admins" title="Admins">
                    {loading ? <div style={{ display: "flex", justifyContent: "center", padding: "50px" }}><Spinner animation="border" /></div> :
                        error ? <></> :
                            <UserList users={users} userType={"admins"} forceReload={forceReloadMethod} />}
                </Tab>
            </Tabs>
        </>
    );
}


function UserList({ users, userType, forceReload }) {
    var userConverter;
    switch (userType) {
        case "admins":
            userConverter = (user) => {
                return {
                    type: "admin",
                    userid: user?.id,
                    name: user?.admin?.first_name + " " + user?.admin?.last_name,
                    username: user?.username,
                    email: user?.email,
                    entityid: user?.admin?.id,
                    is_active: user?.is_active,
                }
            }
            break;
        case "airlines":
            userConverter = (user) => {
                return {
                    type: "airline",
                    userid: user?.id,
                    name: user?.airline?.name,
                    username: user?.username,
                    email: user?.email,
                    entityid: user?.airline?.id,
                    is_active: user?.is_active,
                }
            }
            break;
        case "customers":
            userConverter = (user) => {
                return {
                    type: "customer",
                    userid: user?.id,
                    name: user?.customer?.first_name + " " + user?.customer?.last_name,
                    username: user?.username,
                    email: user?.email,
                    entityid: user?.customer?.id,
                    is_active: user?.is_active,
                }
            }
            break;
        default:
            userConverter = (user) => { return {} }
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

function User({ profile }) {
    const [active, setActive] = useState(profile.is_active);
    const API = useContext(APIContext);
    const handleCancel = () => {
        switch (profile.type) {
            case "admin":
                API.admin.delete(profile.entityid)
                    .then((res) => {
                        setActive(false);
                    })
                    .catch((err) => {
                        console.log(err.response.data.error);
                    })
                break;
            case "airline":
                API.airline.delete(profile.entityid)
                    .then((res) => {
                        setActive(false);
                    })
                    .catch((err) => {
                        console.log(err.response.data.error);
                    })
                break;
            case "customer":
                API.customer.delete(profile.entityid)
                    .then((res) => {
                        setActive(false);
                    })
                    .catch((err) => {
                        console.log(err.response.data.error);
                    })
                break;
            default:
                break;
        }
    }
    const login = useContext(LoginContext);
    return (
        <>
            <div className={"userItem column-1" + (!active ? " cancelled" : "")}>
                {profile.userid}
            </div>
            <div className={"userItem column-2" + (!active ? " cancelled" : "")}>
                {profile.username}
            </div>
            <div className={"userItem column-3" + (!active ? " cancelled" : "")}>
                {profile.name}
            </div>
            <div className={"userItem column-4" + (!active ? " cancelled" : "")}>
                {profile.email}
            </div>
            <div className={"userItem column-5" + (!active ? " cancelled" : "")}>
                {profile.entityid}
            </div>
            <div className={"userItem column-6" + (!active ? " cancelled" : "")}>
                <ValidationButton onClick={handleCancel} variant="danger" disabled={login.id === profile.userid || !active} text="Deactivate" />
            </div>
        </>
    );
}