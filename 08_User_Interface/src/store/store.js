// store/index.js

import Vue from "vue";
import Vuex from "vuex";
import axios_services from '../axios-services.js'

Vue.use(Vuex);

export default new Vuex.Store({
    state: {
        auth: {
            access_token: null,
            refresh_token: null,
            client_id: null,
            client_secret: null,
        },
        userSite: false,
    },
    getters: {
        accessToken: state => {
            return state.access_token;
        },
        userData: state => {
            return state.user;
        },
        name: state => {
            return state.user.first_name + ' ' + state.user.last_name;
        },
        isAuthenticated: state => {
            return state.auth.access_token != null;
        },
        userSite: state => {
            return state.userSite;
        },
        clientID: state => {
            return state.auth.client_id;
        }

    },
    mutations: {
        authUser(state, userData) {
            state.auth.access_token = userData.access_token;
            state.auth.refresh_token = userData.refresh_token;
            state.auth.client_id = userData.client_id;
            state.auth.client_secret = userData.client_secret;
            axios_services.defaults.headers.common['Authorization'] = 'Bearer ' + userData.access_token;
        },
        changeUserSite(state, userSite) {
            state.userSite = userSite;
        },
        clearData(state) {
            for (var prop in state.auth) {
                state.auth[prop] = null;
            }
        },
    },
    actions: {
        setLogoutTimer({ commit }, expirationDate) {
            console.log(expirationDate);
            setTimeout(() => {
                commit('clearData');
            }, 86400000)
        },
        signin({ commit, dispatch }, authData) {
            console.log(process.env)
            return new Promise((resolve, reject) => {
                axios_services.post("/auth/login", authData)
                    .then(response => {
                        commit('authUser', {
                            access_token: response.data.access_token,
                            refresh_token: response.data.refresh_token,
                            client_id: response.data.client_id,
                            client_secret: response.data.client_secret,
                        })
                        const now = new Date();
                        const expirationDate = new Date(now.getTime() + response.data.expires_in * 1000);
                        localStorage.setItem('access_token', response.data.access_token);
                        localStorage.setItem('expirationDate', expirationDate);
                        localStorage.setItem('refresh_token', response.data.refresh_token);
                        localStorage.setItem('client_id', response.data.client_id);
                        localStorage.setItem('client_secret', response.data.client_secret);
                        dispatch('setLogoutTimer', expirationDate);
                        resolve(response);
                    })
                    .catch(error => {
                        reject(error);
                    })
            })
        },
        tryAutoSignIn({ commit, dispatch }) {
            const token = localStorage.getItem('access_token')
            console.log("tryAutoSignIn")
            if (!token) {
                console.log("No Token found");
                return;
            }
            const expirationDate = new Date(localStorage.getItem('expirationDate'));
            const now = new Date();
            if (now >= expirationDate) {
                console.log("Token expired");
                return;
            }
            console.log(localStorage.getItem('access_token'));
            commit('authUser', {
                access_token: localStorage.getItem('access_token'),
                refresh_token: localStorage.getItem('refresh_token'),
                client_id: localStorage.getItem('client_id'),
                client_secret: localStorage.getItem('client_secret'),
            });
            dispatch('setLogoutTimer', expirationDate);
        },
    }
});
