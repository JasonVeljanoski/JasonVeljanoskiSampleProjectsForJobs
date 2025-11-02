<template>
  <div class="actions-root">
    <filter-table
      :loading="loading"
      :headers="headers"
      :items="actions"
      :options.sync="options"
      :server-items-length="total_items"
      save_key="action"
      :filters="filters"
      @clear="clearFilters()"
    >
      <!-- CARD TITLE -->
      <template #card:title>
        <span>
          Actions
          <span v-show="filters.show_mine">for {{ $auth.user.name }}</span>
        </span>
      </template>

      <!-- DATA -->
      <template #item.id="{ item }">
        <copy-icon-btn :id="item.id" @copy="copyActionUrl(item.id)" />
      </template>

      <template #item.source="{ item }">
        <v-chip v-if="item.flash_report_id" color="secondary">
          <b>Flash Report</b>
        </v-chip>
        <v-chip v-else-if="item.five_why_id" color="secondary">
          <b>5-Why</b>
        </v-chip>
        <v-chip v-else-if="item.root_cause_detail_id" color="secondary">
          <b>Root Cause</b>
        </v-chip>
      </template>

      <template #item.is_archived="{ item }">
        <archive-toggle
          :value="item.is_archived"
          :disabled="
            !hasArchivePerms(
              item.owner_ids,
              item.supervisor_id,
              item.investigation_owner_ids
            )
          "
          @toggle="updateArchiveStatus(item.id, item.is_archived)"
        />
      </template>

      <template #item.investigation="{ item }">
        <v-tooltip bottom max-width="300">
          <template v-slot:activator="{ on, attrs }">
            <span
              v-bind="attrs"
              v-on="on"
              class="investigation-title"
              @click="navigate(item)"
            >
              {{ item.investigation_title }}
            </span>
          </template>
          <span>{{ item.investigation_description }}</span>
        </v-tooltip>
      </template>
      <template #item.edit="{ item }">
        <e-icon-btn tooltip="Edit Action" @click="editAction(item)">
          mdi-pencil
        </e-icon-btn>
      </template>
      <template #item.image="{ item }">
        <v-tooltip v-if="item.files.length" content-class="tooltip" left>
          <template v-slot:activator="{ on, attrs }">
            <v-img width="40" :src="item.files[0]" v-on="on" />
          </template>
          <div v-for="(img, i) in item.files" :key="i">
            <v-img :src="img" />
          </div>
        </v-tooltip>
      </template>
      <template #item.title="{ item }">
        <title-hover-text
          :main_text="item.title"
          :sub_text="item.description"
        />
      </template>

      <!-- FILTER -->
      <template #filters>
        <div v-if="loaders.filters" class="d-flex justify-center">
          <v-progress-circular
            v-if="loaders.filters"
            indeterminate
            color="primary"
          />
        </div>

        <template v-else>
          <v-checkbox
            v-model="filters.show_mine"
            :disabled="change_status_flag"
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

          <h4># Action Number</h4>
          <v-text-field
            v-model="filters.id"
            v-bind="$bind.select"
            type="number"
            clearable
          />

          <!-- <h4>FLOC</h4>
          <v-autocomplete
            v-model="filters.function_location"
            v-bind="$bind.select"
            :items="function_locations"
            clearable
            multiple
          /> -->
          <h4>Status</h4>
          <v-autocomplete
            v-model="filters.status"
            v-bind="$bind.select"
            :items="$enums.converter($enums.status)"
            clearable
            multiple
          />

          <h4>Site</h4>
          <v-autocomplete
            v-model="filters.site"
            v-bind="$bind.select"
            :items="sites"
            clearable
            multiple
          />

          <h4>Department</h4>
          <v-autocomplete
            v-model="filters.department"
            v-bind="$bind.select"
            :items="departments"
            clearable
            multiple
          />

          <h4>Source</h4>
          <v-autocomplete
            v-model="filters.source"
            v-bind="$bind.select"
            :items="$enums.action_source"
            clearable
            multiple
          />

          <h4>Priority</h4>
          <v-autocomplete
            v-model="filters.priority"
            v-bind="$bind.select"
            :items="$enums.priority"
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

          <h4>Owner or Member</h4>
          <user-list-autocomplete
            v-model="filters.owner_member_ids"
            v-bind="$bind.select"
            :items="users"
            item-text="filter_name"
            item-value="id"
            clearable
            multiple
          />

          <h4>Date Due</h4>
          <div class="d-flex">
            <div class="mr-1">
              <span>From:</span>
              <e-date-field
                v-model="filters.date_due.min_date"
                v-bind="$bind.textfield"
                :menu-props="{ 'nudge-left': 28 }"
                clearable
              />
            </div>

            <div class="ml-1">
              <span>To:</span>
              <e-date-field
                v-model="filters.date_due.max_date"
                v-bind="$bind.textfield"
                :menu-props="{ 'nudge-left': 160 }"
                clearable
              />
            </div>
          </div>

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

          <h4>Date Created</h4>
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
        </template>

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

    <action-table-form
      ref="action_table_form"
      :action="action"
      @add_action="addAction($event)"
    />
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import ArchiveToggle from "@/components/IconBtns/ArchiveToggle.vue";
import ActionTableForm from "@/components/Investigation/Actions/ActionTableForm";
import CopyIconBtn from "@/components/IconBtns/CopyIconBtn.vue";

