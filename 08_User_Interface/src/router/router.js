import VueRouter from 'vue-router'
import store from '../store/store.js'

import Dashboard from './../components/Dashboard.vue'
import AutomaticServices from './../components/AutomaticServices2.vue'
import ManualTasks from './../components/ManualTask2.vue'
import Login from './../components/Login.vue'

export const routes = [
  {
    name: 'Dashboard', path: '/', component: Dashboard, meta: { requiresAuth: true, userSite: true }
  },
  { name: 'AutomaticServices', path: '/services', component: AutomaticServices, meta: { requiresAuth: true, userSite: true } },
  { name: 'ManualTasks', path: '/tasks', component: ManualTasks, meta: { requiresAuth: true, userSite: true } },
  { name: 'Login', path: '/login', component: Login, meta: { requiresAuth: false, userSite: true } }
]

const router = new VueRouter({
  mode: 'history',
  routes
})

store.dispatch("tryAutoSignIn");
router.beforeEach((to, from, next) => {
  if (!store.state.auth.access_token && to.meta.requiresAuth) {
    next({ path: '/login', query: { redirect: to } });
  }
  else if (to.meta.userSite) {
    store.commit('changeUserSite', true);
    next();
  }
  else {
    store.commit('changeUserSite', false);
    next();
  }

})


export default router
