<template>
  <div>
    <b-navbar toggleable="md" class="navbar navbar-dark bg-dark fixed-top">
      <div class="container">
        <b-navbar-nav class="navbar-brand">
          <b-nav-item to="/">{{ NavbarTitle }}</b-nav-item>
        </b-navbar-nav>
        <b-navbar-toggle target="nav-collapse2"></b-navbar-toggle>
        <b-collapse id="nav-collapse2" is-nav>
          <!-- Right aligned nav items -->
          <b-navbar-nav class="ml-auto">
            <b-navbar-nav>
              <b-nav-item>
                <router-link
                  exact
                  class="nav-link"
                  :style="isClicked ? { 'font-weight': 'bold' } : null"
                  @click="toggleIsClicked"
                  :to="{ name: 'AutomaticServices' }"
                  >{{ automatic }}</router-link
                >
              </b-nav-item>
              <b-nav-item>
                <router-link
                  exact
                  class="nav-link"
                  :style="isClicked ? { 'font-weight': 'bold' } : null"
                  @click="toggleIsClicked"
                  :to="{ name: 'ManualTasks', params: { id: '' } }"
                  >{{ manual }}</router-link
                >
              </b-nav-item>
            </b-navbar-nav>
          </b-navbar-nav>
        </b-collapse>
      </div>
    </b-navbar>
  </div>
</template>

<script>
export default {
  components: {},
  data() {
    return {
      NavbarTitle: "CLC+ Backbone",
      automatic: "Automatic Services",
      manual: "Manual Tasks",
      isClicked: false,
    };
  },
  methods: {
    toggleIsClicked: function() {
      this.isClicked = !this.isClicked;
    },
  },
};
</script>

<style scoped>
@media (min-width: 1200px) {
  .container {
    max-width: 1400px;
  }
}

.router-link-active {
  color: white !important;
  font-weight: bold;
}

nav > a {
  font-weight: bold;
}
</style>
