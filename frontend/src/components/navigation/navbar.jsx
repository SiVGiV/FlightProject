import Nav  from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar"
import NavDropdown from "react-bootstrap/NavDropdown"
import { Link } from "react-router-dom";


export default function MyNavBar({homePage, pages, login}){
    // pagesObject should contain 'name': 'url' pairs.
    // if instead of a URL the object contains more objects, then they shall be 'name': 'url' pairs for a dropdown menu.
    return (
        <Navbar expand="lg" sticky="top" className="bg-body-tertiary">
            <Navbar.Brand as={ Link } to={ Object.keys(homePage)[0] }>{ Object.values(homePage)[0] }</Navbar.Brand>

                { Object.entries(pages).map(([k, v], index) => resolvePage(k, v, index)) }
            
            <Nav className="ms-auto">
                { login }
            </Nav>
        </Navbar>
    );
}

function resolvePage(key, value, index){
    // Check for dropdowns first
    if (((typeof value == 'object')|| (value instanceof Object)) && (typeof Object.values(value)[0] == 'object')){
        return (
            <div className="navbar-item">
                <NavDropdown title={ key } key={ index }>
                    { Object.entries(value).map(([k, v], ind) => resolveDropdown(k, v, ind)) }
                </NavDropdown>
            </div>
        );
    }
    // Then normal items
    if (typeof value == 'object' || value instanceof Object){
        if (('navbar' in value) && (!value['navbar'])){
            return <></>;
        }
        return (<div className="navbar-item"><Nav.Link as={ Link } to={ value['link'] ?? value['url'] } key={ index }>{ key }</Nav.Link></div>);
    }
    return (<></>);
}

function resolveDropdown(key, value, index){
    if (typeof value == 'object' || value instanceof Object){
        return (<NavDropdown.Item as={ Link } to={ value['link'] ?? value['url'] } key={ index }>{ key }</NavDropdown.Item>);
    }
}