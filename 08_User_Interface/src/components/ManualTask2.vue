<template>
  <div>
    <!-- Notification error -->
    <b-toast
      id="notification-error"
      variant="danger"
      solid
      toaster="b-toaster-top-center"
      autoHideDelay="10000"
      lg
    >
      <template v-slot:toast-title>
        <div class="d-flex flex-grow-1">
          <strong class="mr-auto">Error!</strong>
        </div>
      </template>
      <p>{{ errorMsg }}</p>
      <p>{{ errorMsgDetail }}</p>
    </b-toast>

    <!-- Notification success -->
    <b-toast
      id="notification-success"
      variant="success"
      solid
      toaster="b-toaster-top-center"
      autoHideDelay="3000"
    >
      <template v-slot:toast-title>
        <div class="d-flex flex-grow-1">
          <strong class="mr-auto">Success!</strong>
        </div>
      </template>
      {{ successMsg }}
    </b-toast>

    <!-- Notification warning -->
    <b-toast
      id="notification-warning"
      variant="warning"
      solid
      toaster="b-toaster-top-center"
      autoHideDelay="3000"
    >
      <template v-slot:toast-title>
        <div class="d-flex flex-grow-1">
          <strong class="mr-auto">Warning!</strong>
        </div>
      </template>
      <p>{{ errorMsg }}</p>
      <p>{{ errorMsgDetail }}</p>
    </b-toast>

    <b-modal
      id="task-modal-prevent-closing"
      title="Update manual task"
      @show="resetEditModal"
      @hidden="resetEditModal"
      @ok="handleEditOk($event, edit_row.item)"
      ok-title="Update"
      no-close-on-backdrop
      no-close-on-esc
      size="md"
      :busy="editModalBusy"
      :ok-disabled="editModalOKBusy"
      :hide-header-close="true"
    >
      <dl class="row">
        <dt class="col-4 text-right">Processing unit:</dt>
        <dd class="col-8">{{ edit_row.item.processing_unit }}</dd>

        <dt class="col-4 text-right">Service name:</dt>
        <dd class="col-8">{{ humanize(edit_row.item.service_name) }}</dd>

        <dt class="col-4 text-right">Task name:</dt>
        <dd class="col-8">{{ humanize(edit_row.item.task_name) }}</dd>
      </dl>

      <!-- <hr class="mt-3 mb-3" /> -->

      <b-tabs v-model="tabIndex" content-class="mt-3">
        <b-tab title="Status" active>
          <form
            ref="form"
            @submit.stop.prevent="handleEditSubmit(edit_row.item)"
          >
            <b-form-group
              :label="TaskStateLabel"
              :invalid-feedback="TaskStateFeedback"
              :state="edittaskStateState"
              label-class="font-weight-bold"
            >
              <b-form-select
                v-model="state_to_edit"
                :options="task_stati"
                :state="validate_state"
                required
              ></b-form-select>
            </b-form-group>
            <b-form-group
              :label="ResultLabel"
              v-if="state_to_edit == 'finished'"
              label-for="result-input"
              :invalid-feedback="ResultFeedback"
              :state="resultState"
              label-class="font-weight-bold"
            >
              <b-form-input
                id="result-input"
                v-model="result_to_edit"
                :state="validate_result_to_edit"
                required
              ></b-form-input>
            </b-form-group>
          </form>
        </b-tab>
        <b-tab title="Order-ID" :disabled="displayTabViewOrderID == false">
          <form
            ref="form"
            @submit.stop.prevent="handleEditSubmit(edit_row.item)"
          >
            <b-form-group
              label="Order ID"
              label-for="order-id-input"
              label-class="font-weight-bold"
              invalid-feedback="Order-ID required"
            >
              <b-form-input
                v-model="orderID_to_edit"
                :state="validation_orderID"
                required
              ></b-form-input>
            </b-form-group>
          </form>
        </b-tab>
      </b-tabs>
    </b-modal>

    <!-- SPU Edit Modal -->
    <b-modal
      id="task-modal-edit-spu"
      title="Update manual task"
      @show="resetEditModal"
      @hidden="resetEditModal"
      @ok="handleSPUEditOk($event)"
      ok-title="Update"
      no-close-on-backdrop
      no-close-on-esc
      size="md"
      :busy="editModalBusy"
      :ok-disabled="editModalOKBusy"
      :hide-header-close="true"
    >
      <!-- <hr class="mt-3 mb-3" /> -->

      <form ref="form" @submit.stop.prevent="handleSPUEditSubmit()">
        <b-form-group
          :label="SPULabel"
          :invalid-feedback="SPUFeedback"
          :state="editspustate"
          label-class="font-weight-bold"
        >
          <b-form-input
            v-model="spu_to_edit"
            :state="validate_spu_to_edit"
            required
          ></b-form-input>
        </b-form-group>

        <b-form-group
          id="service-name"
          label="Service Name"
          label-class="text-left font-weight-bold"
          :state="editservicestate"
        >
          <b-form-select
            v-model="selected_service"
            :options="services"
            :state="validate_service_to_edit"
            required
          ></b-form-select>
        </b-form-group>

        <b-form-group
          id="task-name"
          label="Task name"
          label-class=" text-left font-weight-bold"
          :state="edittaskstate"
        >
          <b-form-select
            v-model="selected_task"
            :options="tasks"
            :state="validate_task_to_edit"
            required
          ></b-form-select>
        </b-form-group>

        <b-form-group
          :label="TaskStateLabel"
          :invalid-feedback="TaskStateFeedback"
          :state="edittaskStateState"
          label-class="font-weight-bold"
        >
          <b-form-select
            v-model="state_to_edit"
            :options="task_stati"
            :state="validate_state"
            required
          ></b-form-select>
        </b-form-group>
        <b-form-group
          :label="ResultLabel"
          v-if="state_to_edit == 'finished'"
          label-for="result-input"
          :invalid-feedback="ResultFeedback"
          :state="resultState"
          label-class="font-weight-bold"
        >
          <b-form-input
            id="result-input"
            v-model="result_to_edit"
            :state="validate_result_to_edit"
            required
          ></b-form-input>
        </b-form-group>
      </form>
    </b-modal>

    <!-- Filter box -->
    <div id="manual-taks" class="container">
      <div class="card mb-5">
        <!-- <div class="card-header">
        <h5 class="text-left">Filter Options</h5>
      </div> -->
        <div class="card-body">
          <div v-if="alertFilter == true">
            <b-alert class="text-left" show variant="danger">
              {{ alertFilerMsg }}
              <b-button
                type="button"
                class="close"
                data-dismiss="alert"
                @click="alert_close()"
                >&times;</b-button
              >
            </b-alert>
          </div>
          <div class="row">
            <div class="col-sm">
              <b-form-group
                id="sup-name"
                label="Sub-production Unit (SPU)"
                label-class="text-left font-weight-bold"
              >
                <b-form-input
                  :autofocus="false"
                  id="sup-name-input"
                  ref="refName"
                  v-model="spu"
                  placeholder="Add a sub-production unit ..."
                ></b-form-input>
              </b-form-group>
            </div>

            <div class="col-sm">
              <b-form-group
                id="service-name"
                label="Service name"
                label-class="text-left font-weight-bold"
              >
                <b-form-select
                  v-model="selected_service"
                  :options="services"
                ></b-form-select>
              </b-form-group>
            </div>
            <div class="col-sm">
              <b-form-group
                id="orderid-name"
                label="Order status"
                label-class="text-left font-weight-bold"
              >
                <b-form-select
                  v-model="selected_status"
                  :options="stati"
                ></b-form-select>
              </b-form-group>
            </div>
          </div>

          <div class="row">
            <div class="col-sm">
              <b-form-group
                id="processing-unit-name"
                label="Processing unit"
                label-class="text-left font-weight-bold"
              >
                <b-form-input
                  :autofocus="false"
                  id="processing-unit-name-input"
                  ref="refName"
                  v-model="pcu"
                  placeholder="Add a processing unit ..."
                ></b-form-input>
              </b-form-group>
            </div>
            <div class="col-sm">
              <b-form-group
                id="task-name"
                label="Task name"
                label-class=" text-left font-weight-bold"
              >
                <b-form-select
                  v-model="selected_task"
                  :options="tasks"
                ></b-form-select>
              </b-form-group>
            </div>
            <div class="col-sm">
              <b-form-group
                id="task-status"
                label="Task status"
                label-class="text-left font-weight-bold"
              >
                <b-form-select
                  v-model="selected_task_status"
                  :options="task_stati"
                ></b-form-select>
              </b-form-group>
            </div>
          </div>

          <div class="row">
            <div class="col">
              <b-button
                @click="Filter()"
                block
                variant="primary"
                :disabled="isTableBusy == true"
                ><font-awesome-icon
                  :icon="['fa', 'search']"
                />&nbsp;&nbsp;Filter</b-button
              >
            </div>
          </div>
        </div>
      </div>

      <div class="card mb-4">
        <div class="card-header">
          <div class="row">
            <div class="col-6 text-left"><h3>Manual Tasks</h3></div>
            <div class="col-6 text-right">
              <!-- <b-button id="addStepBtn" v-b-modal.modal-prevent-closing
                ><font-awesome-icon
                  :icon="['fa', 'plus-circle']"
                />&nbsp;&nbsp;Start a manual task</b-button
              > -->
              <!-- <b-button
                  size="sm"
                  variant="secondary"
                  @click="show_spu_dialog()"
                  ><font-awesome-icon :icon="['fa', 'edit']" />&nbsp;&nbsp;Edit
                  a Subproduction Unit</b-button
                > -->
              <div class="row">
                <div class="col">
                  <b-button
                    class="text-right"
                    id="addStepBtn"
                    v-b-modal.modal-prevent-closing
                    ><font-awesome-icon
                      :icon="['fa', 'plus-circle']"
                    />&nbsp;&nbsp;Start a manual task</b-button
                  >
                </div>
                <div class="col">
                  <b-button variant="secondary" @click="show_spu_dialog()"
                    ><font-awesome-icon
                      :icon="['fa', 'edit']"
                    />&nbsp;&nbsp;Edit a Subproduction Unit</b-button
                  >
                </div>
              </div>

              <b-modal
                id="modal-prevent-closing"
                ref="modal"
                title="Start a manual task"
                @show="resetModal"
                @hidden="resetModal"
                @ok="handleOk"
                ok-title="Submit"
                size="lg"
                :hide-header-close="true"
                no-close-on-backdrop
                no-close-on-esc
                :busy="addModalBusy"
              >
                <b-overlay :show="addModalBusy" rounded="sm">
                  <!-- ----------------------------------- -->
                  <form ref="form" @submit.stop.prevent="handleSubmit">
                    <b-form-group
                      label="Unit type"
                      label-class="text-left font-weight-bold"
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
                      label-class="text-left font-weight-bold"
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

                    <hr class="mt-3 mb-3" />

                    <!-- ----------------------------------- -->

                    <div class="row">
                      <div class="col">
                        <b-form-group
                          label="Service name"
                          label-class="text-left font-weight-bold"
                          :invalid-feedback="ServiceFeedback"
                          :state="nameState"
                        >
                          <b-form-select
                            v-model="selected_service_start"
                            :options="services"
                            :state="nameState"
                            :invalid-feedback="ServiceFeedback"
                            :required="
                              tasks_mapper[selected_task_start]['oid_required']
                            "
                          ></b-form-select>
                        </b-form-group>
                      </div>

                      <div class="col">
                        <b-form-group
                          :label="TaskLabel"
                          :invalid-feedback="TaskFeedback"
                          :state="taskState"
                          label-class="text-left font-weight-bold"
                        >
                          <b-form-select
                            v-model="selected_task_start"
                            :options="tasks"
                            :state="taskState"
                            required
                          ></b-form-select>
                        </b-form-group>
                      </div>
                    </div>
                  </form>
                </b-overlay>
              </b-modal>
            </div>
          </div>
        </div>
        <div class="card-body">
          <!-- Table View -->
          <div class="row">
            <b-table
              responsive
              striped
              hover
              head-variant="null"
              :items="table_items"
              :fields="columns"
              :busy="isTableBusy"
              class="text-left"
              small
            >
              <template #table-busy>
                <div class="text-center my-2">
                  <b-spinner class="align-middle"></b-spinner>
                  <strong> Loading...</strong>
                </div>
              </template>

              <template v-slot:cell(service_name)="row">
                {{ humanize(row.item.service_name) }}
              </template>

              <template v-slot:cell(order_status)="row">
                <div v-if="row.item.order_status == null">
                  -
                </div>
                <div v-else>
                  {{ row.item.order_status }}
                </div>
              </template>

              <template v-slot:cell(order_id)="row">
                <small>{{ row.item.order_id }}</small>
                <!-- <div v-if="row.order_status == null">
                  <!- <small><i>Not required</i></small> ->
                  -
                </div>
                <div v-else>
                  {{ row.order_status }}
                </div> -->
              </template>

              <template v-slot:cell(task_name)="row">
                {{ humanize(row.item.task_name) }}
              </template>

              <template v-slot:cell(task_result)="row">
                <div v-if="row.item.task_result == null">
                  -
                </div>
                <div v-else>
                  {{ row.item.task_result }}
                </div>
              </template>

              <template v-slot:cell(edit)="row">
                <div class="float-right btn-group-nowrap">
                  <b-button
                    :id="table_items.processing_unit"
                    size="sm"
                    variant="secondary"
                    :disabled="row.item.task_name == null"
                    @click="show_dialog(row)"
                    ><font-awesome-icon
                      :icon="['fa', 'edit']"
                    />&nbsp;&nbsp;Edit</b-button
                  >
                  <!-- Edit Form -->
                </div>
              </template>
            </b-table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
