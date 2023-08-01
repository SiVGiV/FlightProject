import axios from "axios";
import Cookies from "js-cookie";
import { BASE_URL } from "./config"

const API_URL = `${BASE_URL}/api`

axios.defaults.xsrfHeaderName = "X-CSRFToken"
axios.defaults.xsrfCookieName = 'csrf_token'
axios.defaults.withCredentials = true

export default class API {
    // Auth endpoints
    static auth = {
        login: ({ username, password }) => axios.post(`${API_URL}/login/`,
            {
                'username': username,
                'password': password
            }
        ),
        logout: () => axios.post(`${API_URL}/logout/`, {}),
        whoami: () => axios.get(`${API_URL}/whoami/`, {}),
        csrf: () => axios.get(`${API_URL}/csrf/`, {}),
        refreshCsrf: () => {
            var csrfToken = Cookies.get('csrf_token');
            if (csrfToken !== undefined && csrfToken !== null && csrfToken !== '') {
                axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
            }
            else {
                API.auth.csrf().then(response => {
                    Cookies.set('csrf_token', response.data.data['CSRF-Token']);
                    axios.defaults.headers.common['X-CSRFToken'] = response.data.data['CSRF-Token'];
                    console.log('CSRF token set successfully: ' + axios.defaults.headers.common['X-CSRFToken'] + '!');
                }).catch(error => {
                    console.log(error);
                });
            }
        }
    }

    // Admin endpoints
    static admin = {
        delete: (id) => axios.delete(`${API_URL}/admin/${id}/`, {})
    }

    static admins = {
        get: ({ limit, page }) => axios.get(`${API_URL}/admins/`, {
            params: {
                limit: limit ?? undefined,
                page: page ?? undefined
            },
        }),
        post: (params) => axios.post(`${API_URL}/admins/`, params),
    }

    // Country endpoints
    static country = {
        get: (id) => axios.get(`${API_URL}/country/${id}/`)
    }

    static countries = {
        get: ({ limit, page }) => axios.get(`${API_URL}/countries/`, {
            params: {
                limit: limit ?? undefined,
                page: page ?? undefined
            }
        }),
    }

    // Flight endpoints
    static flight = {
        get: (id) => axios.get(`${API_URL}/flight/${id}/`),
        patch: (id, params) => axios.patch(`${API_URL}/flight/${id}/`, params),
        delete: (id) => axios.delete(`${API_URL}/flight/${id}/`),
    }

    static flights = {
        get: ({ origin, destination, date, page, limit }) => axios.get(`${API_URL}/flights/`, {
            params: {
                origin_country: origin ?? undefined,
                destination_country: destination ?? undefined,
                date: date ?? undefined,
                page: page ?? undefined,
                limit: limit ?? undefined
            }
        }),
        post: (params) => axios.post(`${API_URL}/flights/`, params),
    }

    // Airlines endpoints
    static airline = {
        get: (id) => axios.get(`${API_URL}/airline/${id}/`),
        patch: (id, params) => axios.patch(`${API_URL}/airline/${id}/`, params),
        delete: (id) => axios.delete(`${API_URL}/airline/${id}/`),
    }

    static airlines = {
        get: ({ name, limit, page }) => axios.get(`${API_URL}/airlines/`, {
            params: {
                name: name ?? undefined,
                limit: limit ?? undefined,
                page: page ?? undefined
            }
        }),
        post: (params) => axios.post(`${API_URL}/airlines/`, params),
    }

    // Customers endpoints
    static customer = {
        get: (id) => axios.get(`${API_URL}/customer/${id}/`),
        patch: (id, params) => axios.patch(`${API_URL}/customer/${id}/`, params),
        delete: (id) => axios.delete(`${API_URL}/customer/${id}/`),
    }

    static customers = {
        get: ({ limit, page }) => axios.get(`${API_URL}/customers/`, {
            params: {
                limit: limit ?? undefined,
                page: page ?? undefined
            }
        }),
        post: (params) => axios.post(`${API_URL}/customers/`, params),
    }

    // Tickets endpoints
    static ticket = {
        delete: (id) => axios.delete(`${API_URL}/ticket/${id}/`),
    }

    static tickets = {
        get: ({ limit, page }) => axios.get(`${API_URL}/tickets/`, {
            params: {
                limit: limit ?? undefined,
                page: page ?? undefined
            }
        }),
        post: (params) => axios.post(`${API_URL}/tickets/`, params),
    }
}

