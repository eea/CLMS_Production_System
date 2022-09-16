<template>
  <div id="automatic" class="container">
    <!-- Title Box -->
    <section class="jumbotron text-center">
      <div class="container">
        <h1 class="jumbotron-heading">{{ PageTitle }}</h1>
      </div>
    </section>

    <!-- Filtering -->
    <div class="row">
      <div class="col-sm">
        <b-form-textarea
          :id="columns[0].label"
          size="xs"
          :placeholder="columns[0].label"
          v-model="spu"
        ></b-form-textarea>
      </div>
      <div class="col-sm">
        <b-form-textarea
          :id="columns[1].label"
          size="xs"
          :placeholder="columns[1].label"
          v-model="pcu"
        ></b-form-textarea>
      </div>
      <div class="col-sm">
        <b-form-select
          v-model="selected_service"
          :options="services"
        ></b-form-select>
      </div>
      <div class="col-sm">
        <b-form-select
          v-model="selected_status"
          :options="stati"
        ></b-form-select>
      </div>
    </div>
    <div class="row">
      <div class="col align-self-center underpad">
        <b-button class="w-100" v-on:click="Filter" variant="outline-primary">{{
          FilterButtonText
        }}</b-button>
      </div>
    </div>

    <!-- Button for starting a service & the appearing form -->
    <div class="d-flex mb-3">
      <div class="ml-auto p-2">
        <b-button variant="dark" v-b-modal.modal-prevent-closing>{{
          StartButtonText
        }}</b-button>

        <b-modal
          id="modal-prevent-closing"
          ref="modal"
          :title="StartButtonText"
          @show="resetModal"
          @hidden="resetModal"
          @ok="handleOk"
          ok-title="Submit"
        >
          <form ref="form" @submit.stop.prevent="handleSubmit">
            <b-form-group
              :label="UnitLabel"
              label-for="unit-input"
              :invalid-feedback="UnitFeedback"
              :state="unitState"
            >
              <b-form-input
                id="unit-input"
                v-model="unit"
                :state="unitState"
                required
              ></b-form-input>
            </b-form-group>

            <b-form-group
              :label="ServiceLabel"
              :invalid-feedback="ServiceFeedback"
              :state="nameState"
            >
              <b-form-select
                v-model="selected_service_start"
                :options="services"
                :state="nameState"
                required
              ></b-form-select>
            </b-form-group>

            <b-form-group
              :invalid-feedback="parameter + ' required'"
              v-for="parameter in Object.keys(payload[selected_service_start])"
              :key="parameter"
              :label="parameter"
              :state="payload[selected_service_start][parameter]['State']"
            >
              <b-form-input
                v-model="payload[selected_service_start][parameter]['Current']"
                :state="payload[selected_service_start][parameter]['State']"
                :required="
                  payload[selected_service_start][parameter]['Required']
                "
              ></b-form-input>
            </b-form-group>
          </form>
        </b-modal>
      </div>
    </div>

    <!-- Table View -->
    <div class="row">
      <b-table
        responsive
        striped
        hover
        class="align-middle"
        head-variant="null"
        :items="table_items"
        :fields="columns"
      >
      </b-table>
    </div>
  </div>
</template>

<script>
import axios_services from "../axios-services";
import store from "../store/store.js";

