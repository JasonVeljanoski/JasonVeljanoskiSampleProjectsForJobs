<template>
  <div class="feedback-root">
    <div class="feedback-root">
      <filter-table
        :loading="loading"
        :headers="headers"
        :items="feedback_items"
        :options.sync="options"
        :server-items-length="total_items"
        title="Feedback"
        @dblclick:row="onRowDoubleClick"
        @clear="clearFilters()"
      >
        <!-- DATA TABLE SLOTS -->
        <template #item.id="{ item }">
          <copy-icon-btn :id="item.id" @copy="copyFeedbackUrl(item.id)" />
        </template>

        <template #item.edit="{ item }">
          <e-icon-btn tooltip="Edit Feedback" @click="editFeedback(item)"> mdi-pencil </e-icon-btn>
        </template>

        <!-- FILTER SLOTS -->
        <template #filters>
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

          <h4>Reason</h4>
          <v-autocomplete
            v-model="filters.reason"
            v-bind="$bind.select"
            :items="$enums.converter($enums.feedback_types)"
            item-text="text"
            item-value="value"
            clearable
            multiple
          />

          <h4>Status</h4>
          <v-autocomplete
            v-model="filters.status"
            v-bind="$bind.select"
            :items="$enums.converter($enums.feedback_status)"
            clearable
            multiple
          />

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

          <h4>Updated</h4>
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

          <template v-if="$perms.is_admin">
            <h4>Owner</h4>
            <user-list-autocomplete
              v-model="filters.owner_id"
              v-bind="$bind.select"
              :items="users"
              item-text="filter_name"
              item-value="id"
              clearable
              multiple
            />
          </template>
        </template>
      </filter-table>
    </div>

    <!-- ENTRY FORM -->
    <feedback-form ref="feedback_form" @add_feedback="submitFeedback($event)" />
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import FeedbackEnumIcon from "@/components/Global/FeedbackEnumIcon";
import FeedbackForm from "@/components/Feedback/FeedbackForm";
import FeedbackStatusIcon from "@/components/Global/FeedbackStatusIcon";
import CopyIconBtn from "@/components/IconBtns/CopyIconBtn.vue";