export default {
  name: "Actions",
  components: {
    ArchiveToggle,
    ActionTableForm,
    CopyIconBtn,
  },
  head() {
    return {
      title: "Actions",
    };
  },
  data() {
    return {
      loading: false,
      loaders: {
        filters: false,
        archive_status: false,
        options: false,
        filters: false,
      },
      total_items: 0,
      options: {
        itemsPerPage: 20,
        sortBy: [],
        sortDesc: [],
      },
      change_status_flag: false,
      action: null,
      actions: [],
      headers: this.$table_headers.action,
      // filters
      global_text: null,
      title_text: null,
      filters: {
        show_mine: false,
        global_text: null,
        id: null,
        function_location: [],
        site: [],
        department: [],
        status: [],
        source: [],
        priority: [],
        date_closed: {
          min_date: null,
          max_date: null,
        },
        date_due: {
          min_date: null,
          max_date: null,
        },
        date_closed: {
          min_date: null,
          max_date: null,
        },
        created_date: {
          min_date: null,
          max_date: null,
        },
        updated_date: {
          min_date: null,
          max_date: null,
        },
        title: null,
        description: null,
        owner_member_ids: [],
        supervisor_id: [],
        archive_status: 2,
      },
    };
  },
  computed: {
    ...mapGetters({
      users: "user/getUsers",
      function_locations: "lists/getFunctionLocations",
      sites: "lists/getSites",
      departments: "lists/getDepartments",
    }),
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
    action() {
      this.action.created = this.$format.initDate(this.action.created);
      this.action.date_due = this.$format.initDate(this.action.date_due);
    },
    "$route.query"() {
      this.loadData();
    },
  },
  mounted() {
    this.initTextSearch();
  },
  methods: {
    // -----------------------------
    // TABLE DATA
    // -----------------------------
    loadData() {
      const query = this.$route.query;
      if (Object.keys(query).includes("id")) {
        this.filterActionsFromInvestigationID(query.id);

        return;
      } else if (Object.keys(query).includes("action_id")) {
        this.filterActionsFromActionID(query.action_id);
        return;
      }

      // ---------------------------------------

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

      // standard users can only see non-archived items, admins can see everything
      if (!this.$perms.is_admin) api_filters["archive_status"] = 2;

      for (let [k, v] of Object.entries(this.filters)) {
        let temp = X(v, k);
        if (temp != undefined) {
          api_filters[k] = v;
        }
      }

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
        .$post("/action/get_page", data, {
          params: {
            page: page,
            count: itemsPerPage,
          },
        })
        .then((res) => {
          this.total_items = res.count;
          this.processInitActions(res.items);

          // ------------------

          // reset loaders
          this.loaders.filter = false;
          this.loaders.options = false;
        })
        .finally(() => (this.loading = false));
    },
    navigate(payload) {
      this.$router.push({
        path: "/investigation",
        query: { id: payload.investigation_id },
      });
    },

    // -----------------------------
    // POPULATE
    // -----------------------------
    processInitActions(actions) {
      for (let action of actions) {
        action.created = this.$format.initDate(action.created);
        action.updated = this.$format.initDate(action.updated);
        action.date_due = this.$format.initDate(action.date_due);
        action.date_closed = this.$format.initDate(action.date_closed);
      }

      this.actions = actions;
    },
    filterActionsFromActionID(action_id) {
      this.loading = true;
      this.$axios
        .$get("/action", { params: { action_id: action_id } })
        .then((res) => {
          this.processInitActions(res);
          this.total_items = res.length;
          this.loading = false;
        })
        .catch((err) => console.error(err));
    },
    filterActionsFromInvestigationID(investigation_id) {
      this.loading = true;
      this.$axios
        .$get("/action/investigation_id", {
          params: { investigation_id: investigation_id },
        })
        .then((res) => {
          this.processInitActions(res);
          this.total_items = res.length;
          this.loading = false;
        })
        .catch((err) => console.error(err));
    },
    // -----------------------------
    // ACTIONS
    // -----------------------------
    copyActionUrl(id) {
      const text = `${window.location.origin}/actions?action_id=${id}`;
      navigator.clipboard.writeText(text);
    },
    editAction(action) {
      action.created = this.$format.initDate(action.created);
      action.updated = this.$format.initDate(action.updated);
      action.date_due = this.$format.initDate(action.date_due);
      action.date_closed = this.$format.initDate(action.date_closed);
      this.$refs.action_table_form.open(action);
    },
    addAction(payload) {
      this.loading = true;

      // ---------------------------
      // handle attachments + its metadata (sending attachments through pydantic sucks...)

      const form_data = new FormData();

      const attachments = payload.attachments;
      let files_metadatas = [];
      for (let attachment of attachments) {
        files_metadatas.push({
          title: attachment.title,
          description: attachment.description,
          network_drive_link: attachment.network_drive_link,
        });

        form_data.append("attachments", attachment.file);
      }

      let action = payload.action;
      action.genertal_attachments_metas = files_metadatas;
      form_data.append("action", JSON.stringify(action));

      // ----------------------------

      this.$axios
        .$put("/action", form_data)
        .then((res) => {
          res.created = this.$format.initDate(res.created);
          res.updated = this.$format.initDate(res.updated);
          res.date_due = this.$format.initDate(res.date_due);
          res.date_closed = this.$format.initDate(res.date_closed);

          let idx = this.actions.findIndex((x) => x.id == action.id);

          // i dont know why this works but it does
          let actions = JSON.parse(JSON.stringify(this.actions));
          actions[idx] = res; // JSON.parse(JSON.stringify(action));
          this.actions = actions;

          // --------------------------------

          if (res.flash_report_id)
            this.$document
              .create_flash_report(res.investigation_id)
              .catch((err) => console.error(err));
          else if (res.five_why_id)
            this.$document
              .create_five_why_report(res.investigation_id)
              .catch((err) => console.error(err));

          this.$document
            .create_shared_learnings_report(res.investigation_id)
            .catch((err) => console.error(err));

          // --------------------------------

          this.loading = false;
          this.dialog = false;
        })
        .catch((err) => {
          console.error(err);
        });
    },
    // -----------------------------
    // FILTERS
    // -----------------------------
    clearFilters() {
      this.change_status_flag = false;

      this.options = {
        sortBy: [],
        sortDesc: [],
        page: 1,
        itemsPerPage: 20,
      };

      // text
      this.global_text = null;

      this.filters = {
        show_mine: false,
        global_text: null,
        id: null,
        function_location: [],
        site: [],
        department: [],
        status: [],
        source: [],
        priority: [],
        date_closed: {
          min_date: null,
          max_date: null,
        },
        date_due: {
          min_date: null,
          max_date: null,
        },
        date_closed: {
          min_date: null,
          max_date: null,
        },
        created_date: {
          min_date: null,
          max_date: null,
        },
        updated_date: {
          min_date: null,
          max_date: null,
        },
        title: null,
        description: null,
        owner_member_ids: [],
        supervisor_id: [],
        archive_status: 2,
      };
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
      this.loading = true;
      this.$axios
        .$patch("/action/update_archive_status", null, {
          params: {
            action_id: id,
            is_archived: change_status,
          },
        })
        .then(() => {
          const idx = this.actions.findIndex((x) => x.id == id);
          this.actions[idx].is_archived = change_status;

          // --------------------------------------------

          const action = this.actions[idx];

          if (action.flash_report_id)
            this.$document
              .create_flash_report(action.investigation_id)
              .catch((err) => console.error(err));
          else if (action.five_why_id)
            this.$document
              .create_five_why_report(action.investigation_id)
              .catch((err) => console.error(err));

          this.$document
            .create_shared_learnings_report(action.investigation_id)
            .catch((err) => console.error(err));

          // --------------------------------------------

          this.loading = false;
        })
        .catch((err) => {
          console.error(err);
        });
    },
    hasArchivePerms(owner_ids, supervisor_id, investigation_owner_ids) {
      const uid = this.$auth.user.id;
      return (
        this.$perms.is_admin ||
        owner_ids.includes(uid) ||
        supervisor_id == uid ||
        investigation_owner_ids.includes(uid)
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.actions-root {
  height: 100%;

  ::v-deep {
    .wrap-text {
      overflow-wrap: anywhere;
    }
    .filter-table > * > table > * > tr > * {
      &:nth-child(-n + 2) {
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
    }
    .filter-table > * > table > * > tr > th {
      &:nth-child(-n + 2) {
        z-index: 4;
      }
    }
  }
}

.investigation-title {
  cursor: pointer;

  &:hover {
    text-decoration: underline;
    color: var(--v-primary-base);
  }
}

.tooltip {
  padding: 5px;
}
</style>
