<template>
  <div>
    <v-form ref="form" class="root" lazy-validation>
      <div class="form-box">
        <h3>Investigation Details</h3>

        <h4>Investigation Title</h4>
        <v-textarea
          v-model="investigation.title"
          v-bind="$bind.select"
          :rules="[$form.required(investigation.title), $form.length(investigation.title, 60)]"
          hide-details="auto"
          rows="3"
          no-resize
        />

        <h4>Investigation Description</h4>
        <v-textarea
          v-model="investigation.description"
          v-bind="$bind.textarea"
          :rules="[$form.required(investigation.description), $form.length(investigation.description, 800)]"
          hide-details="auto"
          counter="800"
          rows="6"
          no-resize
        />

        <h4>Status</h4>
        <v-autocomplete
          v-model="investigation.status"
          v-bind="$bind.select"
          :items="$enums.converter($enums.status)"
          :rules="[$form.required(investigation.status)]"
          hide-details="auto"
          required
          dense
          @change="statusChange()"
        />

        <h4>Priority</h4>
        <v-autocomplete
          v-model="investigation.priority"
          v-bind="$bind.select"
          :items="['High', 'Medium', 'Low']"
          :rules="[$form.required(investigation.priority)]"
          hide-details="auto"
          required
          dense
        />

        <h4>Investigation Type</h4>
        <v-autocomplete
          v-model="investigation.investigation_type"
          v-bind="$bind.select"
          :items="$enums.converter($enums.investigation_types)"
          :rules="[$form.required(investigation.investigation_type)]"
          hide-details="auto"
          required
          dense
        />

        <span class="d-flex">
          <h4>Investigation Owner and back to back</h4>
          <small class="ml-2">(max: 2)</small>
        </span>
        <user-list-autocomplete
          v-model="investigation.owner_ids"
          v-bind="$bind.select"
          :items="users"
          :rules="[$form.arr_non_empty(investigation.owner_ids), $form.arr_len_lim(investigation.owner_ids, 2)]"
          item-text="filter_name"
          item-value="id"
          clearable
          multiple
        />
        <h4>Investigation Owner(s) Supervisor</h4>
        <user-list-autocomplete
          v-model="investigation.supervisor_id"
          v-bind="$bind.select"
          :items="users"
          :rules="[$form.required(investigation.supervisor_id)]"
          item-text="filter_name"
          item-value="id"
          clearable
        />
        <span class="d-flex">
          <h4>Working Folder Link</h4>
          <small class="ml-2">(optional)</small>
        </span>
        <v-text-field v-model="investigation.working_folder_link" v-bind="$bind.select" />
      </div>

      <equipment-details-form :investigation="investigation" @loading="changeLoading($event)" />

      <div class="form-box">
        <h3>Event Details</h3>

        <h4>Event Date/Time</h4>
        <e-date-time
          v-model="investigation.event_datetime"
          v-bind="$bind.textfield"
          :time="true"
          :rules="noFutureDateTimeRule(investigation.event_datetime)"
          hide-details="auto"
          dense
        />

        <delay-event-form ref="delayForm" :investigation="investigation" @loading="changeLoading($event)" />

        <h4>Investigation Due</h4>
        <e-date-time
          v-model="investigation.completion_due_date"
          v-bind="$bind.textfield"
          :time="false"
          hide-details="auto"
          quick_select
        />
        <span class="d-flex">
          <h4>Date Closed</h4>
          <small class="ml-2">(only required for closed investigations)</small>
        </span>
        <e-date-time
          v-model="investigation.date_closed"
          v-bind="$bind.textfield"
          :apply_default_rules="false"
          :time="false"
          :rules="noFutureDateTimeRule(investigation.date_closed)"
          now_select
          required
          dense
          hide-details="auto"
        />
        <!-- <span class="d-flex">
          <h4>Attachments</h4>
          <small class="ml-2">
            (optional, limit: {{ current_attachment_bytes }}/50MB)
          </small>
        </span>
        <e-file-uploader
          :files="attachments"
          :attachment_metadata="investigation.general_attachments"
          multiple
          @has_exceeded_file_lim="updateFileLimStatus($event)"
        /> -->
      </div>
    </v-form>

    <e-attachment-table
      :attachment_metadata="investigation.general_attachments"
      class="mt-4"
      @new_attachment="handleNewAttachment"
    />
    <!-- <e-file-upload-card
      v-if="investigation.id"
      :attachment_metadata="investigation.general_attachments"
      class="mt-4"
    /> -->
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import DelayEventForm from "@/components/Investigation/Investigation/CreateInvestigation/DelayEventForm";
import DelayEvents from "@/components/Investigation/Investigation/DelayEvents";
import EventMetricViewer from "@/components/Utils/EventMetricViewer";
import EquipmentDetailsForm from "@/components/Investigation/Investigation/CreateInvestigation/EquipmentDetailsForm.vue";

