<template>
  <!-- Title Box -->
  <div id="login" class="container">
    <section class="jumbotron text-center">
      <div class="container">
        <h1 class="jumbotron-heading">{{ PageTitle }}</h1>
      </div>
    </section>

    <!-- Login Form -->
    <b-card class="card">
      <p class="p">Enter your CLC+ Backbone credentials to login</p>
      <b-alert v-model="showAlert" variant="danger" dismissible
        >Email or password are wrong!</b-alert
      >
      <b-form @submit.prevent="onSubmit">
        <b-form-group id="input-group-1" label="Email:" label-for="input-1">
          <b-form-input
            id="input-1"
            v-model="form.email"
            type="email"
            required
            placeholder="Enter email"
            v-bind:class="{ pwalert: showAlert }"
          ></b-form-input>
        </b-form-group>
        <b-form-group id="input-group-2" label="Password:" label-for="input-2">
          <b-form-input
            id="input-2"
            v-model="form.password"
            type="password"
            required
            v-bind:class="{ pwalert: showAlert }"
          ></b-form-input>
        </b-form-group>

        <b-button type="submit" block>Submit</b-button>
      </b-form>
    </b-card>
  </div>
</template>

<script>
export default {
  name: "Login",
  data() {
    return {
      PageTitle: "Login",
      form: {
        email: "",
        password: "",
      },
      showAlert: false,
    };
  },
  methods: {
    onSubmit() {
      const formData = {
        email: this.form.email,
        password: this.form.password,
      };
      this.$store.dispatch("signin", formData).then(
        (response) => {
          console.log(response);
          this.$router.push(this.$route.query.redirect || "/");
        },
        (error) => {
          console.log(error);
          this.showAlert = true;
        }
      );
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
