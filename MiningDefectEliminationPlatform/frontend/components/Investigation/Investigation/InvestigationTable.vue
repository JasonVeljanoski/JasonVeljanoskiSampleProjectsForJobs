<template>
  <filter-table
    ref="rel_inv_table"
    :loading="loading"
    :headers="filtered_headers"
    :items="investigations"
    :options.sync="options"
    :server-items-length="total_items"
    title="Relevant Investigations"
    @clear="clearFilters()"
  >
    <!-- DATA TABLE SLOTS -->
    <template #item.relevant="{ item }">
      <div class="d-flex justify-center">
        <v-checkbox
          v-model="investigation.relevant_investigation_ids"
          :value="item.id"
          @change="updateSelected($event)"
        />
      </div>
    </template>
    <template #item.id="{ item }">
      <copy-icon-btn :id="item.id" @copy="copyInvestigationUrl(item.id)" />
    </template>
    <template #item.view="{ item }">
      <a :href="`/investigation?id=${item.id}`" target="_blank">
        <e-icon-btn v-bind="$bind.btn_simple" tooltip="Investigation Link"> mdi-application-edit-outline </e-icon-btn>
      </a>
    </template>
    <template #item.title="{ item }">
      <title-hover-text :main_text="item.title" :sub_text="item.description" />
    </template>

    <!-- FILTER SLOTS -->
    <template #filters>
      <div v-if="filtersLoading" class="d-flex justify-center">
        <v-progress-circular v-if="filtersLoading" indeterminate color="primary" />
      </div>

      <template v-else>
        <v-checkbox
          v-model="filters.show_relevant_flag"
          label="Relevant Investigations"
          class="mt-0 pt-0 my-3"
          hide-details="auto"
        />

        <v-text-field
          v-model="global_text"
          v-bind="$bind.select"
          placeholder="Global Text Search"
          class="mb-4"
          clearable
          @keyup.native.enter="$event.target.blur()"
          @blur="searchGlobalText"
          @click:clear="clearGlobalText"
        />

        <h4># Investigation Number</h4>
        <v-text-field v-model="filters.id" v-bind="$bind.select" type="number" clearable />

        <h4>Site</h4>
        <v-autocomplete
          v-model="filters.site"
          v-bind="$bind.select"
          :loading="loaders.sites"
          :items="sites"
          clearable
          multiple
        />

        <h4>Department</h4>
        <v-autocomplete
          v-model="filters.department"
          v-bind="$bind.select"
          :loading="loaders.departments"
          :items="departments"
          clearable
          multiple
        />

        <h4>FLOC</h4>
        <v-autocomplete
          v-model="filters.function_location"
          v-bind="$bind.select"
          :loading="loaders.function_locations"
          :items="function_locations"
          clearable
          multiple
        />

        <h4>Title</h4>
        <v-text-field
          v-model="title_text"
          v-bind="$bind.select"
          clearable
          @keyup.native.enter="$event.target.blur()"
          @blur="searchTitleText"
          @click:clear="clearTitleText"
        />

        <h4>Total Event Duration (hrs)</h4>
        {{ display_total_event_duration_range }}
        <v-range-slider
          v-model="filters.event_duration"
          :min="0"
          :max="max_total_event_duration"
          :loading="loaders.max_total_event_duration"
          step="0.1"
          v-bind="$bind.range_slider"
          class="align-center"
          hide-details
        />

        <h4>Total Effective Duration (hrs)</h4>
        {{ display_total_effective_duration_range }}
        <v-range-slider
          v-model="filters.effective_duration"
          :min="0"
          :max="max_total_effective_duration"
          :loading="loaders.max_total_effective_duration"
          step="0.1"
          v-bind="$bind.range_slider"
          class="align-center"
          hide-details
        />

        <h4>Incident Date</h4>
        <div class="d-flex">
          <div class="mr-1">
            <span>From:</span>
            <e-date-field
              v-model="filters.incident_date.min_date"
              v-bind="$bind.textfield"
              :menu-props="{ 'nudge-left': 28 }"
              clearable
            />
          </div>

          <div class="ml-1">
            <span>To:</span>
            <e-date-field
              v-model="filters.incident_date.max_date"
              v-bind="$bind.textfield"
              :menu-props="{ 'nudge-left': 160 }"
              clearable
            />
          </div>
        </div>

        <h4>Owners</h4>
        <user-list-autocomplete
          v-model="filters.owner_ids"
          v-bind="$bind.select"
          :items="users"
          item-text="filter_name"
          item-value="id"
          clearable
          multiple
        />

        <h4>Priority</h4>
        <v-autocomplete
          v-model="filters.priority"
          v-bind="$bind.select"
          :items="['High', 'Medium', 'Low']"
          clearable
          multiple
        />

        <h4>Status</h4>
        <v-autocomplete
          v-model="filters.status"
          v-bind="$bind.select"
          :items="$enums.converter($enums.status)"
          clearable
          multiple
        />

        <h4>Equipment</h4>
        <v-autocomplete
          v-model="filters.equipment_description"
          v-bind="$bind.select"
          :loading="loaders.equipments"
          :items="equipments"
          clearable
          multiple
        />
        <h4>Object Type</h4>
        <v-autocomplete
          v-model="filters.object_type"
          v-bind="$bind.select"
          :loading="loaders.object_type"
          :items="object_types"
          clearable
          multiple
        />
        <h4>Object Part</h4>
        <v-autocomplete
          v-model="filters.object_part_description"
          v-bind="$bind.select"
          :items="object_part_descriptions"
          clearable
          multiple
        />
        <h4>Damage Code</h4>
        <v-autocomplete
          v-model="filters.damage_code"
          v-bind="$bind.select"
          :loading="loaders.damage_code"
          :items="damage_codes"
          clearable
          multiple
        />

        <h4>Cause</h4>
        <v-autocomplete
          v-model="filters.causes"
          v-bind="$bind.select"
          :loading="loaders.causes"
          :items="causes"
          clearable
          multiple
        />

        <h4>Supervisor</h4>
        <user-list-autocomplete
          v-model="filters.supervisor_id"
          v-bind="$bind.select"
          :items="users"
          item-text="filter_name"
          item-value="id"
          clearable
          multiple
        />

        <h4>Last Updated</h4>
        <div class="d-flex">
          <div class="mr-1">
            <span>From:</span>
            <e-date-field
              v-model="filters.updated_date.min_date"
              v-bind="$bind.textfield"
              :menu-props="{ 'nudge-left': 28 }"
              clearable
            />
          </div>

          <div class="ml-1">
            <span>To:</span>
            <e-date-field
              v-model="filters.updated_date.max_date"
              v-bind="$bind.textfield"
              :menu-props="{ 'nudge-left': 160 }"
              clearable
            />
          </div>
        </div>

        <h4>Investigation Closed By</h4>
        <div class="d-flex">
          <div class="mr-1">
            <span>From:</span>
            <e-date-field
              v-model="filters.completion_due_date.min_date"
              v-bind="$bind.textfield"
              :menu-props="{ 'nudge-left': 28 }"
              clearable
            />
          </div>

          <div class="ml-1">
            <span>To:</span>
            <e-date-field
              v-model="filters.completion_due_date.max_date"
              v-bind="$bind.textfield"
              :menu-props="{ 'nudge-left': 160 }"
              clearable
            />
          </div>
        </div>

        <h4>Date Closed</h4>
        <div class="d-flex">
          <div class="mr-1">
            <span>From:</span>
            <e-date-field
              v-model="filters.date_closed.min_date"
              v-bind="$bind.textfield"
              :menu-props="{ 'nudge-left': 28 }"
              clearable
            />
          </div>

          <div class="ml-1">
            <span>To:</span>
            <e-date-field
              v-model="filters.date_closed.max_date"
              v-bind="$bind.textfield"
              :menu-props="{ 'nudge-left': 160 }"
              clearable
            />
          </div>
        </div>

        <h4>Created</h4>
        <div class="d-flex">
          <div class="mr-1">
            <span>From:</span>
            <e-date-field
              v-model="filters.created_date.min_date"
              v-bind="$bind.textfield"
              :menu-props="{ 'nudge-left': 28 }"
              clearable
            />
          </div>

          <div class="ml-1">
            <span>To:</span>
            <e-date-field
              v-model="filters.created_date.max_date"
              v-bind="$bind.textfield"
              :menu-props="{ 'nudge-left': 160 }"
              clearable
            />
          </div>
        </div>
        <h4>Investigation Type</h4>
        <v-autocomplete
          v-model="filters.investigation_type"
          v-bind="$bind.select"
          :items="$enums.converter($enums.investigation_types)"
          clearable
          multiple
        />
      </template>
    </template>
  </filter-table>
