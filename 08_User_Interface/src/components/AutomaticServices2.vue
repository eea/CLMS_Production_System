<template>
  <div>
    <!-- Notification error -->
    <b-toast
      id="notification-error"
      variant="danger"
      solid
      toaster="b-toaster-top-center"
      autoHideDelay="10000"
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
      autoHideDelay="10000"
    >
      <template v-slot:toast-title>
        <div class="d-flex flex-grow-1">
          <strong class="mr-auto">Success!</strong>
        </div>
      </template>
      <p>{{ successMsg }}</p>
      <p>{{ successMsgDetail }}</p>
    </b-toast>

    <!-- Notification warning -->
    <b-toast
      id="notification-warning"
      variant="warning"
      solid
      toaster="b-toaster-top-center"
      autoHideDelay="10000"
    >
      <template v-slot:toast-title>
        <div class="d-flex flex-grow-1">
          <strong class="mr-auto">Warning!</strong>
        </div>
      </template>
      <p>{{ errorMsg }}</p>
      <p>{{ errorMsgDetail }}</p>
    </b-toast>

    <!-- Filter box -->
    <div id="automatic-services" class="container">
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
          </div>

          <div class="row">
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
            <div class="col-6 text-left"><h3>Automatic Services</h3></div>
            <div class="col-6 text-right">
              <b-button id="addStepBtn" v-b-modal.modal-prevent-closing
                ><font-awesome-icon
                  :icon="['fa', 'plus-circle']"
                />&nbsp;&nbsp;Start a service</b-button
              >

              <b-modal
                id="modal-prevent-closing"
                ref="modal"
                title="Start a service"
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
                    <div class="row">
                      <b-form-group
                        label="Service name"
                        label-class="text-left font-weight-bold"
                        :invalid-feedback="ServiceFeedback"
                        :state="nameState"
                        class="col"
                      >
                        <b-form-select
                          v-model="selected_service_start"
                          :options="services"
                          :state="nameState"
                          :invalid-feedback="ServiceFeedback"
                          required
                        ></b-form-select>
                      </b-form-group>
                      <b-form-group
                        :invalid-feedback="humanize(parameter) + ' required'"
                        v-for="parameter in Object.keys(
                          payload[selected_service_start]
                        )"
                        :key="parameter"
                        :label="humanize(parameter)"
                        :state="
                          payload[selected_service_start][parameter]['State']
                        "
                        label-class="text-left font-weight-bold"
                        class="col-sm-6"
                      >
                        <b-form-input
                          v-model="
                            payload[selected_service_start][parameter][
                              'Current'
                            ]
                          "
                          :state="
                            payload[selected_service_start][parameter]['State']
                          "
                          :required="
                            payload[selected_service_start][parameter][
                              'Required'
                            ]
                          "
                        ></b-form-input>
                      </b-form-group>
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
                <div v-if="row.item.order_id == null">
                  -
                </div>
                <div v-else>
                  {{ row.item.order_id }}
                </div>
              </template>

              <template v-slot:cell(order_result)="row">
                <div v-if="row.item.order_result == null">
                  -
                </div>
                <div v-else>
                  {{ row.item.order_result }}
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
import axios_services from "../axios-services";
import store from "../store/store.js";

