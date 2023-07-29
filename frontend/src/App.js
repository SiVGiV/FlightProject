import 'bootstrap/dist/css/bootstrap.min.css';
import './css/universal.css'

import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Import components
import MyNavBar from './components/navigation/navbar';

// Import pages
import HomePage from './pages';
import FlightsPage from './pages/flights';
import AirlinesPage from './pages/airlines';
import RegisterPage from './pages/register';
import Welcome from './components/navigation/welcome';
import LoginPage from './pages/login';

import { BASE_URL } from './config';
import API from './api';



const homepage = {
    '/': <img src={`${BASE_URL}static/images/logo.png`} alt="Flight Project" className='logo'/>
}

const pages = {
    'Home': {
        'url': '/',
        'element': <HomePage/>,
        'navbar': false
    },
    'Flights': {
        'url': '/flights/:flightPage',
        'link': '/flights/1/',
        'element': <FlightsPage/>
    },
    'Airlines': {
        'url': '/airlines/:airlinePage',
        'link': '/airlines/1/',
        'element': <AirlinesPage/>
    },
    'Auth':{
        'Login': {
            'url': '/login/',
            'element': <LoginPage/>,
            'navbar': true
        },
        'Register': {
            'url': '/register/:userType/',
            'element': <RegisterPage/>,
            'link': '/register/customer/',
            'navbar': true
        }
    }
}


function App() {
    return (
        <BrowserRouter>
            <MyNavBar homePage={ homepage } pages={ pages } login={ <Welcome/>} />
            <div className='page-content'>
                <Routes>
                    { Object.values(pages).map((page, index) => RouteResolver(page, index)) }
                </Routes>
            </div>
        </BrowserRouter>
    );
}


function RouteResolver(page, index){
    if (('url' in page) && ('element' in page)){
        return (<Route key={index} path={ page['url'] } element={ page['element'] }/>);
    }
    if (typeof Object.values(page)[0] == 'object'){
        return (Object.values(page).map((p, ind) => <Route key={ ind } path={ p['url'] } element={ p['element'] }/>))
    }
}

export default App;
