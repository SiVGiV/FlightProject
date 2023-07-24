import React, { useEffect, useState } from "react";
import API from "../api";
import { BASE_URL } from "../config";


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
    }, [ airlineData ]);
    
    return (
        loadingData ? <div>Loading airline...</div> : <>
            <div className="airlineHeaderDiv">
                <div className="airlineListing">
                    <img src={country ? BASE_URL + country.flag : ""} alt=""/>
                    <div className="airlineName">{ airlineData.name }</div>
                </div>
            </div>
        </>
    );
}