//import { component } from 'vue/types/umd';
import axios_services from "../axios-services";
import store from "../store/store.js";

export default {
  name: "ManualTasks",
  data() {
    return {
      UnitLabel: "Units (comma separated units)",
      UnitFeedback: "Units are required",
      SPUFeedback: "Subproduction Unit is required",
      SPULabel: "Subproduction-Unit",
      ServiceLabel: "Service Name",
      TaskLabel: "Task Name",
      TaskFeedback: "Task Name is required",
      ServiceFeedback: "Service Name is required",
      OrderIdLabel: "Based on Order-ID",
      OrderIdFeedback: "Order-ID is required for this manual ask",
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
          class: "text-left",
          label: "SPU",
        },
        {
          key: "processing_unit",
          class: "text-left",
          label: "Processing Unit",
        },
        { key: "service_name", class: "text-left", label: "Service Name" },
        {
          key: "order_status",
          class: "text-left",
          label: "Order Status",
        },
        { key: "order_id", class: "text-left", label: "Order ID" },
        {
          key: "task_name",
          class: "text-left",
          label: "Task Name",
        },
        {
          key: "task_status",
          class: "text-left",
          label: "Task Status",
        },
        { key: "task_result", class: "text-left", label: "Task Result" },
        { key: "edit", class: "text-left", label: "" },
      ],
      services: [{ value: null, text: "Select a service" }],
      tasks: [{ value: null, text: "Select a task" }],
      stati: [
        { value: null, text: "Select an order state" },
        { value: "Not started", text: "Not Started" },
        { value: "In progress", text: "In Progress" },
        { value: "Finished", text: "Finished" },
        { value: "Failed", text: "Failed" },
      ],
      task_stati: [
        { value: null, text: "Select a task state" },
        //{ value: "Not started", text: "Not Started" },
        { value: "in_progress", text: "In Progress" },
        { value: "finished", text: "Finished" },
        { value: "failed", text: "Failed" },
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
      taskStateState: null,
      order_id: "",
      OrderIdState: null,
      selected_service_start: null,
      selected_task_start: null,
      selected_task_status_start: null,
      start_unit_type: null,
      resultState: null,
      edittaskStateState: null,
      editspustate: null,
      edittaskstate: null,
      editservicestate: null,
      unittypeState: null,
      unit_options: [
        { text: "Select a unit type", value: null },
        { text: "Sub-Production unit", value: "subproduction_unit" },
        { text: "Processing Unit", value: "processing_unit" },
      ],
      services_mapper: {
        null:
          "a332e9289121bf19abd4005b94cee4e257ea8689e279eeb37f4bbc0773581356",
      }, // no_base service
      tasks_mapper: { null: { id: "", oid_required: false } },
      state_to_edit: null,
      result_to_edit: "",
      spu_to_edit: "",
      isTableBusy: false,
      successMsg: null,
      errorMsg: null,
      errorMsgDetail: null,
      addModalBusy: false,
      editModalBusy: false,
      fullPage: true,
      edit_row: {
        item: { processing_unit: null, service_name: null, task_name: null },
      },
      edit_spu_row: {
        item: { subproduction_unit: null, service_name: null, task_name: null },
      },
      alertFilter: false,
      alertFilerMsg: "",
      tabIndex: null,
      displayTabViewOrderID: true,
      orderID_to_edit: null,
      editModalOKBusy: false,
      tasks_list: [],
    };
  },
  methods: {
    Edit(item, tabIndex) {
      var payload_edit = {
        processing_unit: item["processing_unit"],
        service_id: this.services_mapper[item["service_name"]],
        task_id: this.tasks_mapper[item["task_name"]]["id"],
        client_id: store.state.auth.client_id,
      };

      if (tabIndex == 0) {
        if (this.state_to_edit) {
          payload_edit["state"] = this.state_to_edit;
        }
        if (this.state_to_edit == "finished") {
          payload_edit["result"] = this.result_to_edit;
        }
        this.editModalBusy = true;
        axios_services
          .put("/crm/manual_tasks/update_state", payload_edit)
          .then((response) => {
            console.log(payload_edit);
            console.log(response);
            this.$root.$emit("bv::hide::modal", "task-modal-prevent-closing");
            this.successMsg = "Successfully updated manual task.";
            this.$bvToast.show("notification-success");
            this.editModalBusy = false;
          })
          .catch((error) => {
            console.log(error.response);
            console.log(`Error: ${error.response}`);
            this.errorMsg = "Manual task could not be updated.";
            this.errorMsgDetail =
              error.response.data.message.error_definition.message;
            this.$bvToast.show("notification-error");
            this.editModalBusy = false;
          });
      } else {
        payload_edit["refers_to_order_id"] = this.orderID_to_edit;
        this.editModalBusy = true;
        axios_services
          .put("/crm/manual_tasks/update_order_id", payload_edit)
          .then(() => {
            this.$root.$emit("bv::hide::modal", "task-modal-prevent-closing");
            this.successMsg = "Successfully updated manual task.";
            this.$bvToast.show("notification-success");
            this.editModalBusy = false;
          })
          .catch((error) => {
            console.log(error.response);
            console.log(`Error: ${error.response}`);
            this.errorMsg = "Manual task could not be updated.";
            this.errorMsgDetail =
              error.response.data.message.error_definition.message;
            this.$bvToast.show("notification-error");
            this.editModalBusy = false;
          });
      }
    },
    SPUEdit() {
      var payload_edit = {
        subproduction_unit: this.spu_to_edit,
        service_id: this.services_mapper[this.selected_service],
        task_id: this.tasks_mapper[this.selected_task]["id"],
        client_id: store.state.auth.client_id,
      };

      if (this.state_to_edit) {
        payload_edit["state"] = this.state_to_edit;
      }
      if (this.state_to_edit == "finished") {
        payload_edit["result"] = this.result_to_edit;
      }
      this.editModalBusy = true;
      axios_services
        .put("/crm/manual_tasks/update_spu_state", payload_edit)
        .then((response) => {
          console.log(payload_edit);
          console.log(response);
          this.$root.$emit("bv::hide::modal", "task-modal-edit-spu");
          this.successMsg = "Successfully updated manual task.";
          this.$bvToast.show("notification-success");
          this.editModalBusy = false;
        })
        .catch((error) => {
          console.log(error.response);
          console.log(`Error: ${error.response}`);
          this.errorMsg = "Manual task could not be updated.";
          this.errorMsgDetail =
            error.response.data.message.error_definition.message;
          this.$bvToast.show("notification-error");
          this.editModalBusy = false;
        });
    },
    checkEditFormValidity(tabIndex) {
      if (tabIndex == 0) {
        // // check if the form is valid - (tab 1)
        // const valid = this.$refs.form.checkValidity();

        // if (this.state_to_edit) {
        //   this.edittaskStateState = true;
        //   if ((this.state_to_edit == "finished") & (this.result_to_edit != "")) {
        //     this.resultState = true;
        //   } else {
        //     this.resultState = false;
        //   }
        // } else {
        //   this.edittaskStateState = false;
        // }
        // return valid;
        return true;
      } else if (tabIndex == 1) {
        return true;
      }
    },
    checkFormValidity() {
      // check if the form is valid
      const valid = this.$refs.form.checkValidity();

      if (this.unit != "") {
        this.unitState = true;
      } else {
        this.unitState = false;
      }

      if (
        this.selected_service_start ||
        !this.tasks_mapper[this.selected_task_start]["oid_required"]
      ) {
        this.nameState = true;
      } else {
        this.nameState = false;
      }

      if (this.selected_task_start) {
        this.taskState = true;
      } else {
        this.taskState = false;
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
      this.addModalBusy = false;
      this.orderID_to_edit_state = null;
      this.orderID_to_edit = null;
    },
    resetEditModal() {
      // empty values set inside the form after the form gets closed
      this.state_to_edit = null;
      this.result_to_edit = "";
      this.spu_to_edit = "";
      this.selected_service = null;
      this.selected_task = null;
      this.resultState = null;
      this.edittaskStateState = null;
      this.editspustate = null;
      this.edittaskstate = null;
      this.editservicestate = null;
      this.editModalBusy = false;
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
      this.handleEditSubmit(item, this.tabIndex);
    },
    handleSPUEditOk(bvModalEvt) {
      // Prevent edit modal from closing
      bvModalEvt.preventDefault();
      // Trigger submit handler
      this.handleSPUEditSubmit();
    },
    handleEditSubmit(item, tabIndex) {
      this.Edit(item, tabIndex);
    },
    handleSPUEditSubmit() {
      this.SPUEdit();
    },
    handleSubmit() {
      // Exit when the form isn't valid
      if (!this.checkFormValidity()) {
        return;
      }

      this.addModalBusy = true;

      // POST request loop (for each given unit)
      var post_req = "/crm/manual_tasks/create";
      var payload_filled = {
        service_id: this.services_mapper[this.selected_service_start],
        task_id: this.tasks_mapper[this.selected_task_start]["id"],
        client_id: store.state.auth.client_id,
      };

      // if (this.order_id) {
      //   payload_filled["refers_to_order_id"] = this.order_id.split(",");
      // }

      // remove spaces
      this.unit = this.unit.replace(/\s/g, "");
      // split units string to array
      var units_array = this.unit.split(",");
      // remove duplicates
      units_array = [...new Set(units_array)];

      payload_filled[this.start_unit_type] = units_array;
      //payload_filled[this.start_unit_type] = this.unit;
      console.log(payload_filled);
      axios_services
        .post(post_req, payload_filled)
        .then((response) => {
          console.log(post_req);
          console.log(payload_filled);
          console.log(response);
          this.addModalBusy = false;
          this.successMsg = "Successfully created manual task.";
          this.$bvToast.show("notification-success");

          // Hide the modal manually
          this.$nextTick(() => {
            this.$bvModal.hide("modal-prevent-closing");
          });
        })
        .catch((err) => {
          console.log(err.response.data.message.error_definition.message);
          this.$bvToast.show("notification-error");
          this.errorMsg = "Manual task could not be created.";
          this.errorMsgDetail =
            err.response.data.message.error_definition.message;
          this.addModalBusy = false;
        });
    },
    Filter() {
      // GET filtered service orders

      var first_filter_set = false;
      var req = "/crm/manual_tasks/task_query";

      if (this.spu != "" && this.pcu != "") {
        this.alertFilerMsg =
          "For filtering, only one sub-production unit or one processing unit can be filtered at a time.";
        this.alertFilter = true;
        return;
      } else if (this.spu == "" && this.pcu == "") {
        this.alertFilerMsg =
          "For filtering, either one sub-production unit or one processing unit needs to be provided!";
        this.alertFilter = true;
        return;
      } else {
        this.alertFilter = false;
        this.alertFilerMsg = null;
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

      // Show waiting animation
      this.isTableBusy = true;

      // send GET request
      console.log(req);
      // axios_services.get(req).then((response) => {
      //   console.log(response.data);
      //   var filtered_jobs = Object.keys(response.data["tasks"]).length;
      //   for (var i = 0; i < filtered_jobs; i++) {
      //     this.table_items.push(response.data["tasks"][i]);
      //   }
      // });

      axios_services
        .get(req)
        .then((response) => {
          var filtered_jobs = Object.keys(response.data["tasks"]).length;

          for (var i = 0; i < filtered_jobs; i++) {
            this.table_items.push(response.data["tasks"][i]);
          }

          this.isTableBusy = false;
          console.log(response.data);
        })
        .catch((err) => {
          this.isTableBusy = false;
          console.log(`Èrror: ${err}`);
          // show error
          this.errorMsg = "Manual tasks could not be loaded.";
          this.errorMsgDetail =
            err.response.data.message.error_definition.message;
          this.$bvToast.show("notification-warning");
        });

      console.log(this.table_items);
    },
    humanize(str) {
      if (!str) {
        return "-";
      }
      var i,
        frags = str.split("_");
      for (i = 0; i < frags.length; i++) {
        frags[i] = frags[i].charAt(0).toUpperCase() + frags[i].slice(1);
      }
      return frags.join(" ");
    },
    show_dialog(row) {
      this.edit_row = row;
      this.$root.$emit("bv::show::modal", "task-modal-prevent-closing");
      this.set_is_order_id_required(this.edit_row.item.task_name);
    },
    show_spu_dialog() {
      this.$root.$emit("bv::show::modal", "task-modal-edit-spu");
    },
    alert_close() {
      this.alertFilter = false;
    },
    set_is_order_id_required(task_name) {
      var order_id_not_required = true;
      this.tasks_list.forEach((element) => {
        if (element.task_name == task_name) {
          order_id_not_required = element.order_id_not_required;
        }
      });
      this.displayTabViewOrderID = !order_id_not_required;
    },
  },
  mounted() {
    // fill table items on page start with manual tasks which are currently running
    // this.isTableBusy = true;
    // axios_services
    //   .get("/crm/manual_tasks/task_query?task_status=In%20progress")
    //   .then((response) => {
    //     var filtered_jobs = Object.keys(response.data["tasks"]).length;
    //     for (var i = 0; i < filtered_jobs; i++) {
    //       this.table_items.push(response.data["tasks"][i]);
    //     }
    //     this.isTableBusy = false;
    //     console.log(response.data);
    //   })
    //   .catch((err) => {
    //     this.isTableBusy = false;
    //     console.log(`Èrror: ${err}`);
    //   });

    // get all service names and ids on page start
    axios_services.get("/crm/services").then((response) => {
      var number_of_services = Object.keys(response.data["services"]).length;
      for (var i = 0; i < number_of_services; i++) {
        var element = {
          value: response.data["services"][i]["service_name"],
          text: this.humanize(response.data["services"][i]["service_name"]),
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
          text: this.humanize(response.data["tasks"][i]["task_name"]),
        };
        this.tasks.push(element);
        this.tasks_mapper[response.data["tasks"][i]["task_name"]] = {
          id: response.data["tasks"][i]["task_id"],
          oid_required: !response.data["tasks"][i]["order_id_not_required"],
        };
        this.tasks_list = response.data["tasks"];
      }
    });
  },
  watch: {
    tabIndex(newValue) {
      if (newValue == 0) {
        this.editModalOKBusy = true;
        this.orderID_to_edit = null;
      } else if (newValue == 1) {
        this.editModalOKBusy = true;
        this.state_to_edit = null;
        this.result_to_edit = null;
      }
    },
    validation_orderID(newValue) {
      console.log("order: ", newValue);
      if (newValue) {
        this.editModalOKBusy = false;
      } else {
        this.editModalOKBusy = true;
      }
    },
    validate_state(newValue) {
      if (newValue) {
        this.editModalOKBusy = false;
      } else {
        this.editModalOKBusy = true;
      }
    },
    validate_result_to_edit(newV) {
      console.log(newV);
      if (newV) {
        this.editModalOKBusy = false;
      } else {
        this.editModalOKBusy = true;
      }
    },
    validate_spu_to_edit(newV) {
      console.log(newV);
      if (newV) {
        this.editModalOKBusy = false;
      } else {
        this.editModalOKBusy = true;
      }
    },
    validate_service_to_edit(newV) {
      console.log(newV);
      if (newV) {
        this.editModalOKBusy = false;
      } else {
        this.editModalOKBusy = true;
      }
    },
    validate_task_to_edit(newV) {
      console.log(newV);
      if (newV) {
        this.editModalOKBusy = false;
      } else {
        this.editModalOKBusy = true;
      }
    },
    state_to_edit(newValue) {
      console.log(newValue);
      if (newValue == null) {
        this.editModalOKBusy = true;
      } else if (newValue == "finished") {
        if (this.result_to_edit == null || this.result_to_edit.length == 0) {
          this.editModalOKBusy = true;
        }
      } else {
        this.editModalOKBusy = false;
      }
    },
  },
  computed: {
    validation_orderID() {
      return !(
        this.orderID_to_edit == null || this.orderID_to_edit.length == 0
      );
    },
    validate_state() {
      return !(this.state_to_edit == null);
    },
    validate_result_to_edit() {
      return !(this.result_to_edit == null || this.result_to_edit.length == 0);
    },
    validate_spu_to_edit() {
      return !(this.spu_to_edit == null || this.spu_to_edit.length == 0);
    },
    validate_service_to_edit() {
      return !(
        this.selected_service == null || this.selected_service.length == 0
      );
    },
    validate_task_to_edit() {
      return !(this.selected_task == null || this.selected_task.length == 0);
    },
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

#manual-taks {
  margin-top: 100px;
}

.table th,
.table td {
  vertical-align: middle !important;
}
</style>
