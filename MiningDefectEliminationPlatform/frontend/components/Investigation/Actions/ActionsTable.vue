<template>
  <div class="root-tbl">
    <v-card max-width="1200" class="main-card ml-auto mr-auto mt-4" v-bind="$bind.card">
      <div class="d-flex justify-space-between align-center">
        <v-card-title>Actions</v-card-title>
        <v-btn v-bind="$bind.btn" class="mx-3" @click="editAction()">
          <v-icon left>mdi-plus</v-icon>
          <span>Action</span>
        </v-btn>
      </div>
      <v-divider />
      <e-data-table
        class="table"
        fixed-header
        :headers="table_headers"
        :loading="loading"
        :items="filtered_actions"
        hide-default-footer
        disable-pagination
      >
        <template #item.id="{ item }">
          <span v-if="type == 'flash_report' && item.flash_report_id">
            <copy-icon-btn :id="item.id" @copy="copyActionUrl(item.id)" />
          </span>
          <span v-else-if="type == 'five_why' && item.five_why_id">
            <copy-icon-btn :id="item.id" @copy="copyActionUrl(item.id)" />
          </span>
          <v-tooltip v-else top>
            <template v-slot:activator="{ on, attrs }">
              <v-icon v-bind="attrs" v-on="on"> mdi-progress-clock </v-icon>
            </template>
            <span>Pending</span>
          </v-tooltip>
        </template>
        <template #item.edit="{ item }">
          <e-icon-btn @click="editAction(item)"> mdi-pencil </e-icon-btn>
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
          <title-hover-text :main_text="item.title" :sub_text="item.description" />
        </template>
      </e-data-table>
    </v-card>
    <v-btn
      v-if="!hide_button"
      :disabled="(!is_my_investigation && !$perms.is_admin) || loading"
      class="action-btn"
      color="success"
      @click="$emit('save')"
    >
      <v-icon left>{{ button_icon }}</v-icon>
      {{ button_text }}
    </v-btn>
    <action-table-form ref="action_table_form" :investigation_id="investigation_id" @add_action="addAction($event)" />
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import ActionTableForm from "@/components/Investigation/Actions/ActionTableForm";
import StatusEnumIcon from "@/components/Global/StatusEnumIcon";
import PriorityEnumIcon from "@/components/Global/PriorityEnumIcon";
import CopyIconBtn from "@/components/IconBtns/CopyIconBtn.vue";

export default {
  name: "ActionsTable",
  components: {
    ActionTableForm,
    CopyIconBtn,
  },
  props: {
    actions: { type: Array },
    investigation_id: { type: Number },
    type: {
      type: String,
      enum: ["flash_report", "five_why"],
    },
    button_text: {
      type: String,
      required: false,
      default: "proceed",
    },
    button_icon: {
      type: String,
      required: false,
      default: "mdi-arrow-down-left-bold",
    },
    hide_button: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      loading: false,
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
          text: "Priority",
          value: "priority",
          align: "center",
          divider: true,
          component: PriorityEnumIcon,
          hide: false,
          width: "10",
          divider: true,
        },
        {
          text: "Action",
          value: "title",
          cellClass: "wrap-text",
          hide: false,
          width: "320",
          divider: true,
        },
        {
          text: "Owners",
          value: "owners",
          hide: false,
          formatter: (x) =>
            x
              .map((a) => this.$utils.getUserName(a?.user_id))
              .sort()
              .join(", "),
          width: "150",
          divider: true,
        },
        {
          text: "Date Due",
          value: "date_due",
          formatter: (x) => this.$format.date(x),
          width: "120",
          hide: false,
          width: "10",
          divider: true,
        },
        {
          text: "Status",
          value: "status",
          align: "center",
          divider: true,
          component: StatusEnumIcon,
          hide: false,
          width: "10",
        },
        {
          text: "Image",
          value: "image",
          sortable: false,
          divider: true,
          hide: false,
          width: "10",
        },
        {
          text: "Supervisor",
          value: "supervisor_id",
          formatter: (x) => this.$utils.getUserName(x),
          cellClass: "nowrap",
          hide: false,
          width: "10",
          divider: true,
        },
        {
          text: "Date Created",
          value: "created",
          formatter: (x) => this.$format.date(x),
          width: "125",
          hide: false,
          width: "10",
          divider: true,
        },
        {
          text: "Last Updated",
          value: "updated",
          formatter: (x) => this.$format.date(x),
          width: "125",
          hide: false,
          width: "10",
          divider: true,
        },
        {
          text: "Date Closed",
          value: "date_closed",
          width: "120",
          hide: false,
          formatter: (x) => (x ? this.$format.date(x) : ""),
          width: "10",
          divider: true,
        },
      ],
    };
  },
  computed: {
    ...mapGetters({
      is_my_investigation: "user/getIsMyInvestigation",
    }),
    table_headers() {
      return [...this.headers];
    },
    filtered_actions() {
      return this.actions.filter((x) => !x.is_archived);
    },
  },
  methods: {
    editAction(action) {
      if (action) {
        action.created = this.$format.initDate(action.created);
        action.updated = this.$format.initDate(action.updated);
        action.date_due = this.$format.initDate(action.date_due);
        action.date_closed = this.$format.initDate(action.date_closed);

        this.$refs.action_table_form.open(action);
      } else {
        this.$refs.action_table_form.open(null);
      }
    },
    addAction(payload) {
      this.loading = true;
      this.$emit("loading", this.loading);

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

          // --------------------------------------------

          let index = this.actions.findIndex((x) => x.id == action.id);
          if (index > -1) {
            this.$set(this.actions, index, res);
          } else {
            this.actions.push(res);
          }

          // --------------------------------------------

          if (res.flash_report_id)
            this.$document.create_flash_report(res.investigation_id).catch((err) => console.error(err));
          else if (res.five_why_id)
            this.$document.create_five_why_report(res.investigation_id).catch((err) => console.error(err));

          this.$document.create_shared_learnings_report(res.investigation_id).catch((err) => console.error(err));

          // --------------------------------

          this.loading = false;
          this.$emit("loading", this.loading);
        })
        .catch((err) => {
          console.error(err);
        });
    },
    copyActionUrl(id) {
      const text = `${window.location.origin}/actions?action_id=${id}`;
      navigator.clipboard.writeText(text);
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$action-form-height: 340px;
$stepper-height: 72px;

.root-tbl {
  max-width: 1200px;
  margin: auto;

  .main-card {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    width: 100%;
    overflow: hidden;

    .table {
      overflow-y: auto;
    }
  }
}

.action-btn {
  margin-top: 5px;
}

.tooltip {
  padding: 5px;
}

::v-deep {
  .wrap-text {
    overflow-wrap: anywhere;
  }
  .table > * > table > * > tr > * {
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
  .table > * > table > * > tr > th {
    &:nth-child(-n + 2) {
      z-index: 4;
    }
  }
}
</style>
