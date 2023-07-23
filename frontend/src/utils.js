import { Pagination } from "react-bootstrap";

export function formatDate(isoDate){
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

export function makePagination(current, last, url){
    const firstIndex = Math.max(1, current - 2);
    const lastIndex = Math.min(last, current + 2);
    const beginningEllipsis = firstIndex >= 2;
    const endEllipsis = lastIndex <= last - 1;

    var numberLinks = []
    for (var i = firstIndex; i <= lastIndex; i++){
        numberLinks.push(i)
    }

    return (
        <div className="pagination">
            <Pagination size="lg">
                { (current > 2 ) ? <Pagination.First href={ `${url}/1/` }/> : <></>}
                { (current >= 2) ? <Pagination.Prev href={ `${url}/${current - 1}` }/> : <></>}
                { beginningEllipsis ? <Pagination.Ellipsis/> : <></>}
                { numberLinks.map( (pageNum)=><Pagination.Item href={ `${url}/${pageNum}/` } active={ pageNum === current}>{ pageNum }</Pagination.Item> ) }
                { endEllipsis ? <Pagination.Ellipsis/> : <></>}
                { (current <= last - 1) ? <Pagination.Next href={ `${url}/${current + 1}` }/> : <></>}
                { (current < last - 1) ? <Pagination.Last href={ `${url}/${last}` }/> : <></>}
            </Pagination>
        </div>
    );

}