</template>

<script>
import { mapGetters } from "vuex";
import StatusEnumIcon from "@/components/Global/StatusEnumIcon";
import PriorityEnumIcon from "@/components/Global/PriorityEnumIcon";
import CopyIconBtn from "@/components/IconBtns/CopyIconBtn.vue";

export default {
  components: {
    CopyIconBtn,
  },
  props: {
    investigation: { Object },
  },
  data() {
    return {
      // loaders
      loaders: {
        damage_codes: false,
        cause_codes: false,
        function_locations: false,
        sites: false,
        departments: false,
        equipments: false,
        object_types: false,
        max_total_effective_duration: false,
        max_total_event_duration: false,
        options: false,
        filters: false,
      },
      // ------------

      total_items: 0,
      options: {
        itemsPerPage: 20,
        sortBy: [],
        sortDesc: [],
      },
      filtersLoading: false,
      loading: false,
      max_total_event_duration: 0,
      max_total_effective_duration: 0,
      // other
      max_lost_tonnes: 0,
      max_effective_duration: 0,
      investigations: [],
      // table
      headers: this.$table_headers.relevant_investigation,
      // filters
      global_text: null,
      title_text: null,
      filters: {
        show_relevant_flag: null,
        global_text: null,
        id: null,
        function_location: [],
        status: [],
        priority: [],
        title: null,
        date_closed: {
          min_date: null,
          max_date: null,
        },
        incident_date: {
          min_date: null,
          max_date: null,
        },
        updated_date: {
          min_date: null,
          max_date: null,
        },
        completion_due_date: {
          min_date: null,
          max_date: null,
        },
        created_date: {
          min_date: null,
          max_date: null,
        },
        owner_ids: [],
        supervisor_id: [],

        site: [],
        department: [],
        equipment_description: [],
        damage_code: [],
        causes: [],
        object_type: [],
        object_part_description: [],
        effective_duration: [],
        event_duration: [],
        investigation_type: [],
      },
    };
  },
  computed: {
    ...mapGetters({
      users: "user/getUsers",
      function_locations: "lists/getFunctionLocations",
      damage_codes: "lists/getDamageCodes",
      causes: "lists/getCauseCodes",
      sites: "lists/getSites",
      departments: "lists/getDepartments",
      equipments: "lists/getEquipments",
      object_types: "lists/getObjectTypes",
      object_part_descriptions: "lists/getObjectParts",
    }),
    filtered_headers() {
      return this.headers;
    },
    display_total_effective_duration_range() {
      const array = this.filters.effective_duration;
      return array[0] + " - " + array[1];
    },
    display_total_event_duration_range() {
      const array = this.filters.event_duration;
      return array[0] + " - " + array[1];
    },
  },
  watch: {
    options: {
      handler() {
        this.loaders.options = true;
        // do not loadData if `filter handler` is triggered (expensive task)
        if (!this.loaders.filter) this.loadData();
      },
      deep: true,
    },
    filters: {
      handler() {
        this.loaders.filter = true;
        // do not loadData if `options handler` is triggered (expensive task)
        if (!this.loaders.options) this.loadData();
      },
      deep: true,
    },
    "investigation.object_type"(newval) {
      // object type is a default filter
      this.filters.object_type = [];
      if (newval) {
        this.filters.object_type.push(this.investigation.object_type);
      }
    },
  },
  mounted() {
    this.updateObjectTypeFilter();
    this.fetchDropDownData();
    if (this.relevant_clicked) {
      this.filters.show_relevant_flag = true;
      this.filters.object_type = [];
      this.filters.object_part_description = [];
    }
  },
  methods: {
    // -----------------------------
    // TABLE DATA
    // -----------------------------
    loadData() {
      let { sortBy, sortDesc, page, itemsPerPage } = this.options;

      if (!page) page = 1;

      let dates = ["date_closed", "incident_date", "updated_date"];
      let X = (v, k) => {
        if (Array.isArray(v)) {
          return v.length > 0 ? true : undefined;
        }

        if (dates.includes(k)) {
          return !!v.min_date || !!v.max_date || undefined;
        }

        return v ? true : undefined;
      };

      let api_filters = {};

      for (let [k, v] of Object.entries(this.filters)) {
        let temp = X(v, k);
        if (temp != undefined) {
          api_filters[k] = v;
        }
      }

      api_filters["blacklist_ids"] = [this.investigation.id];
      api_filters["investigation_id"] = this.investigation.id;
      api_filters["archive_status"] = 2;

      if (!sortBy || sortBy.length == 0) {
        sortBy = ["updated"];
        sortDesc = [true];
      }

      let data = {
        sort_by: sortBy,
        sort_desc: sortDesc,
        filters: api_filters,
      };

      this.loading = true;
      this.$axios
        .$post("/investigation/get_page", data, {
          params: {
            page: page,
            count: itemsPerPage,
          },
        })
        .then((res) => {
          this.total_items = res.count;

          for (let item of res.items) {
            item.created = this.$format.initDate(item.created);
            item.updated = this.$format.initDate(item.updated);
            item.date_due = this.$format.initDate(item.date_due);
            item.event_datetime = this.$format.initDate(item.event_datetime);
            item.date_closed = this.$format.initDate(item.date_closed);
          }

          this.investigations = res.items;

          // ------------------

          // reset loaders
          this.loaders.filter = false;
          this.loaders.options = false;
        })
        .finally(() => (this.loading = false));
    },
    // -----------------------------
    // SELECTED
    // -----------------------------
    updateObjectTypeFilter() {
      // object type is a default filter
      this.filters.object_type = [];
      if (this.investigation.object_type) {
        this.filters.object_type.push(this.investigation.object_type);
      }

      // object part is a default filter
      this.filters.object_part_description = [];
      if (this.investigation.object_part_description) {
        this.filters.object_part_description.push(this.investigation.object_part_description);
      }
    },
    updateSelected(payload) {
      let rel_invs = [];

      for (let rel_id of payload) {
        rel_invs.push({
          investigation_id: this.investigation.id,
          relevent_investigation_id: rel_id,
        });
      }
      this.$axios
        .$put("/investigation/save_relevant", rel_invs, {
          params: { investigation_id: this.investigation.id },
        })
        .then(() => {})
        .catch((err) => {
          console.error(err);
        });
    },
    // -----------------------------
    // DATA TABLE
    // -----------------------------
    clearFilters() {
      this.options = {
        sortBy: [],
        sortDesc: [],
        page: 1,
        itemsPerPage: 20,
      };
      this.filters = {
        show_relevant_flag: null,
        global_text: null,
        id: null,
        function_location: [],
        status: [],
        priority: [],
        title: null,
        date_closed: {
          min_date: null,
          max_date: null,
        },
        incident_date: {
          min_date: null,
          max_date: null,
        },
        updated_date: {
          min_date: null,
          max_date: null,
        },
        completion_due_date: {
          min_date: null,
          max_date: null,
        },
        created_date: {
          min_date: null,
          max_date: null,
        },
        owner_ids: [],
        supervisor_id: [],

        site: [],
        department: [],
        equipment_description: [],
        damage_code: [],
        causes: [],
        object_type: [],
        effective_duration: [0, this.max_total_event_duration],
        event_duration: [0, this.max_total_event_duration],
        investigation_type: [],
      };
    },
    navigate(payload) {
      this.$router.push({
        path: "/investigation",
        query: { id: payload.id },
      });
    },
    copyInvestigationUrl(id) {
      const text = `${window.location.origin}/investigation?id=${id}`;
      navigator.clipboard.writeText(text);
    },
    // -----------------------------
    // FILTER DROPDOWN DATA
    // -----------------------------
    fetchDropDownData() {
      this.loaders.max_total_effective_duration = true;
      this.loaders.max_total_event_duration = true;
      this.$axios
        .$get("/incident/max_total_effective_duration")
        .then((res) => {
          this.max_total_effective_duration = res["max_effective_duration"];
          this.max_total_event_duration = res["max_duration"];
          this.filters.effective_duration = [0, this.max_total_effective_duration];
          this.filters.event_duration = [0, this.max_total_event_duration];
          this.loaders.max_total_effective_duration = false;
          this.loaders.max_total_event_duration = false;
        })
        .catch((err) => {
          console.error(err);
        });
    },
    // -----------------------------
    // GLOBAL TEXT SEARCH FILTER
    // -----------------------------
    searchGlobalText() {
      this.filters.global_text = this.global_text;
    },
    clearGlobalText() {
      this.filters.global_text = null;
    },
    searchTitleText() {
      this.filters.title = this.title_text;
    },
    clearTitleText() {
      this.filters.title = null;
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;

.investigation-title {
  cursor: pointer;

  &:hover {
    text-decoration: underline;
    color: var(--v-primary-base);
  }
}

.investigation-title {
  cursor: pointer;

  &:hover {
    text-decoration: underline;
    color: var(--v-primary-base);
  }
}

::v-deep {
  .wrap-text {
    // background: red !important;
    overflow-wrap: anywhere;
  }
  table thead th.wrap-header {
    word-wrap: break-word;
    white-space: normal;
  }
}

::v-deep {
  .title-cell {
    max-width: 500px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .wrap-text {
    overflow-wrap: anywhere;
  }
  .filter-table > * > table > * > tr > * {
    &:nth-child(-n + 3) {
      position: sticky;
      z-index: 2;
      background: var(--default-background);
    }

    &:nth-child(1) {
      left: 0;
    }

    &:nth-child(2) {
      left: 80px;
    }

    &:nth-child(3) {
      left: 149px;
    }
  }
  .filter-table > * > table > * > tr > th {
    &:nth-child(-n + 3) {
      z-index: 4;
    }
  }
}

::v-deep .filters {
  max-height: calc(100vh - #{$header-height} - #{$stepper-height} - 200px);
  overflow-y: auto;
}

::v-deep .main-card {
  max-height: calc(100vh - #{$header-height} - #{$stepper-height} - 65px);
  overflow-y: auto;
}
</style>
