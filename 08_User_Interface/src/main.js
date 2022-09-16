import Vue from 'vue'
import App from './App.vue'
import VueRouter from 'vue-router';

// Add  dependencies
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import router from './router/router.js'

// Fontawsome
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faEdit, faFilter, faPlusCircle, faSearch } from '@fortawesome/free-solid-svg-icons'

// Store
import store from "./store/store.js";

library.add(faEdit);
library.add(faFilter);
library.add(faSearch);
library.add(faPlusCircle);

Vue.config.productionTip = false

Vue.component('font-awesome-icon', FontAwesomeIcon)

// Use components
Vue.use(BootstrapVue)
Vue.use(VueRouter);

new Vue({
  router,
  store,
  render: h => h(App),
}).$mount('#app')
