<template>
  <div id="app">
    <router-view />
    <div v-if="userIsLoggedIn">
      <Navbar />
    </div>
  </div>
</template>

<script>
import Navbar from "./components/Navbar.vue";

export default {
  name: "App",
  components: {
    Navbar,
  },
  created() {
    this.$store.dispatch("tryAutoSignIn");
  },
  computed: {
    userIsLoggedIn() {
      return this.$store.getters.userSite;
    },
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
