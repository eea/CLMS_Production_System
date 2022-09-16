<template>
  <div id="manual" class="container">
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
      <div class="col-sm">
        <b-form-select v-model="selected_task" :options="tasks"></b-form-select>
      </div>
      <div class="col-sm">
        <b-form-select
          v-model="selected_task_status"
          :options="task_stati"
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

    <div class="d-flex mb-3">
      <div class="ml-auto p-2">
        <!-- Button for starting a service & the appearing form -->
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
              label-for="unittype-input"
              :invalid-feedback="UnittypeFeedback"
              :state="unittypeState"
            >
              <b-form-select
                id="unittype-input"
                v-model="start_unit_type"
                :options="unit_options"
                :state="unittypeState"
                required
              ></b-form-select>
            </b-form-group>

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
              :label="TaskLabel"
              :invalid-feedback="TaskFeedback"
              :state="taskState"
            >
              <b-form-select
                v-model="selected_task_start"
                :options="tasks"
                :state="taskState"
                required
              ></b-form-select>
            </b-form-group>

            <b-form-group
              :label="OrderIdLabel"
              label-for="orderid-input"
              :invalid-feedback="OrderIdFeedback"
              :state="OrderIdState"
            >
              <b-form-input
                id="orderid-input"
                v-model="order_id"
                :state="OrderIdState"
                :required="tasks_mapper[selected_task_start]['oid_required']"
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
        <template v-slot:cell(edit)="row">
          <div class="float-right btn-group-nowrap">
            <b-button
              size="sm"
              variant="secondary"
              v-b-modal.task-modal-prevent-closing
              ><font-awesome-icon :icon="['fa', 'edit']" />&nbsp;&nbsp;{{
                EditButtonText
              }}</b-button
            >
            <!-- Edit Form -->
            <b-modal
              id="task-modal-prevent-closing"
              ref="modal"
              :title="EditButtonText"
              @show="resetEditModal"
              @hidden="resetEditModal"
              @ok="handleEditOk($event, row.item)"
              ok-title="Submit"
            >
              <form
                ref="form"
                @submit.stop.prevent="handleEditSubmit(row.item)"
              >
                <b-form-group :label="columns[1]['label'] + ':'">
                  {{ row.item["processing_unit"] }}</b-form-group
                >
                <b-form-group :label="ServiceLabel + ':'">{{
                  row.item["service_name"]
                }}</b-form-group>
                <b-form-group :label="TaskLabel + ':'">{{
                  row.item["task_name"]
                }}</b-form-group>

                <b-form-group
                  :label="TaskStateLabel"
                  :invalid-feedback="TaskStateFeedback"
                  :state="edittaskStateState"
                >
                  <b-form-select
                    v-model="state_to_edit"
                    :options="task_stati"
                    :state="edittaskStateState"
                    required
                  ></b-form-select>
                </b-form-group>
                <b-form-group
                  :label="ResultLabel"
                  v-if="state_to_edit == 'Finished'"
                  label-for="result-input"
                  :invalid-feedback="ResultFeedback"
                  :state="resultState"
                >
                  <b-form-input
                    id="result-input"
                    v-model="result_to_edit"
                    :state="resultState"
                    required
                  ></b-form-input>
                </b-form-group>
              </form>
            </b-modal>
          </div>
        </template>
      </b-table>
    </div>
  </div>
</template>

<script>
import axios_services from "../axios-services";
import store from "../store/store.js";

