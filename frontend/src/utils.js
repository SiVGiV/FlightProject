import React, { useState } from "react";
import { Pagination, Button } from "react-bootstrap";

export function formatDate(isoDate) {
    const dateObj = new Date(isoDate)
    return dateObj.toLocaleDateString("en-GB", {
        "hour": "numeric",
        "minute": "2-digit",
        "day": "numeric",
        "weekday": "long",
        "year": "numeric",
        "month": "short",
    })
}

export function makePagination(current, last, url) {
    const firstIndex = Math.max(1, current - 2);
    const lastIndex = Math.min(last, current + 2);
    const beginningEllipsis = firstIndex >= 2;
    const endEllipsis = lastIndex <= last - 1;

    var numberLinks = []
    for (var i = firstIndex; i <= lastIndex; i++) {
        numberLinks.push(i)
    }

    return (
        <div className="pagination">
            <Pagination size="lg">
                {(current > 2) ? <Pagination.First href={`${url}/1/`} /> : <></>}
                {(current >= 2) ? <Pagination.Prev href={`${url}/${current - 1}`} /> : <></>}
                {beginningEllipsis ? <Pagination.Ellipsis /> : <></>}
                {numberLinks.map((pageNum) => <Pagination.Item href={`${url}/${pageNum}/`} active={pageNum === current}>{pageNum}</Pagination.Item>)}
                {endEllipsis ? <Pagination.Ellipsis /> : <></>}
                {(current <= last - 1) ? <Pagination.Next href={`${url}/${current + 1}`} /> : <></>}
                {(current < last - 1) ? <Pagination.Last href={`${url}/${last}`} /> : <></>}
            </Pagination>
        </div>
    );

}


export function ValidationButton(props) {
    const { onClick, variant, text, disabled, children } = props;
    const [validate, setValidate] = useState(false);

    return !validate ?
        <Button disabled={ disabled } variant={variant} onClick={() => setValidate(true)}>{children ?? text}</Button> :
        (
            <div className="validationComponent">
                Are you sure?&nbsp;
                <Button variant="success" onClick={(e) => {setValidate(false); onClick(e)}}>Yes</Button>&nbsp;
                <Button variant="danger" onClick={() => setValidate(false)}>No</Button>
            </div>
        );
}


export function ParseErrorObjects(obj){
    var errors = [];
    if (typeof obj === 'string' || obj instanceof String){
        return [obj];
    }
    for (var key in obj){
        errors.push(...ParseErrorObjects(obj[key]));
    }
    return errors;
}