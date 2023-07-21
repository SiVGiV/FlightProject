import axios from "axios";
import { BASE_URL } from "./config"

const API_URL = `${BASE_URL}api`

export default class API {
    // Admin endpoints
    static admin = {
        delete: (id) => axios.delete(`${API_URL}/admin/${id}`)
    }

    static admins = {
        get: ({ limit, page }) => axios.get(`${API_URL}/api/admins/`, {
            params: {
                limit: limit || "",
                page: page || ""
            }
        }),
        post: (params) => axios.post(`${API_URL}/api/admins/`, params),
    }

    // Country endpoints
    static country = {
        get: (id) => axios.get(`${API_URL}/country/${id}`)
    }
    static countries = {
        get: ({ limit, page }) => axios.get(`${API_URL}/api/countries/`, {
            params: {
                limit: limit || "",
                page: page || ""
            }
        }),
    }

    // Flight endpoints
    static flight = {
        get: (id) => axios.get(`${API_URL}/flight/${id}`),
        patch: (id, params) => axios.patch(`${API_URL}/flight/${id}`, params),
        delete: (id) => axios.delete(`${API_URL}/flight/${id}`),
    }

    static flights = {
        get: ({ origin, destination, date, page, limit }) => axios.get(`${API_URL}/flights/`, {
            params: {
                origin: origin || "",
                destination: destination || "",
                date: date || "",
                page: page || "",
                limit: limit || ""
            }
        }),
        post: (params) => axios.post(`${API_URL}/flights/`, params),
    }

    // Airlines endpoints
    static airline = {
        get: (id) => axios.get(`${API_URL}/airline/${id}`),
        patch: (id, params) => axios.patch(`${API_URL}/airline/${id}`, params),
        delete: (id) => axios.delete(`${API_URL}/airline/${id}`),
    }

    static airlines = {
        get: ({ name, limit, page }) => axios.get(`${API_URL}/airlines/`, {
            params: {
                name: name || "",
                limit: limit || "",
                page: page || ""
            }
        }),
        post: (params) => axios.post(`${API_URL}/airlines/`, params),
    }

    // Customers endpoints
    static customer = {
        get: (id) => axios.get(`${API_URL}/customer/${id}`),
        patch: (id, params) => axios.patch(`${API_URL}/customer/${id}`, params),
        delete: (id) => axios.delete(`${API_URL}/customer/${id}`),
    }

    static customers = {
        get: ({ limit, page }) => axios.get(`${API_URL}/customers/`, {
            params: {
                limit: limit || "",
                page: page || ""
            }
        }),
        post: (params) => axios.post(`${API_URL}/customers/`, params),
    }

    // Tickets endpoints
    static ticket = {
        delete: (id) => axios.delete(`${API_URL}/ticket/${id}`),
    }

    static tickets = {
        get: ({ limit, page }) => axios.get(`${API_URL}/tickets/`, {
            params: {
                limit: limit || "",
                page: page || ""
            }
        }),
        post: (params) => axios.post(`${API_URL}/tickets/`, params),
    }
}