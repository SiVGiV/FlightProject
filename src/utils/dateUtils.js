
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