export default {
  name: "AutomaticServices",
  data() {
    return {
      PageTitle: "Automatic Services",
      FilterButtonText: "Filter",
      StartButtonText: "Start an automatic service",
      UnitLabel: "Units (comma separated Processing or Subprocessing Unit)",
      UnitFeedback: "Units are required",
      ServiceLabel: "Service Name",
      ServiceFeedback: "Service Name is required",
      table_items: [],
      columns: [
        {
          key: "subproduction_unit",
          class: "align-middle",
          label: "Sub-Production Unit",
        },
        {
          key: "processing_unit",
          class: "align-middle",
          label: "Processing Unit",
        },
        { key: "service_name", class: "align-middle", label: "Service Name" },
        {
          key: "order_status",
          class: "align-middle",
          label: "Order Status",
        },
        { key: "order_id", class: "align-middle", label: "Order ID" },
        {
          key: "order_json",
          class: "align-middle",
          label: "Order Json",
        },
        { key: "order_result", class: "align-middle", label: "Result" },
      ],
      services: [{ value: null, text: "Please select a Service" }],
      stati: [
        { value: null, text: "Please select an Order Status" },
        { value: "Not started", text: "Not Started" },
        { value: "In progress", text: "In Progress" },
        { value: "Finished", text: "Finished" },
        { value: "Failed", text: "Failed" },
      ],
      selected_service: null,
      selected_status: null,
      spu: "",
      pcu: "",
      unitState: null,
      unit: "",
      nameState: null,
      selected_service_start: null,
      payload: {
        null: {},
        harmonics: {
          start_date: { State: null, Current: "", Required: true },
          end_date: { State: null, Current: "", Required: true },
          band: { State: null, Current: "", Required: true },
          resolution: { State: null, Current: "", Required: true },
          ndi_band: { State: null, Current: "", Required: false },
        },
        batch_classification_test: {
          ParamA: { State: null, Current: "", Required: true },
          ParamB: { State: null, Current: "", Required: false },
        },
      },
      service_units: {
        harmonics: "tile_id",
        batch_classification_test: "processing_unit",
      },
    };
  },
  methods: {
    checkFormValidity() {
      // check if the form is valid
      const valid = this.$refs.form.checkValidity();

      if (this.unit != "") {
        this.unitState = true;
      } else {
        this.unitState = false;
      }

      if (this.selected_service_start) {
        this.nameState = true;
      } else {
        this.nameState = false;
      }

      for (var param in this.payload[this.selected_service_start]) {
        if (
          this.payload[this.selected_service_start][param]["Current"] != "" ||
          !this.payload[this.selected_service_start][param]["Required"]
        ) {
          this.payload[this.selected_service_start][param]["State"] = true;
        } else {
          this.payload[this.selected_service_start][param]["State"] = false;
        }
      }

      return valid;
    },
    resetModal() {
      // empty values set inside the form after the form gets closed
      this.unit = "";
      this.unitState = null;
      this.nameState = null;
      for (var param in this.payload[this.selected_service_start]) {
        this.payload[this.selected_service_start][param]["Current"] = "";
        this.payload[this.selected_service_start][param]["State"] = null;
      }
      this.selected_service_start = null;
    },
    handleOk(bvModalEvt) {
      // Prevent modal from closing
      bvModalEvt.preventDefault();
      // Trigger submit handler
      this.handleSubmit();
    },
    handleSubmit() {
      // Exit when the form isn't valid
      if (!this.checkFormValidity()) {
        return;
      }

      // POST request loop (for each given unit)
      var units_array = this.unit.split(",");

      var post_req = "/services/" + this.selected_service_start;
      var payload_filled = {
        service_name: this.selected_service_start,
        user_id: store.state.auth.client_id,
      };
      for (var param in this.payload[this.selected_service_start]) {
        var current_val = this.payload[this.selected_service_start][param][
          "Current"
        ];
        if (current_val != "") {
          payload_filled[param] = current_val;
        }
      }

      for (var u = 0; u < units_array.length; u++) {
        var payload_filled_unit = Object.assign({}, payload_filled);
        payload_filled_unit[this.service_units[this.selected_service_start]] =
          units_array[u];
        axios_services
          .post(post_req, payload_filled_unit)
          .then((response) => {
            console.log(post_req);
            console.log(payload_filled_unit);
            console.log(response);
          })
          .catch((err) => {
            console.log(`Error: ${err}`);
          });
      }

      // Hide the modal manually
      this.$nextTick(() => {
        this.$bvModal.hide("modal-prevent-closing");
      });
    },
    Filter() {
      // GET filtered service orders

      var first_filter_set = false;
      var req = "/crm/services/order_query";

      // alert if two lists are provided
      if (this.spu.includes(",") || this.pcu.includes(",")) {
        alert(
          "For filtering, only one Sub-Production and Processing Unit can be filtered at a time."
        );
        return null;
      }

      this.table_items = [];

      // order status
      if (this.selected_status) {
        first_filter_set = true;
        req += "?order_status=" + encodeURIComponent(this.selected_status);
      }

      // service name
      if (this.selected_service) {
        if (first_filter_set) {
          req += "&";
        } else {
          req += "?";
          first_filter_set = true;
        }
        req += "service_name=" + this.selected_service;
      }

      // Sub-Processing Unit
      if (this.spu != "") {
        if (first_filter_set) {
          req += "&";
        } else {
          req += "?";
          first_filter_set = true;
        }
        req += "subproduction_unit=" + this.spu;
      }

      // Processing Unit
      if (this.pcu != "") {
        if (first_filter_set) {
          req += "&";
        } else {
          req += "?";
          first_filter_set = true;
        }
        req += "processing_unit=" + this.pcu;
      }

      // send GET request
      console.log(req);
      axios_services.get(req).then((response) => {
        console.log(response.data);
        var filtered_jobs = Object.keys(response.data["services"]).length;
        for (var i = 0; i < filtered_jobs; i++) {
          this.table_items.push(response.data["services"][i]);
        }
      });
      console.log(this.table_items);
    },
  },
  mounted() {
    // fill table items on page start with service orders which are currently running
    axios_services
      .get("/crm/services/order_query?order_status=In%20progress")
      .then((response) => {
        var running_jobs = Object.keys(response.data["services"]).length;
        for (var i = 0; i < running_jobs; i++) {
          this.table_items.push(response.data["services"][i]);
        }
      });

    // get all service names on page start
    axios_services.get("/crm/services").then((response) => {
      var number_of_services = Object.keys(response.data["services"]).length;
      for (var i = 0; i < number_of_services; i++) {
        var element = {
          value: response.data["services"][i]["service_name"],
          text: response.data["services"][i]["service_name"],
        };
        this.services.push(element);
      }
    });
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.underpad {
  margin-bottom: 75px;
  margin-top: 5px;
}
/* large devices */
@media (min-width: 1200px) {
  .container {
    max-width: 1400px;
  }
}
</style>
