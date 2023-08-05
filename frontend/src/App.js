import 'bootstrap/dist/css/bootstrap.min.css';
import './css/universal.css'

import { Routes, Route, BrowserRouter } from 'react-router-dom';
import { useState } from 'react';

// Import components
import MyNavBar from './components/navigation/navbar';

// Import pages
import HomePage from './pages';
import FlightsPage from './pages/flights';
import AirlinesPage from './pages/airlines';
import TicketsPage from './pages/tickets';
import UsersPage from './pages/users';

import Welcome from './components/navigation/welcome';

import RegisterPage from './pages/register';
import LoginPage from './pages/login';

import { LoginContext, RefreshLoginContext } from './contexts/auth_contexts';
import { APIContext } from './contexts/api_contexts';
import API from './api';


const homepage = {
    '/': <img src={`${process.env.PUBLIC_URL}/logo.png`} alt="Flight Project" className='logo' />
}

const pages = {
    'Home': {
        'url': '/',
        'element': <HomePage />,
        'navbar': false
    },
    'Flights': {
        'url': '/flights/:flightPage',
        'link': '/flights/1/',
        'element': <FlightsPage />
    },
    'Airlines': {
        'url': '/airlines/:airlinePage',
        'link': '/airlines/1/',
        'element': <AirlinesPage />
    },
    'Tickets': {
        'url': '/tickets/',
        'element': <TicketsPage />,
        'onlyFor': 'customer'
    },
    'Users': {
        'url': '/users/',
        'element': <UsersPage />,
        'onlyFor': 'admin'
    },
    'Login': {
        'url': '/login/',
        'element': <LoginPage />,
        'navbar': false
    },
    'Register': {
        'url': '/register/',
        'element': <RegisterPage />,
        'navbar': false
    }
}

function App() {
    const [login, setLogin] = useState({});
    const APIClient = new API(process.env.BACKEND_URL ?? 'http://localhost:8000');

    function refreshLogin() {
        APIClient.auth.whoami().then(response => {
            setLogin(response.data.data)
        }).catch(error => {
            console.log("Error while refreshing identity: " + error);
        })
    }

    return (
        <BrowserRouter>

            <APIContext.Provider value={APIClient}>
                <LoginContext.Provider value={login}>
                    <RefreshLoginContext.Provider value={refreshLogin}>

                        <MyNavBar homePage={homepage} pages={pages} login={<Welcome />} />
                        <div className='page-content'>
                            <Routes>
                                {Object.values(pages).map((page, index) => RouteResolver(page, index))}
                            </Routes>
                        </div>

                    </RefreshLoginContext.Provider>
                </LoginContext.Provider>
            </APIContext.Provider>

        </BrowserRouter>
    );
}


function RouteResolver(page, index) {
    if (('url' in page) && ('element' in page)) {
        return (<Route key={index} path={page['url']} element={page['element']} />);
    }
    if (typeof Object.values(page)[0] == 'object') {
        return (Object.values(page).map((p, ind) => <Route key={ind} path={p['url']} element={p['element']} />))
    }
}

export default App;