export default {
  components: {
    DelayEvents,
    EventMetricViewer,
    DelayEventForm,
    EquipmentDetailsForm,
  },
  props: {
    investigation: { type: Object },
    add_save_btn: { type: Boolean, required: false, default: true },
  },
  data() {
    return {
      // loading
      isLoading: false,
      // attachment
      attachments: [],
      exceeded_file_limit: false,
      equipmentLoading: false,
      filtered_equipments: [],
      filtered_damage_codes: [],
      // work order
    };
  },
  computed: {
    ...mapGetters({
      users: "user/getUsers",
    }),
    // --------------------
    // FLAGS
    // --------------------
    is_loading() {
      return this.isLoading;
    },
    is_new_investigation() {
      return this.investigation.id == null;
    },
    is_owner_supervisor_or_admin() {
      // admins can edit anything
      if (this.$perms.is_admin) return true;

      // owners and supervisor logic
      const uid = this.$auth.user.id;
      const res = this.investigation.owner_ids.includes(uid) || uid === this.investigation.supervisor_id;

      this.$store.dispatch("user/changeIsMyInvestigation", res);

      return res;
    },
  },
  watch: {
    is_loading() {
      this.$emit("loading", this.is_loading);
    },
    investigation() {
      // required if new aplus events to investigation (DevOps #183229)
      this.processInvestigationFromChart();
    },
  },
  mounted() {
    // HANDLE CHART STUFF
    this.processInvestigationFromChart();

    // OTHER
    // this.getEquipmentFields();
    // this.getAPLUSEventDetails();
    // this.getREMSEventDetails();
  },
  methods: {
    // ---------------------------------
    // work order number / repair costs
    // ---------------------------------
    cancelRequest() {
      this.is_aborting = true;
      this.is_loading = false;
    },
    async fetchWorkOrderDetails() {
      this.wo_loading = true;
      this.is_aborting = false;
      const url = "/redis/get_workorder";
      await this.$axios
        .$post(url, this.investigation.workorders)
        .then((res) => {
          this.wo_loading = false;
          this.planned_cost = res.planned_cost;
          this.planned_cost = Math.round(this.planned_cost);
          this.actual_cost = res.actual_cost;
          this.actual_cost = Math.round(this.actual_cost);
        })
        .catch((err) => console.error(err));

      //valid data for testing purpose 2200297776, 2200262040
    },
    statusChange() {
      if (this.investigation.status == 1) this.investigation.date_closed = null;
    },
    // --------------------
    // CHART
    // --------------------
    processInvestigationFromChart() {
      const query = this.$route.query;
      let date = [];
      let problem = [];
      let action = [];
      let circuit = [];
      let time_usage = [];

      if (query.items && query.items.length > 0 && typeof query.items[0] === "string") {
        this.$router.push({
          path: "/investigation",
          query: { id: parseInt(query.id) },
        });
      }

      // if new investigation
      if (query.items) {
        query.items.forEach((item) => {
          date.push(item.date);
          problem.push(item.problem);
          action.push(item.action);
          circuit.push(item.circuit);
          time_usage.push(item.time_usage);
        });
      }

      if (query.type === "APLUS") {
        if (!query.id) {
          const existing_aplus_ids = this.investigation.aplus_delay_event_ids;
          this.$axios
            .$get("/snowflake/get_charting_items", {
              params: {
                keys: {
                  date: date,
                  problem: problem,
                  action: action,
                  circuit: circuit,
                },
              },
            })
            .then((res) => {
              const new_ids = res.map((x) => x.id);

              // if existing investigation
              if (query.id) {
                this.investigation.aplus_delay_event_ids = [...existing_aplus_ids, ...new_ids];
              } else {
                this.investigation.aplus_delay_event_ids = res.map((x) => x.id);
                // all description should be same in aray
                this.investigation.description = res[0].problem;

                // ? all event_dates should be same in aray, right
                // ! data has same date but diff time, may not always be the case
                // ! e.g. 2022-06-01T06:42:40, 2022-06-27T17:53:10.269737+08:00
                this.investigation.event_datetime = this.$format.initDate(res[0].start_time);
              }

              this.$refs.delayForm.fetchEventDetails();
            });
        } else {
          let new_ids = query.items.map((x) => x.ids);
          new_ids = [].concat.apply([], new_ids);

          this.investigation.aplus_delay_event_ids = [...this.investigation.aplus_delay_event_ids, ...new_ids];
          this.investigation.aplus_delay_event_ids = [...new Set(this.investigation.aplus_delay_event_ids)];

          this.$refs.delayForm.fetchEventDetails();
        }
      }

      // // -------------------------
      else if (query.type === "REMS" && !query.id) {
        this.$axios.$get(`/snowflake/get_floc_item?id=${query.id}`).then((res) => {
          this.investigation.description = res.last_comment;
          // EQUIPMENT DETAILS
          this.investigation.function_location = res.functional_location;
          if (!this.equipment_descriptions.includes(res.equipment_name))
            this.equipment_descriptions.push(res.equipment_name);
          this.investigation.object_type = res.fleet_type;
          // EVENT DETAILS
          this.investigation.event_type = 2;
          this.investigation.event_datetime = new Date(Date.parse(res.event_datetime + "Z"));
          this.investigation.rems_delay_event_ids.push(res.event_id);
        });
      }
    },
    // --------------------
    // OTHER
    // --------------------

    changeLoading(flag) {
      this.isLoading = flag;
    },
    emitSave(noEmail = false) {
      this.investigation.noEmail = noEmail;
      this.$emit("save", {
        investigation: this.investigation,
        attachments: this.attachments,
      });

      this.attachments = [];
    },
    // --------------------
    // ATTACHMENTS
    // --------------------
    handleNewAttachment(attachment) {
      // update attachments array for emit
      const file_clone = {
        title: JSON.parse(JSON.stringify(attachment.title)),
        description: JSON.parse(JSON.stringify(attachment.description)),
        network_drive_link: JSON.parse(JSON.stringify(attachment.network_drive_link)),
        file: new File([attachment.file], attachment.file.name, {
          type: attachment.file.type,
        }),
      };

      this.attachments.push(file_clone);

      // update attachment meta data with pending attachments
      let meta_obj = {};
      meta_obj.filename = JSON.parse(JSON.stringify(attachment.file.name));
      meta_obj.size = JSON.parse(JSON.stringify(attachment.file.size));
      // meta_obj.extension = JSON.parse(JSON.stringify(attachment.file.filename.split(".").pop()));
      meta_obj.uploaded_by = this.$auth.user.id;
      meta_obj.created = new Date();
      meta_obj.network_drive_link = attachment.network_drive_link;
      meta_obj.title = attachment.title;
      meta_obj.description = attachment.description;

      this.investigation.general_attachments.push(meta_obj);
    },
    noFutureDateTimeRule(datetime) {
      if (this.investigation.id) return [];

      // only if new investigation
      return [this.$form.date_cannot_be_in_future(datetime)];
    },
  },
};
</script>

<style lang="scss" scoped>
.root {
  display: grid;
  gap: 0 26px;
  grid-template-columns: repeat(3, 1fr);
}

.form-box {
  max-width: 400px;
  width: 100%;
}

.v-textarea {
  * {
    overflow-y: auto;
  }
}

h3 {
  color: var(--v-primary-base);
  margin-bottom: 5px;
  font-weight: 400;
}
</style>
