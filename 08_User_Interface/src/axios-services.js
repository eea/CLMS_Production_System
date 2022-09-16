import axios from 'axios'
import store from './store/store.js'

console.log("VUE_API_URL:", process.env.VUE_APP_API_URL);

const axios_services = axios.create({
    //baseURL: process.env.VUE_APP_API_URL
    baseURL: 'https://api.clcplusbackbone.geoville.com/v1'
})

axios_services.interceptors.request.use(function (config) {
    let key = 'Bearer ' + store.state.auth.access_token;
    config.headers.Authorization = key;
    return config;
}, function (error) {
    return Promise.reject(error);
});

export default axios_services

