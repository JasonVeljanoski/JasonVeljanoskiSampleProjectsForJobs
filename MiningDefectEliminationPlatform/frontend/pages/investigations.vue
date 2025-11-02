<template>
  <div class="investigation-root">
    <filter-table
      :loading="loading"
      :headers="headers"
      :items="investigations"
      :options.sync="options"
      :server-items-length="total_items"
      save_key="investigation"
      :filters="filters"
      @clear="clearFilters()"
    >
      <template #card:header>
        <v-btn v-bind="$bind.btn" @click="$router.push('/investigation')">
          <v-icon left>mdi-application-edit-outline</v-icon>
          New Investigation
        </v-btn>
      </template>

      <!-- CARD TITLE -->
      <template #card:title>
        <span>
          Investigations
          <span v-show="filters.show_mine">for {{ $auth.user.name }}</span>
        </span>
      </template>

      <!-- DATA TABLE SLOTS -->
      <template #item.id="{ item }">
        <copy-icon-btn :id="item.id" @copy="copyInvestigationUrl(item.id)" />
      </template>

      <template #item.investigation_type="{ item }">
        <investigation-type-icon :value="item.investigation_type" :has_completed_rca="hasCompleteRCA(item)" />
      </template>

      <template #item.is_archived="{ item }">
        <archive-toggle
          :value="item.is_archived"
          :disabled="!hasArchivePerms(item.owner_ids, item.supervisor_id)"
          @toggle="updateArchiveStatus(item.id, item.is_archived)"
        />
      </template>

      <template #item.investigation="{ item }">
        <e-icon-btn tooltip="Investigation Link" @click="clickInvest(item)"> mdi-application-edit-outline </e-icon-btn>
      </template>
      <template #item.actions="{ item }">
        <!-- <e-icon-btn tooltip="Actions Link" :to="`/actions?id=${item.id}`">
            mdi-clock-fast
          </e-icon-btn> -->

        <v-badge
          v-if="item.actions_number != 0"
          color="primary"
          overlap
          offset-x="13"
          offset-y="15"
          :value="item.actions_number.toString()"
          :content="item.actions_number.toString()"
        >
          <template v-slot:badge>
            <span class="white--text">{{ item.actions_number }}</span>
          </template>
          <e-icon-btn :tooltip="'Actions Link'" :to="`/actions?id=${item.id}`"> mdi-clock-fast </e-icon-btn>
        </v-badge>
        <e-icon-btn v-else :tooltip="'Actions Link'" :to="`/actions?id=${item.id}`"> mdi-clock-fast </e-icon-btn>
      </template>

      <template #item.title="{ item }">
        <title-hover-text :main_text="item.title" :sub_text="item.description" @click="clickInvest(item)" />
      </template>

      <!-- FILTER SLOTS -->
      <template #filters>
        <v-checkbox
          v-model="filters.show_mine"
          label="Only Relevant To Me"
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

        <h4>Status</h4>
        <v-autocomplete
          v-model="filters.status"
          v-bind="$bind.select"
          :items="$enums.converter($enums.status)"
          clearable
          multiple
        />

        <h4>Site</h4>
        <v-autocomplete v-model="filters.site" v-bind="$bind.select" :items="sites" clearable multiple />

        <h4>Department</h4>
        <v-autocomplete v-model="filters.department" v-bind="$bind.select" :items="departments" clearable multiple />

        <h4>FLOC</h4>
        <v-autocomplete
          v-model="filters.function_location"
          v-bind="$bind.select"
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
        <div class="d-flex" style="width: 200px">
          <v-text-field
            :value="filters.event_duration[0]"
            class="mt-0 pt-0"
            hide-details
            single-line
            type="number"
            dense
            style="width: 50px"
            @change="changeInput($event, 'event', 0)"
            :key="key + 4"
          />
          <h4>&nbsp&nbsp&nbsp&nbspto&nbsp&nbsp&nbsp&nbsp</h4>
          <v-text-field
            :value="filters.event_duration[1]"
            class="mt-0 pt-0"
            hide-details
            single-line
            type="number"
            dense
            style="width: 80px"
            @change="changeInput($event, 'event', 1)"
            :key="key + 5"
          />
        </div>
        <v-range-slider
          v-if="max_total_event_duration"
          v-model="filters.event_duration"
          :min="0"
          :max="max_total_event_duration"
          :loading="loaders.max_total_event_duration"
          step="10"
          v-bind="$bind.range_slider"
          class="align-center"
          hide-details
          @mouseup="loadData()"
          :key="key"
        />

        <h4>Total Effective Duration (hrs)</h4>
        <div class="d-flex" style="width: 200px">
          <v-text-field
            :value="filters.effective_duration[0]"
            step="1"
            class="mt-0 pt-0"
            type="number"
            hide-details
            single-line
            dense
            style="width: 50px"
            @change="changeInput($event, 'effect', 0)"
            :key="key + 2"
          />
          <h4>&nbsp&nbsp&nbsp&nbspto&nbsp&nbsp&nbsp&nbsp</h4>
          <v-text-field
            :value="filters.effective_duration[1]"
            step="1"
            class="mt-0 pt-0"
            type="number"
            hide-details
            single-line
            dense
            style="width: 80px"
            @change="changeInput($event, 'effect', 1)"
            :key="key + 3"
          />
        </div>
        <v-range-slider
          v-if="max_total_effective_duration"
          v-model="filters.effective_duration"
          :min="0"
          :max="max_total_effective_duration"
          :loading="loaders.max_total_effective_duration"
          step="1"
          v-bind="$bind.range_slider"
          class="align-center"
          hide-details
          @mouseup="loadData()"
          :key="key + 1"
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

        <h4>Equipment</h4>
        <v-autocomplete
          v-model="filters.equipment_description"
          v-bind="$bind.select"
          :items="equipments"
          clearable
          multiple
        />
        <h4>Object Type</h4>
        <v-autocomplete v-model="filters.object_type" v-bind="$bind.select" :items="object_types" clearable multiple />
        <h4>Object Part</h4>
        <v-autocomplete
          v-model="filters.object_part_description"
          v-bind="$bind.select"
          :items="object_part_descriptions"
          clearable
          multiple
        />
        <h4>Damage Code</h4>
        <v-autocomplete v-model="filters.damage_code" v-bind="$bind.select" :items="damage_codes" clearable multiple />

        <h4>Cause</h4>
        <v-autocomplete v-model="filters.causes" v-bind="$bind.select" :items="causes" clearable multiple />

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

        <h4>Completed Steps</h4>
        {{ $enums.completed_steps[filters.completed_steps[0]] }} to
        {{ $enums.completed_steps[filters.completed_steps[1]] }}
        <v-range-slider
          v-model="filters.completed_steps"
          :tick-labels="[1, 2, 3, 4, 5, 6]"
          :value="[1, 6]"
          min="1"
          max="6"
          ticks="always"
          tick-size="4"
        />

        <h4>Investigation Type</h4>
        <v-autocomplete
          v-model="filters.investigation_type"
          v-bind="$bind.select"
          :items="$enums.converter($enums.investigation_types)"
          clearable
          multiple
        />

        <h4>Archive Status</h4>
        <v-autocomplete
          v-model="filters.archive_status"
          v-bind="$bind.select"
          :items="$enums.converter($enums.archive_status)"
          item-text="text"
          item-value="value"
          clearable
        />
      </template>
    </filter-table>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import CopyIconBtn from "@/components/IconBtns/CopyIconBtn.vue";
