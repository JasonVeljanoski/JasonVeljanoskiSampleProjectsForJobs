<template>
  <div class="inv-table-wrapper">
    <e-data-table
      class="table"
      fixed-header
      :headers="table_headers"
      :items="items"
      hide-default-footer
      disable-pagination
      @dblclick:row="onRowDoubleClick"
    >
      <!-- DATA TABLE SLOTS -->
      <template #item.id="{ item }">
        <copy-icon-btn :id="item.id" @copy="copyInvestigationUrl(item.id)" />
      </template>
      <template #item.investigation="{ item }">
        <e-icon-btn
          v-bind="$bind.btn_simple"
          tooltip="Investigation Link"
          :to="`/investigation?id=${item.id}`"
          target="_blank"
        >
          mdi-link-variant
        </e-icon-btn>
      </template>

      <template #item.actions="{ item }">
        <e-icon-btn v-bind="$bind.btn_simple" tooltip="Investigation Actions" :to="`/actions?id=${item.id}`">
          mdi-clock-fast
        </e-icon-btn>
      </template>
      <template #item.title="{ item }">
        <title-hover-text :main_text="item.title" :sub_text="item.description" />
      </template>
    </e-data-table>
  </div>
</template>

<script>
import CopyIconBtn from "@/components/IconBtns/CopyIconBtn.vue";

export default {
  components: {
    CopyIconBtn,
  },
  props: {
    items: { type: Array },
  },
  data() {
    return {
      headers: this.$table_headers.investigation_alert,
    };
  },

  computed: {
    table_headers() {
      return [...this.headers];
    },
  },
  methods: {
    copyInvestigationUrl(id) {
      const text = `${window.location.origin}/investigation?id=${id}`;
      navigator.clipboard.writeText(text);
    },
    editInvestigation(payload) {
      let investigation = { ...payload };
      investigation.created = this.$format.initDate(investigation.created);
      investigation.updated = this.$format.initDate(investigation.updated);
      investigation.date_closed = this.$format.initDate(investigation.date_closed);
      investigation.event_datetime = this.$format.initDate(investigation.event_datetime);
      investigation.completion_due_date = this.$format.initDate(investigation.completion_due_date);

      this.$refs.edit_investigation.open(investigation);
    },
    onRowDoubleClick(_, item) {
      this.$router.push(`/investigation?id=${item.item.id}`);
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;

.inv-table-wrapper {
  border: solid 1px var(--v-accent-base);
  border-radius: 5px;

  .table {
    max-height: calc(100vh - #{$header-height} - 180px);
    overflow-y: auto;
  }
}

.investigation-title {
  cursor: pointer;

  &:hover {
    text-decoration: underline;
    color: var(--v-primary-base);
  }
}
</style>
