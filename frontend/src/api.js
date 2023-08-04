import axios from "axios";
import Cookies from "js-cookie";

axios.defaults.xsrfHeaderName = "X-CSRFToken"
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.withCredentials = true


export default class API {
    identity = undefined;
    BASE_URL = 'localhost:8000'
    API_URL = 'localhost:8000/api'
    constructor(base_url) {
        this.BASE_URL = base_url
        this.API_URL = base_url + "/api"
        this.auth.refreshCsrf();
    }

    // Auth endpoints
    auth = {
        login: ({ username, password }) => axios.post(`${this.API_URL}/login/`,
            {
                'username': username,
                'password': password
            })
            .then(response => {
                this.auth.refreshCsrf();
                return response;
            }),
        logout: () => axios.post(`${this.API_URL}/logout/`, {})
            .then(response => {
                this.auth.refreshCsrf();
                return response;
            }),
        whoami: () => axios.get(`${this.API_URL}/whoami/`, {}),
        refreshCsrf: () => {
            if (Cookies.get('csrftoken') === undefined) {
                axios.get(`${this.API_URL}/csrf/`, {})
                .then(response => {
                    console.log('CSRF token fetched successfully: ' + Cookies.get('csrftoken') + '!');
                }).catch(error => {
                    console.log(error);
                });
            }
            axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken');

        }
    }

    // Admin endpoints
    admin = {
        delete: (id) => axios.delete(`${this.API_URL}/admin/${id}/`, {})
    }

    admins = {
        get: ({ limit, page }) => axios.get(`${this.API_URL}/admins/`, {
            params: {
                limit: limit ?? undefined,
                page: page ?? undefined
            },
        }),
        post: (params) => axios.post(`${this.API_URL}/admins/`, params),
    }

    // Country endpoints
    country = {
        get: (id) => axios.get(`${this.API_URL}/country/${id}/`)
    }

    countries = {
        get: ({ limit, page }) => axios.get(`${this.API_URL}/countries/`, {
            params: {
                limit: limit ?? undefined,
                page: page ?? undefined
            }
        }),
    }

    // Flight endpoints
    flight = {
        get: (id) => axios.get(`${this.API_URL}/flight/${id}/`),
        patch: (id, params) => axios.patch(`${this.API_URL}/flight/${id}/`, params),
        delete: (id) => axios.delete(`${this.API_URL}/flight/${id}/`),
    }

    flights = {
        get: ({ origin, destination, date, airline, page, limit }) => axios.get(`${this.API_URL}/flights/`, {
            params: {
                origin_country: origin ?? undefined,
                destination_country: destination ?? undefined,
                date: date ?? undefined,
                airline: airline ?? undefined,
                page: page ?? undefined,
                limit: limit ?? undefined
            }
        }),
        post: (params) => axios.post(`${this.API_URL}/flights/`, params),
    }

    // Airlines endpoints
    airline = {
        get: (id) => axios.get(`${this.API_URL}/airline/${id}/`),
        patch: (id, params) => axios.patch(`${this.API_URL}/airline/${id}/`, params),
        delete: (id) => axios.delete(`${this.API_URL}/airline/${id}/`),
    }

    airlines = {
        get: ({ name, limit, page }) => axios.get(`${this.API_URL}/airlines/`, {
            params: {
                name: name ?? undefined,
                limit: limit ?? undefined,
                page: page ?? undefined
            }
        }),
        post: (params) => axios.post(`${this.API_URL}/airlines/`, params),
    }

    // Customers endpoints
    customer = {
        get: (id) => axios.get(`${this.API_URL}/customer/${id}/`),
        patch: (id, params) => axios.patch(`${this.API_URL}/customer/${id}/`, params),
        delete: (id) => axios.delete(`${this.API_URL}/customer/${id}/`),
    }

    customers = {
        get: ({ limit, page }) => axios.get(`${this.API_URL}/customers/`, {
            params: {
                limit: limit ?? undefined,
                page: page ?? undefined
            }
        }),
        post: (params) => axios.post(`${this.API_URL}/customers/`, params),
    }

    // Tickets endpoints
    ticket = {
        delete: (id) => axios.delete(`${this.API_URL}/ticket/${id}/`),
    }

    tickets = {
        get: ({ limit, page }) => axios.get(`${this.API_URL}/tickets/`, {
            params: {
                limit: limit ?? undefined,
                page: page ?? undefined
            }
        }),
        post: (params) => axios.post(`${this.API_URL}/tickets/`, params),
    }
}

