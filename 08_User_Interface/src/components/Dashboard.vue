<template>
  <div id="Dashboard" class="container">
    <section class="jumbotron text-center">
      <div class="container">
        <h1 class="jumbotron-heading">{{ DashboardTitle }}</h1>
        <p class="lead text-muted">{{ DashboardText }}</p>
        <p>
          <b-button
            @click="changeToAutomatic"
            class=""
            variant="outline-secondary"
            size="lg"
            >{{ automatic }}</b-button
          >
          <b-button
            @click="changeToManual"
            class="ml-3"
            variant="outline-secondary"
            size="lg"
            >{{ manual }}</b-button
          >
        </p>
      </div>
    </section>
  </div>
</template>

<script>
import router from "./../router/router.js";

export default {
  name: "Dashboard",
  data() {
    return {
      DashboardTitle: "CLC+ Backbone",
      DashboardText:
        "Select whether you want to view and start automatic services or manual tasks.",
      automatic: "Automatic Services",
      manual: "Manual Tasks",
    };
  },
  methods: {
    changeToAutomatic() {
      router.push({ name: "AutomaticServices" });
    },
    changeToManual() {
      router.push({ name: "ManualTasks" });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#Dashboard {
  margin-top: 150px;
}
</style>
