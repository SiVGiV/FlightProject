import React, { useEffect, useState } from "react";
import { Accordion } from "react-bootstrap";

import API from "../api";
import { formatDate } from "../utils";
import { BASE_URL } from "../config";

// import '../css/airlinesPage.css';

export default function Flight({airlineData}){

    const [country, setCountry] = useState();
    const [loadingData, setLoadingData] = useState(true);

    useEffect(()=>{
        setLoadingData(true)
        Promise.all([
            API.country.get(airlineData.country),
        ]).then(([countryResponse]) => {
            setCountry(countryResponse.data.data);
        }).catch(error => {
            console.log(error.data)
        }).finally(() => {
            setLoadingData(false)
        })
    }, [ airlineData ])
    
    return (
            loadingData ? <div>Loading airline...</div> : <>
                <div className="airlineHeaderDiv">
                    <div className="airlineListing">
                        <div className="country">
                            <img src={country ? BASE_URL + country.flag : ""} alt=""/>
                            <div className="airlineName">{ airlineData.name }</div>
                        </div>
                    </div>
                </div>
            </>
    );
}
