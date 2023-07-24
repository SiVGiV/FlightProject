import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Import components
import MyNavBar from './components/navigation/navbar';

// Import pages
import HomePage from './pages';
import FlightsPage from './pages/flights';
import AirlinesPage from './pages/airlines';


const homepage = {
    '/': 'Flight Project'
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
    }
}

function App() {
    return (
        <BrowserRouter>
            <MyNavBar homePage={ homepage } pages={ pages } login={undefined} />
            <Routes>
                { Object.values(pages).map((page, index) => RouteResolver(page, index)) }
            </Routes>
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