export default {
  name: "ManualTasks",
  data() {
    return {
      PageTitle: "Manual Tasks",
      FilterButtonText: "Filter",
      StartButtonText: "Start a manual task",
      EditButtonText: "Edit",
      UnitLabel: "Units (comma separated Processing or Subprocessing Unit)",
      UnitFeedback: "Units are required",
      ServiceLabel: "Service Name",
      TaskLabel: "Task Name",
      TaskFeedback: "Task Name is required",
      ServiceFeedback: "Service Name is required",
      OrderIdLabel: "Based on Order-ID",
      OrderIdFeedback: "Order-ID is required for this manual Task",
      TaskStateLabel: "Task Status",
      TaskStateFeedback: "Task Status is required",
      ResultFeedback:
        "The path to the result is required when setting a task to finished",
      ResultLabel: "Result Path",
      UnittypeFeedback: "Unit type is required",
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
          key: "task_name",
          class: "align-middle",
          label: "Task Name",
        },
        {
          key: "task_status",
          class: "align-middle",
          label: "Task Status",
        },
        { key: "task_result", class: "align-middle", label: "Task Result" },
        { key: "edit", class: "align-middle", label: "" },
      ],
      services: [{ value: null, text: "Please select a Service" }],
      tasks: [{ value: null, text: "Please select a Task" }],
      stati: [
        { value: null, text: "Please select an Order Status" },
        { value: "Not started", text: "Not Started" },
        { value: "In progress", text: "In Progress" },
        { value: "Finished", text: "Finished" },
        { value: "Failed", text: "Failed" },
      ],
      task_stati: [
        { value: null, text: "Please select a Task Status" },
        { value: "Not started", text: "Not Started" },
        { value: "In progress", text: "In Progress" },
        { value: "Finished", text: "Finished" },
        { value: "Failed", text: "Failed" },
      ],
      selected_service: null,
      selected_task: null,
      selected_status: null,
      selected_task_status: null,
      spu: "",
      pcu: "",
      unitState: null,
      unit: "",
      nameState: null,
      taskState: null,
      order_id: "",
      OrderIdState: null,
      selected_service_start: null,
      selected_task_start: null,
      start_unit_type: null,
      editstateState: null,
      resultState: null,
      edittaskStateState: null,
      unittypeState: null,
      unit_options: [
        { text: "Please select a Unit Type", value: null },
        { text: "Sub-Production Unit", value: "subproduction_unit" },
        { text: "Processing Unit", value: "processing_unit" },
      ],
      services_mapper: { null: "" },
      tasks_mapper: { null: { id: "", oid_required: false } },
      state_to_edit: "",
      result_to_edit: "",
    };
  },
  methods: {
    Edit(item) {
      // Edit Function (POST Request)
      var payload_edit = {
        processing_unit: item["processing_unit"],
        service_id: this.services_mapper[item["service_name"]],
        task_id: this.tasks_mapper[item["task_name"]],
        client_id: store.state.auth.client_id,
      };

      if (this.state_to_edit != "") {
        payload_edit["state"] = this.state_to_edit;
      }

      if (this.result_to_edit != "") {
        payload_edit["result"] = this.result_to_edit;
      }

      axios_services
        .post("/crm/manual_tasks/update", payload_edit)
        .then((response) => {
          console.log(payload_edit);
          console.log(response);
          return true;
        })
        .catch((err) => {
          console.log(`Error: ${err}`);
          return false;
        });
    },
    checkEditFormValidity() {
      // check if the form is valid
      const valid = this.$refs.form.checkValidity();
      if (this.state_to_edit != "") {
        this.editstateState = true;
        if ((this.state_to_edit == "Finished") & (this.result_to_edit != "")) {
          this.resultState = true;
        } else {
          this.resultState = false;
        }
      } else {
        this.editstateState = false;
      }

      return valid;
    },
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

      if (this.selected_task_start) {
        this.taskState = true;
      } else {
        this.taskState = false;
      }

      if (
        this.order_id != "" ||
        !this.tasks_mapper[this.selected_task_start]["oid_required"]
      ) {
        this.OrderIdState = true;
      } else {
        this.OrderIdState = false;
      }

      if (this.start_unit_type) {
        this.unittypeState = true;
      } else {
        this.unittypeState = false;
      }

      return valid;
    },
    resetModal() {
      // empty values set inside the form after the form gets closed
      this.unit = "";
      this.unitState = null;
      this.nameState = null;
      this.selected_service_start = null;
      this.selected_task_start = null;
      this.taskState = null;
      this.order_id = "";
      this.OrderIdState = null;
      this.start_unit_type = null;
      this.unittypeState = null;
    },
    resetEditModal() {
      // empty values set inside the form after the form gets closed
      this.state_to_edit = "";
      this.result_to_edit = "";
    },
    handleOk(bvModalEvt) {
      // Prevent modal from closing
      bvModalEvt.preventDefault();
      // Trigger submit handler
      this.handleSubmit();
    },
    handleEditOk(bvModalEvt, item) {
      // Prevent edit modal from closing
      bvModalEvt.preventDefault();
      // Trigger submit handler
      this.handleEditSubmit(item);
    },
    handleEditSubmit(item) {
      // Exit when the form isn't valid
      if (!this.checkEditFormValidity()) {
        return;
      }

      if (!this.Edit(item)) {
        return;
      }

      // Hide the modal manually
      this.$nextTick(() => {
        this.$bvModal.hide("task-modal-prevent-closing");
      });
    },
    handleSubmit() {
      // Exit when the form isn't valid
      if (!this.checkFormValidity()) {
        return;
      }

      // POST request loop (for each given unit)
      var post_req = "/crm/manual_tasks/create";
      var payload_filled = {
        service_id: this.services_mapper[this.selected_service_start],
        task_id: this.tasks_mapper[this.selected_task_start]["id"],
        client_id: store.state.auth.client_id,
      };

      if (this.order_id) {
        payload_filled["refers_to_order_id"] = this.order_id;
      }

      var units_array = this.unit.split(",");
      payload_filled[this.start_unit_type] = units_array;

      axios_services
        .post(post_req, payload_filled)
        .then((response) => {
          console.log(post_req);
          console.log(payload_filled);
          console.log(response);
        })
        .catch((err) => {
          console.log(`Error: ${err}`);
        });

      // Hide the modal manually
      this.$nextTick(() => {
        this.$bvModal.hide("modal-prevent-closing");
      });
    },
    Filter() {
      // GET filtered service orders

      var first_filter_set = false;
      var req = "/crm/manual_tasks/task_query";

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

      // task name
      if (this.selected_task) {
        if (first_filter_set) {
          req += "&";
        } else {
          req += "?";
          first_filter_set = true;
        }
        req += "task_name=" + this.selected_task;
      }

      // task status
      if (this.selected_task_status) {
        if (first_filter_set) {
          req += "&";
        } else {
          req += "?";
          first_filter_set = true;
        }
        req += "task_status=" + this.selected_task_status;
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
        var filtered_jobs = Object.keys(response.data["tasks"]).length;
        for (var i = 0; i < filtered_jobs; i++) {
          this.table_items.push(response.data["tasks"][i]);
        }
      });
      console.log(this.table_items);
    },
  },
  mounted() {
    // fill table items on page start with manual tasks which are currently running
    axios_services
      .get("/crm/manual_tasks/task_query?task_status=In%20progress")
      .then((response) => {
        var running_jobs = Object.keys(response.data["tasks"]).length;
        for (var i = 0; i < running_jobs; i++) {
          this.table_items.push(response.data["tasks"][i]);
        }
      });

    // get all service names and ids on page start
    axios_services.get("/crm/services").then((response) => {
      var number_of_services = Object.keys(response.data["services"]).length;
      for (var i = 0; i < number_of_services; i++) {
        var element = {
          value: response.data["services"][i]["service_name"],
          text: response.data["services"][i]["service_name"],
        };
        this.services.push(element);
        this.services_mapper[response.data["services"][i]["service_name"]] =
          response.data["services"][i]["service_id"];
      }
    });

    // get all task names, ids and order-id-required on page start
    axios_services.get("/crm/manual_tasks").then((response) => {
      var number_of_tasks = Object.keys(response.data["tasks"]).length;
      for (var i = 0; i < number_of_tasks; i++) {
        var element = {
          value: response.data["tasks"][i]["task_name"],
          text: response.data["tasks"][i]["task_name"],
        };
        this.tasks.push(element);
        this.tasks_mapper[response.data["tasks"][i]["task_name"]] = {
          id: response.data["tasks"][i]["task_id"],
          oid_required: !response.data["tasks"][i]["order_id_not_required"],
        };
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

  font-weight-bold {
    
  }
}
</style>
