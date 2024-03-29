import React, { useContext, useEffect } from "react";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import NavDropdown from "react-bootstrap/NavDropdown";
import { Link, useLocation } from "react-router-dom";
import {
    LoginContext,
    RefreshLoginContext,
} from "../contexts/auth_contexts";

export default function MyNavBar({ homePage, pages, login }) {
    const refreshLogin = useContext(RefreshLoginContext);
    const loginDetails = useContext(LoginContext);
    // pagesObject should contain 'name': 'url' pairs.
    // if instead of a URL the object contains more objects, then they shall be 'name': 'url' pairs for a dropdown menu.
    const location = useLocation();
    useEffect(() => {
        refreshLogin();
    }, [location]);

    return (
        <Navbar expand="lg" sticky="top" className="bg-body-tertiary">
            <Navbar.Brand as={Link} to={Object.keys(homePage)[0]}>
                {Object.values(homePage)[0]}
            </Navbar.Brand>

            {Object.entries(pages).map(([k, v], index) =>
                resolvePage(k, v, index, loginDetails)
            )}

            <Nav className="ms-auto">{login}</Nav>
        </Navbar>
    );
}

function resolvePage(key, value, index, loginDetails) {
    // Check for dropdowns first
    if (
        (typeof value == "object" || value instanceof Object) &&
        typeof Object.values(value)[0] == "object"
    ) {
        if (
            ("onlyFor" in value && value["onlyFor"] === loginDetails.type) ||
            !("onlyFor" in value)
        ) {
            return (
                <div className="navbar-item" key={index}>
                    <NavDropdown title={key} key={index}>
                        {Object.entries(value).map(([k, v], ind) =>
                            resolveDropdown(k, v, ind, loginDetails)
                        )}
                    </NavDropdown>
                </div>
            );
        }
    }
    // Then normal items
    if (typeof value == "object" || value instanceof Object) {
        if ("navbar" in value && !value["navbar"]) {
            return <></>;
        }
        if ("onlyFor" in value && value["onlyFor"] !== loginDetails.type) {
            return <></>;
        }
        return (
            <div className="navbar-item" key={index}>
                <Nav.Link
                    as={Link}
                    to={value["link"] ?? value["url"]}
                    key={index}
                >
                    {key}
                </Nav.Link>
            </div>
        );
    }
    return <></>;
}

function resolveDropdown(key, value, index, loginDetails) {
    if (typeof value == "object" || value instanceof Object) {
        if ("onlyFor" in value && value["onlyFor"] !== loginDetails.type) {
            return <></>;
        }
        return (
            <NavDropdown.Item
                as={Link}
                to={value["link"] ?? value["url"]}
                key={index}
            >
                {key}
            </NavDropdown.Item>
        );
    }
    return <></>;
}
