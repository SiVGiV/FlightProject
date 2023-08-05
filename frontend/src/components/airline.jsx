import React, { useEffect, useState } from "react";
import { useContext } from "react";
import { APIContext } from '../contexts/api_contexts';


export default function Flight({airlineData}){
    const API = useContext(APIContext);
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
                    <img src={country ? API.BASE_URL + "/" + country.flag : ""} alt=""/>
                    <div className="airlineName">{ airlineData.name }</div>
                </div>
            </div>
        </>
    );
}
