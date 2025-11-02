<template>
  <div class="act-table-wrapper">
    <e-data-table
      class="table"
      fixed-header
      :headers="table_headers"
      :items="items"
      :loading="loading"
      hide-default-footer
      disable-pagination
    >
      <!-- DATA TABLE SLOTS -->
      <template #item.id="{ item }">
        <copy-icon-btn :id="item.id" @copy="copyActionUrl(item.id)" />
      </template>
      <template #item.action="{ item }">
        <e-icon-btn
          v-bind="$bind.btn_simple"
          tooltip="Action Link"
          :to="`/actions?action_id=${item.id}`"
          target="_blank"
        >
          mdi-link-variant
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
      loading: false,
      headers: this.$table_headers.action_alert,
    };
  },
  computed: {
    table_headers() {
      return [...this.headers];
    },
  },
  methods: {
    copyActionUrl(id) {
      const text = `${window.location.origin}/actions?action_id=${id}`;
      navigator.clipboard.writeText(text);
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;

.act-table-wrapper {
  border: solid 1px var(--v-accent-base);
  border-radius: 5px;

  .table {
    max-height: calc(100vh - #{$header-height} - 180px);
    overflow-y: auto;
  }
}
.tooltip {
  padding: 5px;
}
</style>