export default {
  name: "AutomaticServices",
  data() {
    return {
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
      services: [{ value: null, text: "Select a service" }],
      stati: [
        { value: null, text: "Select an order state" },
        { value: "Not started", text: "Not Started" },
        { value: "In progress", text: "In Progress" },
        { value: "Finished", text: "Finished" },
        { value: "Failed", text: "Failed" },
      ],
      selected_service: null,
      selected_status: null,
      spu: "",
      pcu: "",
      nameState: null,
      selected_service_start: null,
      services_mapper: { null: "" },
      isTableBusy: false,
      successMsg: null,
      errorMsg: null,
      errorMsgDetail: null,
      successMsgDetail: null,
      addModalBusy: false,
      editModalBusy: false,
      fullPage: true,
      edit_row: {
        item: { processing_unit: null, service_name: null, task_name: null },
      },
      alertFilter: false,
      alertFilerMsg: "",
      payload: {
        null: {},
        harmonics: {},
        batch_classification_test: {},
        logger: {},
        state: {},
        batch_classification_production: {},
        batch_classification_staging: {},
        vector_class_attribution: {
          subproduction_unit_name: {
            State: null,
            Current: "",
            Default: "",
            Required: true,
            Type: String,
          },
          vector: {
            State: null,
            Current: "/vsis3/task22/tests/in/test1.shp",
            Default: "/vsis3/task22/tests/in/test1.shp",
            Required: true,
            Type: String,
          },
          raster: {
            State: null,
            Current: "/vsis3/task22/tests/in/test.tif",
            Default: "/vsis3/task22/tests/in/test.tif",
            Required: true,
            Type: String,
          },
          config: {
            State: null,
            Current:
              "AWS_SECRET_ACCESS_KEY 2e7516dc941f4bdcae1204d51c354bee AWS_S3_ENDPOINT cf2.cloudferro.com:8080 AWS_VIRTUAL_HOSTING FALSE AWS_ACCESS_KEY_ID bc8e686837c2476ba4dcef06ba7272ca",
            Default:
              "AWS_SECRET_ACCESS_KEY 2e7516dc941f4bdcae1204d51c354bee AWS_S3_ENDPOINT cf2.cloudferro.com:8080 AWS_VIRTUAL_HOSTING FALSE AWS_ACCESS_KEY_ID bc8e686837c2476ba4dcef06ba7272ca",
            Required: true,
            Type: String,
          },
          method: {
            State: null,
            Current: "relative_count",
            Default: "relative_count",
            Required: true,
            Type: String,
          },
          method_params: {
            State: null,
            Current: "1 7",
            Default: "1 7",
            Required: false,
            Type: String,
          },
          na_value: {
            State: null,
            Current: 0,
            Default: 0,
            Required: false,
            Type: Number,
          },
          col_names: {
            State: null,
            Current: "occurrence_class_1 occurrence_class_7",
            Default: "occurrence_class_1 occurrence_class_7",
            Required: false,
            Type: String,
          },
          id_column: {
            State: null,
            Current: "id",
            Default: "id",
            Required: true,
            Type: String,
          },
          bucket_path: {
            State: null,
            Current: "bucketname/folder/subfolder/",
            Default: "bucketname/folder/subfolder/",
            Required: true,
            Type: String,
          },
          reference_year: {
            State: null,
            Current: "2018",
            Default: "2018",
            Required: true,
            Type: String,
          },
        },
        task2_feature_calculation: {
          processing_unit_name: {
            State: null,
            Current: "",
            Default: "",
            Required: true,
            Type: String,
          },
          start_date: {
            State: null,
            Current: "2017-07-01",
            Default: "2017-07-01",
            Required: true,
            Type: String,
          },
          end_date: {
            State: null,
            Current: "2019-06-30",
            Default: "2019-06-30",
            Required: true,
            Type: String,
          },
          cloud_cover: {
            State: null,
            Current: 80,
            Default: 80,
            Required: true,
            Type: Number,
          },
          interval_size: {
            State: null,
            Current: 10,
            Default: 10,
            Required: true,
            Type: Number,
          },
          s1_bands: {
            State: null,
            Current:
              "ASC_DVVVH,ASC_RVVVH,ASC_VV,ASC_VH,DSC_DVVVH,DSC_RVVVH,DSC_VV,DSC_VH",
            Default:
              "ASC_DVVVH,ASC_RVVVH,ASC_VV,ASC_VH,DSC_DVVVH,DSC_RVVVH,DSC_VV,DSC_VH",
            Required: false,
            Type: Array,
          },
          s2_bands: {
            State: null,
            Current:
              "B01,B02,B03,B04,B05,B06,B07,B08,B09,B11,B12,B8A,BRGHT,IRECI,NBR,NDVI,NDWI,NDWIGREEN,NGDR,RENDVI",
            Default:
              "B01,B02,B03,B04,B05,B06,B07,B08,B09,B11,B12,B8A,BRGHT,IRECI,NBR,NDVI,NDWI,NDWIGREEN,NGDR,RENDVI",
            Required: false,
            Type: Array,
          },
          precalculated_features: {
            State: null,
            Current: "geomorpho90,distance,dem",
            Default: "geomorpho90,distance,dem",
            Required: false,
            Type: Array,
          },
          use_cache: {
            State: null,
            Current: true,
            Default: true,
            Required: true,
            Type: Boolean,
          },
          aoi_coverage: {
            State: null,
            Current: 0,
            Default: 0,
            Required: true,
            Type: Number,
          },
          data_filter_s1: {
            State: null,
            Current: '{"min_aoi_coverage": 0, "min_time_difference": 0}',
            Default: '{"min_aoi_coverage": 0, "min_time_difference": 0}',
            Required: true,
            Type: String,
          },
          data_filter_s2: {
            State: null,
            Current: '{"min_aoi_coverage": 0, "min_time_difference": 24}',
            Default: '{"min_aoi_coverage": 0, "min_time_difference": 24}',
            Required: true,
            Type: String,
          },
        },
        task2_apply_model: {
          processing_unit_name: {
            State: null,
            Current: "",
            Default: "",
            Required: true,
            Type: String,
          },
          model_path: {
            State: null,
            Current: "",
            Default: "",
            Required: true,
            Type: String,
          },
          start_date: {
            State: null,
            Current: "2017-07-01",
            Default: "2017-07-01",
            Required: true,
            Type: String,
          },
          end_date: {
            State: null,
            Current: "2019-06-30",
            Default: "2019-06-30",
            Required: true,
            Type: String,
          },
          cloud_cover: {
            State: null,
            Current: 80,
            Default: 80,
            Required: true,
            Type: Number,
          },
          interval_size: {
            State: null,
            Current: 10,
            Default: 10,
            Required: true,
            Type: Number,
          },
          s1_bands: {
            State: null,
            Current:
              "ASC_DVVVH,ASC_RVVVH,ASC_VV,ASC_VH,DSC_DVVVH,DSC_RVVVH,DSC_VV,DSC_VH",
            Default:
              "ASC_DVVVH,ASC_RVVVH,ASC_VV,ASC_VH,DSC_DVVVH,DSC_RVVVH,DSC_VV,DSC_VH",
            Required: false,
            Type: Array,
          },
          s2_bands: {
            State: null,
            Current:
              "B01,B02,B03,B04,B05,B06,B07,B08,B09,B11,B12,B8A,BRGHT,IRECI,NBR,NDVI,NDWI,NDWIGREEN,NGDR,RENDVI",
            Default:
              "B01,B02,B03,B04,B05,B06,B07,B08,B09,B11,B12,B8A,BRGHT,IRECI,NBR,NDVI,NDWI,NDWIGREEN,NGDR,RENDVI",
            Required: false,
            Type: Array,
          },
          precalculated_features: {
            State: null,
            Current: "geomorpho90,distance,dem",
            Default: "geomorpho90,distance,dem",
            Required: false,
            Type: Array,
          },
          use_cache: {
            State: null,
            Current: true,
            Default: true,
            Required: true,
            Type: Boolean,
          },
          aoi_coverage: {
            State: null,
            Current: 0,
            Default: 0,
            Required: true,
            Type: Number,
          },
          data_filter_s1: {
            State: null,
            Current: '{"min_aoi_coverage": 0, "min_time_difference": 0}',
            Default: '{"min_aoi_coverage": 0, "min_time_difference": 0}',
            Required: true,
            Type: String,
          },
          data_filter_s2: {
            State: null,
            Current: '{"min_aoi_coverage": 0, "min_time_difference": 24}',
            Default: '{"min_aoi_coverage": 0, "min_time_difference": 24}',
            Required: true,
            Type: String,
          },
        },
        task2_apply_model_fast_lane: {
          processing_unit_name: {
            State: null,
            Current: "",
            Default: "",
            Required: true,
            Type: String,
          },
          model_path: {
            State: null,
            Current: "",
            Default: "",
            Required: true,
            Type: String,
          },
          start_date: {
            State: null,
            Current: "2017-07-01",
            Default: "2017-07-01",
            Required: true,
            Type: String,
          },
          end_date: {
            State: null,
            Current: "2019-06-30",
            Default: "2019-06-30",
            Required: true,
            Type: String,
          },
          cloud_cover: {
            State: null,
            Current: 80,
            Default: 80,
            Required: true,
            Type: Number,
          },
          interval_size: {
            State: null,
            Current: 10,
            Default: 10,
            Required: true,
            Type: Number,
          },
          s1_bands: {
            State: null,
            Current:
              "ASC_DVVVH,ASC_RVVVH,ASC_VV,ASC_VH,DSC_DVVVH,DSC_RVVVH,DSC_VV,DSC_VH",
            Default:
              "ASC_DVVVH,ASC_RVVVH,ASC_VV,ASC_VH,DSC_DVVVH,DSC_RVVVH,DSC_VV,DSC_VH",
            Required: false,
            Type: Array,
          },
          s2_bands: {
            State: null,
            Current:
              "B01,B02,B03,B04,B05,B06,B07,B08,B09,B11,B12,B8A,BRGHT,IRECI,NBR,NDVI,NDWI,NDWIGREEN,NGDR,RENDVI",
            Default:
              "B01,B02,B03,B04,B05,B06,B07,B08,B09,B11,B12,B8A,BRGHT,IRECI,NBR,NDVI,NDWI,NDWIGREEN,NGDR,RENDVI",
            Required: false,
            Type: Array,
          },
          precalculated_features: {
            State: null,
            Current: "geomorpho90,distance,dem",
            Default: "geomorpho90,distance,dem",
            Required: false,
            Type: Array,
          },
          use_cache: {
            State: null,
            Current: true,
            Default: true,
            Required: true,
            Type: Boolean,
          },
          aoi_coverage: {
            State: null,
            Current: 0,
            Default: 0,
            Required: true,
            Type: Number,
          },
          data_filter_s1: {
            State: null,
            Current: '{"min_aoi_coverage": 0, "min_time_difference": 0}',
            Default: '{"min_aoi_coverage": 0, "min_time_difference": 0}',
            Required: true,
            Type: String,
          },
          data_filter_s2: {
            State: null,
            Current: '{"min_aoi_coverage": 0, "min_time_difference": 24}',
            Default: '{"min_aoi_coverage": 0, "min_time_difference": 24}',
            Required: true,
            Type: String,
          },
        },
        task1_reprocessing: {
          processing_unit_name: {
            State: null,
            Current: "",
            Default: "",
            Required: true,
            Type: String,
          },
          start_date: {
            State: null,
            Current: "2018-04-01",
            Default: "2018-04-01",
            Required: true,
            Type: String,
          },
          end_date: {
            State: null,
            Current: "2018-10-31",
            Default: "2018-10-31",
            Required: true,
            Type: String,
          },
          cloud_cover: {
            State: null,
            Current: 80,
            Default: 80,
            Required: true,
            Type: Number,
          },
          features: {
            State: null,
            Current: "B01_MIN",
            Default: "B01_MIN",
            Required: true,
            Type: Array,
          },
          use_cache: {
            State: null,
            Current: true,
            Default: true,
            Required: true,
            Type: Boolean,
          },
          rule_set: {
            State: null,
            Current: '{"rule_key": "rule_value"}',
            Default: '{"rule_key": "rule_value"}',
            Required: true,
            Type: String,
          },
          data_filter: {
            State: null,
            Current: '{"min_aoi_coverage": 80, "min_time_difference": 0}',
            Default: '{"min_aoi_coverage": 80, "min_time_difference": 0}',
            Required: true,
            Type: String,
          },
        },
        task1_batch_classification: {
          processing_unit_name: {
            State: null,
            Current: "",
            Default: "",
            Required: true,
            Type: String,
          },
          start_date: {
            State: null,
            Current: "2018-04-01",
            Default: "2018-04-01",
            Required: true,
            Type: String,
          },
          end_date: {
            State: null,
            Current: "2018-10-31",
            Default: "2018-10-31",
            Required: true,
            Type: String,
          },
          cloud_cover: {
            State: null,
            Current: 80,
            Default: 80,
            Required: true,
            Type: Number,
          },
          features: {
            State: null,
            Current: "B01_MIN",
            Default: "B01_MIN",
            Required: true,
            Type: Array,
          },
          use_cache: {
            State: null,
            Current: true,
            Default: true,
            Required: true,
            Type: Boolean,
          },
          rule_set: {
            State: null,
            Current: '{"rule_key": "rule_value"}',
            Default: '{"rule_key": "rule_value"}',
            Required: true,
            Type: String,
          },
          data_filter: {
            State: null,
            Current: '{"min_aoi_coverage": 80, "min_time_difference": 0}',
            Default: '{"min_aoi_coverage": 80, "min_time_difference": 0}',
            Required: true,
            Type: String,
          },
        },
        retransformation: {
          subproduction_unit_name: {
            State: null,
            Current: "",
            Default: "",
            Required: true,
            Type: String,
          },
        },
        task1_stitching: {
          processing_unit_name: {
            State: null,
            Current: "129_1",
            Default: "129_1",
            Required: true,
            Type: String,
          },
          surrounding_pus: {
            State: null,
            Current: "129_2, 174, 175",
            Default: "129_2, 174, 175",
            Required: true,
            Type: String,
          },
        },
        task1_feature_calculation: {
          processing_unit_name: {
            State: null,
            Current: "",
            Default: "",
            Required: true,
            Type: String,
          },
          start_date: {
            State: null,
            Current: "2018-04-01",
            Default: "2018-04-01",
            Required: true,
            Type: String,
          },
          end_date: {
            State: null,
            Current: "2018-10-31",
            Default: "2018-10-31",
            Required: true,
            Type: String,
          },
          cloud_cover: {
            State: null,
            Current: 80,
            Default: 80,
            Required: true,
            Type: Number,
          },
          features: {
            State: null,
            Current: "NDVI_MEDIAN,B08_P75,B04_P75",
            Default: "NDVI_MEDIAN,B08_P75,B04_P75",
            Required: true,
            Type: Array,
          },
          use_cache: {
            State: null,
            Current: true,
            Default: true,
            Required: true,
            Type: Boolean,
          },
          data_filter: {
            State: null,
            Current: '{"min_aoi_coverage": 0, "min_time_difference": 0}',
            Default: '{"min_aoi_coverage": 0, "min_time_difference": 0}',
            Required: true,
            Type: String,
          },
        },
      },
      service_units: {
        task2_feature_calculation: "processing_unit_name",
        task2_apply_model: "processing_unit_name",
        task1_feature_calculation: "processing_unit_name",
        task1_batch_classification: "processing_unit_name",
        task1_reprocessing: "processing_unit_name",
        task2_apply_model_fast_lane: "processing_unit_name",
        vector_class_attribution: "subproduction_unit_name",
        retransformation: "subproduction_unit_name",
        task1_stitching: "processing_unit_name",
      },
    };
  },
  methods: {
    checkFormValidity() {
      // check if the form is valid
      const valid = this.$refs.form.checkValidity();

      if (this.selected_service_start) {
        this.nameState = true;
      } else {
        this.nameState = false;
      }

      for (var param in this.payload[this.selected_service_start]) {
        var comparison = "";
        if (
          typeof this.payload[this.selected_service_start][param]["Current"] ==
          "number"
        ) {
          comparison = null;
        }
        if (
          this.payload[this.selected_service_start][param]["Current"] !=
            comparison ||
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
      this.nameState = null;
      for (var param in this.payload[this.selected_service_start]) {
        this.payload[this.selected_service_start][param][
          "Current"
        ] = this.payload[this.selected_service_start][param]["Default"];
        this.payload[this.selected_service_start][param]["State"] = null;
      }
      this.selected_service_start = null;
      this.addModalBusy = false;
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

      this.addModalBusy = true;

      // POST request loop (for each given unit)
      var unit = this.payload[this.selected_service_start][
        this.service_units[this.selected_service_start]
      ];

      // remove spaces
      unit.Current = unit.Current.replace(/\s/g, "");
      // split units string to array
      var units_array = unit.Current.split(",");
      // remove duplicates
      units_array = [...new Set(units_array)];

      var post_req = "/services/" + this.selected_service_start;
      var payload_filled = {
        service_name: this.selected_service_start,
        user_id: store.state.auth.client_id,
      };
      for (var param in this.payload[this.selected_service_start]) {
        var current_val = this.payload[this.selected_service_start][param][
          "Current"
        ];

        var comparison = "";
        if (typeof current_val == "number") {
          comparison = null;
        }
        if (current_val == comparison) {
          continue;
        }
        var val_type = this.payload[this.selected_service_start][param]["Type"];
        if (val_type == Array) {
          payload_filled[param] = current_val.split(",");
        } else if (val_type == Number) {
          payload_filled[param] = Number(current_val);
        } else if (val_type == Boolean) {
          if (current_val.toString().toLowerCase() == "true") {
            payload_filled[param] = true;
          } else {
            payload_filled[param] = false;
          }
        } else if (val_type == String) {
          payload_filled[param] = current_val;
        } else if (val_type == Object) {
          payload_filled[param] = JSON.parse(current_val);
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
            this.successMsg = "Successfully created automatic service.";
            this.successMsgDetail =
              "Order ID: " + response.data.links.href.split("/")[3];
            this.$bvToast.show("notification-success");
            this.addModalBusy = false;
            // Hide the modal manually
            this.$nextTick(() => {
              this.$bvModal.hide("modal-prevent-closing");
            });
          })
          .catch((err) => {
            console.log(err.response.data.message.error_definition.message);
            this.errorMsg = "Automatic service could not be created.";
            this.errorMsgDetail =
              err.response.data.message.error_definition.message;
            this.$bvToast.show("notification-error");
            this.addModalBusy = false;
          });
      }
    },
    Filter() {
      // GET filtered service orders

      var first_filter_set = false;
      var req = "/crm/services/order_query";

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

      axios_services
        .get(req)
        .then((response) => {
          var filtered_jobs = Object.keys(response.data["services"]).length;
          for (var i = 0; i < filtered_jobs; i++) {
            this.table_items.push(response.data["services"][i]);
          }
          this.isTableBusy = false;
          console.log(response.data);
        })
        .catch((err) => {
          this.isTableBusy = false;
          console.log(`Èrror: ${err}`);
          // show error
          this.errorMsg = "Automatic Services could not be loaded.";
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
    foo(row) {
      this.edit_row = row;
      this.$root.$emit("bv::show::modal", "task-modal-prevent-closing");
    },
    alert_close() {
      this.alertFilter = false;
    },
  },
  mounted() {
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

#automatic-services {
  margin-top: 100px;
}

.table th,
.table td {
  vertical-align: middle !important;
}
</style>
