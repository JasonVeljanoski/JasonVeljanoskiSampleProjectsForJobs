<template>
  <div>
    <v-card outlined elevation="0">
      <v-card-title class="att-title d-flex justify-space-between">
        Actions
        <v-btn
          v-bind="$bind.btn"
          class="mx-3"
          :disabled="!can_add"
          @click="editAction()"
        >
          <v-icon left>mdi-plus</v-icon>
          <span>Action</span>
        </v-btn>
      </v-card-title>

      <v-divider />

      <v-card-text v-if="actions.length == 0" class="my-2">
        No actions.
      </v-card-text>

      <e-data-table
        v-else
        :headers="headers"
        :items="filtered_actions"
        fixed-header
        :options="{
          itemsPerPage: 5,
          sortBy: ['created'],
          sortDesc: [true],
        }"
        :footer-props="{
          'items-per-page-options': [],
        }"
        class="filter-table"
      >
        <template #item.id="{ item }">
          <span v-if="type == 'flash_report' && item.flash_report_id">
            <copy-icon-btn :id="item.id" @copy="copyActionUrl(item.id)" />
          </span>
          <span v-else-if="type == 'five_why' && item.five_why_id">
            <copy-icon-btn :id="item.id" @copy="copyActionUrl(item.id)" />
          </span>
          <span
            v-else-if="type == 'root_cause_detail' && item.root_cause_detail_id"
          >
            {{ item.id }}
          </span>
          <v-tooltip v-else top>
            <template v-slot:activator="{ on, attrs }">
              <v-icon v-bind="attrs" v-on="on"> mdi-progress-clock </v-icon>
            </template>
            <span>Pending</span>
          </v-tooltip>
        </template>
        <template #item.edit="{ item }">
          <e-icon-btn :disabled="!can_edit" @click="editAction(item)">
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
        <template #item.remove="{ item }">
          <e-icon-btn
            :disabled="!pendingState(item)"
            color="error"
            @click="remove(item.id)"
          >
            mdi-delete
          </e-icon-btn>
        </template>
      </e-data-table>
    </v-card>

    <action-table-form
      ref="action_table_form"
      :investigation_id="investigation_id"
      :report_id="report_id"
      @add_action="addAction($event)"
    />
  </div>
</template>

<script>
import ActionTableForm from "@/components/Investigation/Actions/ActionTableForm";
import StatusEnumIcon from "@/components/Global/StatusEnumIcon";
import PriorityEnumIcon from "@/components/Global/PriorityEnumIcon";
import CopyIconBtn from "@/components/IconBtns/CopyIconBtn.vue";

export default {
  components: {
    ActionTableForm,
    PriorityEnumIcon,
    StatusEnumIcon,
    CopyIconBtn,
  },
  props: {
    investigation_id: { type: Number },
    actions: { type: Array, default: () => [] },
    type: {
      type: String,
      enum: ["flash_report", "five_why", "root_cause_detail"],
    },
    report_id: {
      type: Number,
      required: false,
      default: null,
    },
    can_add: {
      type: Boolean,
      default: true,
    },
    can_edit: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      headers: this.$table_headers.simple_action,
    };
  },
  computed: {
    filtered_actions() {
      return this.actions.filter((x) => !x.is_archived);
    },
  },
  methods: {
    addAction(payload) {
      this.loading = true;
      this.$emit("loading", this.loading);

      // --------------------------------------------

      // bind action to report if id provided
      if (this.type == "flash_report") {
        payload.action.flash_report_id = this.report_id;
      } else if (this.type == "five_why") {
        payload.action.five_why_id = this.report_id;
      } else if (this.type == "root_cause_detail") {
        payload.action.root_cause_detail_id = this.report_id;
      }

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
            this.$document
              .create_flash_report(res.investigation_id)
              .then(() => this.$emit("refresh_report"))
              .catch((err) => console.error(err));
          else if (res.five_why_id)
            this.$document
              .create_five_why_report(res.investigation_id)
              .then(() => this.$emit("refresh_report"))
              .catch((err) => console.error(err));

          this.$document
            .create_shared_learnings_report(res.investigation_id)
            .catch((err) => console.error(err));

          // --------------------------------

          this.loading = false;
          this.$emit("loading", this.loading);
        })
        .catch((err) => {
          console.error(err);
        });
    },
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
    copyActionUrl(id) {
      const text = `${window.location.origin}/actions?action_id=${id}`;
      navigator.clipboard.writeText(text);
    },
    remove(id) {
      if (confirm("Are you sure you want to remove this action?")) {
        let x = this.actions.findIndex((x) => x.id == id);
        if (x > -1) {
          this.actions.splice(x, 1);
        }
      }
    },
    pendingState(item) {
      return (
        !item.flash_report_id && !item.five_why_id && !item.root_cause_detail_id
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.att-title {
  font-size: 16px;
}

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
</style>