import ArchiveToggle from "@/components/IconBtns/ArchiveToggle.vue";
import InvestigationTypeIcon from "@/components/Investigation/Investigation/InvestigationTypeIcon.vue";

export default {
  head() {
    return {
      title: "Investigations",
    };
  },
  components: {
    CopyIconBtn,
    ArchiveToggle,
    InvestigationTypeIcon,
  },
  data() {
    return {
      // loaders
      key: 0,
      loading: false,
      loaders: {
        max_total_effective_duration: true,
        max_total_event_duration: true,
        archive_status: false,
        options: false,
        filters: false,
      },
      // ---------
      total_items: 0,
      options: {
        itemsPerPage: 20,
        sortBy: [],
        sortDesc: [],
      },
      max_total_effective_duration: null,
      max_total_event_duration: null,

      // other
      selected: {
        status: null,
        investigation_ids: [],
      },

      status: [
        { text: "Complete", value: 1 },
        { text: "Incomplete", value: -1 },
      ],
      investigations: [],

      // table
      headers: this.$table_headers.investigation,

      // filters
      global_text: null,
      title_text: null,
      filters: {
        show_mine: false,
        global_text: null,
        id: null,
        archive_status: 2, // archive_status is a default filter
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
        function_location: [],
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
        completed_steps: [1, 6],
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
    display_total_effective_duration_range() {
      const array = this.filters.effective_duration;
      return array[0] + " - " + array[1];
    },
    display_total_event_duration_range() {
      const array = this.filters.event_duration;
      return array[0] + " - " + array[1];
    },
    is_unique_investigation() {
      const query = this.$route.query;
      return Object.keys(query).includes("id");
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
      handler(newV, old) {
        this.loaders.filter = true;
        if (!this.loaders.options) this.loadData();
      },
      deep: true,
    },
    "$route.query"() {
      // if /investigations?id=1 then user clicks menu to go to /investigations, must repopulate table
      this.loadData();
    },
  },
  created() {
    this.fetchDropDownData();
  },
  mounted() {
    this.initTextSearch();
  },
  methods: {
    changeInput(value, name, index) {
      // data process when value is empty
      if (value == "" && index == 0) value = 0;
      if (value == "" && index == 1) {
        if (name == "event") value = this.max_total_event_duration;
        else value = this.max_total_effective_duration;
      }

      value = parseInt(value);
      // when data less than 0
      if (value < 0) value = 0;
      if (name == "event") {
        // when data greater than max
        if (value > this.max_total_event_duration) value = this.max_total_event_duration;
        // data assignment
        this.filters.event_duration[index] = parseInt(value);
      } else if (name == "effect") {
        // bounds
        if (value > this.max_total_effective_duration) value = this.max_total_effective_duration;
        if (value < 0) value = 0;
        // data assignment
        this.filters.effective_duration[index] = parseInt(value);
      }
      this.key++;
      this.loadData();
    },
    clickInvest(item) {
      let routeData = this.$router.resolve({
        path: `/investigation?id=${item.id}`,
        // query: {'dataParameter': 'parameterValue'}
      });
      window.open(routeData.href, "_blank");
    },
    // -----------------------------
    // TABLE DATA
    // -----------------------------
    async loadData() {
      const query = this.$route.query;
      if (this.is_unique_investigation) {
        this.filterInvestigationFromInvestigationID(query.id);
        return;
      }

      // ------------------------------

      // inits
      let { sortBy, sortDesc, page, itemsPerPage } = this.options;
      let dates = ["date_closed", "incident_date", "updated_date"];
      if (!page) page = 1;

      // formatter
      let X = (v, k) => {
        if (Array.isArray(v)) {
          return v.length > 0 ? true : undefined;
        }

        if (dates.includes(k)) {
          return !!v.min_date || !!v.max_date || undefined;
        }

        return v ? true : undefined;
      };

      // ------------------------------

      // api filters
      let api_filters = {};

      // standard users can only see non-archived items, admins can see everything
      if (!this.$perms.is_admin) api_filters["archive_status"] = 2;

      for (let [k, v] of Object.entries(this.filters)) {
        let temp = X(v, k);
        if (temp != undefined) {
          api_filters[k] = v;
        }
      }

      // ------------------------------
      // sorter
      if (!sortBy || sortBy.length == 0) {
        sortBy = ["event_datetime"];
        sortDesc = [true];
      }

      // payload and route
      let data = {
        sort_by: sortBy,
        sort_desc: sortDesc,
        filters: api_filters,
      };

      this.loading = true;
      await this.$axios
        .$post("/investigation/get_page", data, {
          params: {
            page: page,
            count: itemsPerPage,
          },
        })
        .then((res) => {
          this.total_items = res.count;

          this.processInvestigations(res.items);

          // ------------------

          // reset loaders
          this.loaders.filter = false;
          this.loaders.options = false;
        })
        .finally(() => (this.loading = false));
    },

    // -----------------------------
    // IMPORT DATA
    // -----------------------------
    processInvestigations(investigations) {
      for (let item of investigations) {
        item.created = this.$format.initDate(item.created);
        item.updated = this.$format.initDate(item.updated);
        item.date_due = this.$format.initDate(item.date_due);
        item.event_datetime = this.$format.initDate(item.event_datetime);
        item.date_closed = this.$format.initDate(item.date_closed);
      }
      this.investigations = investigations;
    },
    filterInvestigationFromInvestigationID(investigation_id) {
      this.loading = true;
      this.$axios
        .$get("/investigation", { params: { id: investigation_id } })
        .then((res) => {
          this.processInvestigations([res]);
          this.total_items = 1;
          this.loading = false;
        })
        .catch((err) => console.error(err));
    },
    // -----------------------------
    // DATA TABLE
    // -----------------------------
    copyInvestigationUrl(id) {
      const text = `${window.location.origin}/investigation?id=${id}`;
      navigator.clipboard.writeText(text);
    },
    clearFilters() {
      this.options = {
        sortBy: [],
        sortDesc: [],
        page: 1,
        itemsPerPage: 20,
      };

      // text
      this.global_text = null;

      this.filters = {
        show_relevant_flag: null,
        global_text: null,
        id: null,
        archive_status: 2,
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
        effective_duration: [0, this.max_total_effective_duration],
        event_duration: [0, this.max_total_event_duration],
        investigation_type: [],
        completed_steps: [1, 6],
      };
    },
    editInvestigation(investigation) {
      investigation.created = this.$format.initDate(investigation.created);
      investigation.updated = this.$format.initDate(investigation.updated);
      investigation.date_closed = this.$format.initDate(investigation.date_closed);
      investigation.event_datetime = this.$format.initDate(investigation.event_datetime);
      investigation.completion_due_date = this.$format.initDate(investigation.completion_due_date);

      this.$refs.edit_investigation.open(investigation);
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

          // set default values if needed
          if (this.filters.effective_duration[1] == null || this.filters.effective_duration[1] == 0)
            this.filters.effective_duration = [0, this.max_total_effective_duration];
          if (this.filters.event_duration[1] == null || this.filters.event_duration[1] == 0)
            this.filters.event_duration = [0, this.max_total_event_duration];

          // loaders
          this.loaders.max_total_effective_duration = false;
          this.loaders.max_total_event_duration = false;
        })
        .catch((err) => {
          console.error(err);
        });
    },
    // -----------------------------
    // TEXT SEARCH FILTER
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
    initTextSearch() {
      this.global_text = this.filters.global_text;
      this.title_text = this.filters.title;
    },
    // -----------------------------
    // ARCHIVE STATUS
    // -----------------------------
    updateArchiveStatus(id, is_archived) {
      const change_status = !(is_archived || false);

      // update process
      this.loaders.archive_status = true;
      this.$axios
        .$patch("/investigation/update_archive_status", null, {
          params: {
            investigation_id: id,
            is_archived: change_status,
          },
        })
        .then(() => {
          let idx = this.investigations.findIndex((x) => x.id == id);
          this.investigations[idx].is_archived = change_status;
          this.loaders.archive_status = false;
        })
        .catch((err) => {
          console.error(err);
        });
    },
    hasArchivePerms(owner_ids, supervisor_id) {
      const uid = this.$auth.user.id;
      return this.$perms.is_admin || owner_ids.includes(uid) || supervisor_id == uid;
    },
    hasCompleteRCA(item) {
      return !item.has_completed_rca && item.investigation_type == 2;
    },
  },
};
</script>

<style lang="scss" scoped>
.investigation-title {
  cursor: pointer;

  &:hover {
    text-decoration: underline;
    color: var(--v-primary-base);
  }
}

.investigation-root {
  height: 100%;

  ::v-deep {
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
        left: 69px;
      }

      &:nth-child(3) {
        left: 172px;
      }
    }
    .filter-table > * > table > * > tr > th {
      &:nth-child(-n + 3) {
        z-index: 4;
      }
    }
  }
}
</style>