export default {
  components: {
    FeedbackEnumIcon,
    FeedbackForm,
    FeedbackStatusIcon,
    CopyIconBtn,
  },
  head() {
    return {
      title: "Feedback",
    };
  },
  data() {
    return {
      loading: false,
      total_items: 0,
      options: {
        itemsPerPage: 20,
        sortBy: [],
        sortDesc: [],
      },

      // table
      feedback_items: [],
      headers: [
        {
          text: "#",
          align: "center",
          value: "id",
          sortable: false,
          divider: true,
          hide: false,
          width: "10",
        },
        {
          text: "Edit",
          value: "edit",
          width: "20",
          align: "center",
          divider: true,
          sortable: false,
          hide: false,
          width: "10",
          divider: true,
        },
        {
          text: "Reason",
          value: "reason",
          hide: false,
          divider: true,
          cellClass: "wrap-text",
          width: "10",
          align: "center",
          component: FeedbackEnumIcon,
        },
        {
          text: "Status",
          value: "status",
          divider: true,
          align: "center",
          component: FeedbackStatusIcon,
          hide: false,
          width: "10",
        },
        {
          text: "Created",
          value: "created",
          formatter: (x) => this.$format.date(x),
          hide: false,
          divider: true,
          width: "10",
        },
        {
          text: "Last Updated",
          value: "updated",
          formatter: (x) => this.$format.date(x),
          hide: false,
          divider: true,
          width: "10",
        },
        {
          text: "Created By",
          value: "created_by_id",
          formatter: (x) => this.$utils.getUserName(x),
          hide: false,
          divider: true,
          width: "150",
        },
        {
          text: "Last Updated By",
          value: "updated_by_id",
          formatter: (x) => this.$utils.getUserName(x),
          hide: false,
          divider: true,
          width: "150",
        },
        {
          text: "Title",
          value: "title",
          hide: false,
          divider: true,
          cellClass: "wrap-text",
          width: "320",
        },
        {
          text: "Issue relates to",
          value: "page",
          hide: false,
          divider: true,
          cellClass: "wrap-text",
          width: "320",
        },
        {
          text: "Summary",
          value: "summary",
          hide: false,
          divider: true,
          cellClass: "wrap-text",
          width: "450",
        },
        {
          text: "How to Replicate",
          value: "replicate",
          hide: false,
          divider: true,
          cellClass: "wrap-text",
          width: "900",
        },
      ],

      // filters
      global_text: null,
      filters: {
        global_text: null,
        id: null,
        reason: [],
        status: [],
        created_date: {
          min_date: null,
          max_date: null,
        },
        updated_date: {
          min_date: null,
          max_date: null,
        },
        owner_id: null,
        page: null,
        replicate: null,
      },
    };
  },
  computed: {
    ...mapGetters({
      users: "user/getUsers",
    }),
  },
  watch: {
    options: {
      handler() {
        this.loadData();
      },
      deep: true,
    },
    filters: {
      handler() {
        this.loadData();
      },
      deep: true,
    },
    "$route.query"() {
      // if /feedback?id=1 then user clicks menu to go to /feedback, must repopulate table
      this.loadData();
    },
  },
  created() {
    this.$nuxt.$on("force_load_data_update", () => {
      this.loadData();
    });
  },
  beforeDestroy() {
    this.$nuxt.$off("open-contact-form");
  },
  methods: {
    // -----------------------------
    // TABLE DATA
    // -----------------------------
    processFeedbackItems(items) {
      this.feedback_items = items;
    },
    filterFeedbacksByID(id) {
      this.loading = true;
      this.$axios
        .$get("/feedback", { params: { id: id } })
        .then((res) => {
          this.processFeedbackItems(res);
          this.total_items = res.length;
          this.loading = false;
        })
        .catch((err) => console.error(err));
    },
    loadData() {
      const query = this.$route.query;
      if (Object.keys(query).includes("id")) {
        this.filterFeedbacksByID(query.id);
        return;
      }

      // ------------------------------------------

      let { sortBy, sortDesc, page, itemsPerPage } = this.options;

      if (!page) page = 1;

      let dates = ["created", "updated"];
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
        .$post("/feedback/get_page", data, {
          params: {
            page: page,
            count: itemsPerPage,
          },
        })
        .then((res) => {
          this.total_items = res.count;

          this.processFeedbackItems(res.items);
        })
        .finally(() => (this.loading = false));
    },
    // -----------------------------
    // FILTERS
    // -----------------------------
    clearFilters() {
      this.options = {
        sortBy: [],
        sortDesc: [],
        page: 1,
        itemsPerPage: 20,
      };

      this.global_text = null;

      this.filters = {
        id: null,
        reason: [],
        status: [],
        created_date: {
          min_date: null,
          max_date: null,
        },
        updated_date: {
          min_date: null,
          max_date: null,
        },
        owner_id: null,
        page: null,
        replicate: null,
      };
    },
    // -----------------------------
    // FEEDBACK
    // -----------------------------
    onRowDoubleClick(_, payload) {
      this.editFeedback(payload.item);
    },
    editFeedback(feedback) {
      if (feedback) this.$refs.feedback_form.open(feedback);
    },
    submitFeedback(payload) {
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

      let feedback = payload.feedback;
      feedback.general_attachments_metas = files_metadatas;
      form_data.append("edits", JSON.stringify(feedback));

      // ----------------------------

      this.$axios
        .$put("feedback", form_data)
        .then((res) => {
          res.created = this.$format.initDate(res.created);
          res.updated = this.$format.initDate(res.updated);

          let idx = this.feedback_items.findIndex((x) => x.id == res.id);

          if (idx != -1) this.feedback_items.splice(idx, 1);

          this.feedback_items.unshift(res);

          this.$snackbar.add(`Feedback Item #${res.id} Updated`);
          this.loading = false;
        })
        .catch((err) => console.error(err));
    },
    copyFeedbackUrl(id) {
      const text = `${window.location.origin}/feedback?id=${id}`;
      navigator.clipboard.writeText(text);
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
  },
};
</script>

<style lang="scss" scoped>
.feedback-root {
  height: 100%;

  ::v-deep {
    .wrap-text {
      overflow-wrap: anywhere;
    }
    table thead th.wrap-header {
      word-wrap: break-word;
      white-space: normal;
    }
  }
}
</style>
