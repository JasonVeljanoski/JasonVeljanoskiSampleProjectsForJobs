<template>
  <div class="root-tbl">
    <v-card max-width="1200" class="main-card ml-auto mr-auto mt-4" v-bind="$bind.card">
      <v-card-title>Flash Report Actions</v-card-title>
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
          <copy-icon-btn :id="item.id" @copy="copyActionUrl(item.id)" />
        </template>

        <template #item.include="{ item }">
          <div class="d-flex justify-center">
            <v-checkbox v-model="five_why.flash_report_action_ids" :value="item.id" @change="updateIncludes" />
          </div>
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
    five_why: { type: Object },
    investigation_id: { type: Number },
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
          text: "Include",
          align: "center",
          value: "include",
          sortable: false,
          divider: true,
          hide: false,
          width: "10",
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
    copyActionUrl(id) {
      const text = `${window.location.origin}/actions?action_id=${id}`;
      navigator.clipboard.writeText(text);
    },
    updateIncludes() {
      this.$axios.$patch("/five_why/flash_report_action_ids", this.five_why.flash_report_action_ids, {
        params: {
          five_why_id: this.five_why.id,
        },
      });
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
