<template>
  <div class="root">
    <v-card class="main-card" outlined>
      <v-card-title class="d-flex justify-end align-center header">
        <slot name="card:title">{{ title }}</slot>
        <v-spacer />
        <slot name="card:header" />
        <e-icon-btn
          :tooltip="!headers_panel ? 'Show Headers' : 'Hide Headers'"
          @click="setSidePanel('headers')"
        >
          mdi-format-list-numbered
        </e-icon-btn>
        <e-icon-btn
          v-if="!filters_panel"
          tooltip="Show Filters"
          @click="setSidePanel('filters')"
        >
          mdi-filter-plus-outline
        </e-icon-btn>
        <e-icon-btn
          v-else
          tooltip="Hide Filters"
          @click="setSidePanel('filters')"
        >
          mdi-filter-minus-outline
        </e-icon-btn>
      </v-card-title>
      <v-divider />
      <e-data-table
        :headers="headers"
        :items="filtered_items"
        :search="search"
        :loading="loading"
        :item-class="itemClass"
        :footer-props="{
          'items-per-page-options': [20, 30, 50, 100],
        }"
        v-bind="$attrs"
        multi-sort
        fixed-header
        :server-items-length="serverItemsLength"
        v-on="$listeners"
        class="filter-table"
      >
        <template v-for="(index, name) in $scopedSlots" #[name]="data">
          <slot :name="name" v-bind="data"></slot>
        </template>
      </e-data-table>
    </v-card>

    <v-card v-show="filters_panel" class="side-card" outlined>
      <v-card-title class="d-flex justify-between align-center header">
        Filters
        <v-spacer />
        <e-icon-btn
          color="warning"
          tooltip="Reset Filters"
          @click="$emit('clear')"
        >
          mdi-restore
        </e-icon-btn>
      </v-card-title>

      <v-divider />
      <v-card-text class="filters">
        <slot name="filters"> Add Filters here </slot>
      </v-card-text>
    </v-card>
    <v-card v-show="headers_panel" class="side-card" outlined>
      <v-card-title class="d-flex justify-between align-center header">
        Headers
        <v-spacer />
        <e-icon-btn
          color="warning"
          tooltip="Reset Filters"
          @click="resetHeaders"
        >
          mdi-restore
        </e-icon-btn>
      </v-card-title>
      <v-divider />
      <v-card-text class="filters ma-0 pa-0">
        <draggable
          :list="headers"
          class="header-items"
          :move="checkMove"
          v-bind="drag_options"
        >
          <div v-for="header in headers" :key="header.text" class="header-item">
            <v-icon v-if="header.persistent" small>
              mdi-format-line-spacing
            </v-icon>
            <v-icon v-else small class="handle">mdi-format-line-spacing</v-icon>
            <v-checkbox
              :input-value="!header.hide"
              hide-details
              class="mt-0 pt-0"
              style="width: 100%"
              :label="header.text"
              :disabled="header.persistent"
              @click="header.hide = !header.hide"
            />
          </div>
        </draggable>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import Draggable from "vuedraggable";

export default {
  components: {
    Draggable,
  },
  props: {
    title: { type: String },
    hideSearchBar: { type: Boolean, required: false, default: false },
    items: { type: Array, default: () => [] },
    filter: { type: Function, default: null },
    loading: { type: Boolean, default: false },
    serverItemsLength: { type: Number, default: undefined },
    itemClass: { type: Function, default: null },
    save_key: { type: String },
    filters: { type: Object, default: () => {} },
    headers: { type: Array, default: () => [] },
  },
  data() {
    return {
      LS_KEY: "table_options",
      search: null,
      side_panel: "filters",
      drag_options: {
        animation: 200,
        group: "description",
        disabled: false,
        ghostClass: "dragging",
        handle: ".handle",
      },
    };
  },
  computed: {
    filtered_items() {
      if (this.filter) return this.filter(this.items);
      return this.items;
    },
    filters_panel() {
      return this.side_panel == "filters";
    },
    headers_panel() {
      return this.side_panel == "headers";
    },
    // save key for local storage
    save_key_filters() {
      if (!this.save_key) return null;
      return `${this.LS_KEY}-${this.save_key}-filters`;
    },
    save_key_headers() {
      if (!this.save_key) return null;
      return `${this.LS_KEY}-${this.save_key}-headers`;
    },
  },
  watch: {
    filters: {
      handler() {
        if (!this.save_key) return;

        localStorage.setItem(
          this.save_key_filters,
          JSON.stringify(this.filters)
        );
      },
      deep: true,
    },
    headers: {
      handler() {
        if (!this.save_key) return;
        const headers = {};

        for (let ii = 0; ii < this.headers.length; ii++) {
          const header = this.headers[ii];
          headers[header.value] = {
            hide: header.hide ?? false,
            order: ii,
            id: ii,
          };
        }

        localStorage.setItem(this.save_key_headers, JSON.stringify(headers));
      },
      deep: true,
    },
  },
  created() {
    if (this.save_key) {
      let saved_filters = localStorage.getItem(this.save_key_filters);

      if (saved_filters) {
        saved_filters = JSON.parse(saved_filters);

        for (const key in saved_filters) {
          // ----------------------------

          // format date like
          if (saved_filters[key]?.min_date) {
            saved_filters[key].min_date = new Date(saved_filters[key].min_date);
          }
          if (saved_filters[key]?.max_date) {
            saved_filters[key].max_date = new Date(saved_filters[key].max_date);
          }

          // ----------------------------

          this.$set(this.filters, key, saved_filters[key]);
        }
      }

      // -------------------------------------------------------------------

      let saved_headers = localStorage.getItem(this.save_key_headers);

      if (saved_headers) {
        saved_headers = JSON.parse(saved_headers);
        const headers = this.headers;

        for (let ii = 0; ii < headers.length; ii++) {
          const header = headers[ii];
          const saved_header = saved_headers[header.value];

          // -----

          // set default sort and visibility props in case ingested object does not have
          this.$set(header, "id", ii);
          this.$set(header, "order", ii);
          this.$set(header, "hide", false);

          // ----

          if (saved_header) {
            this.$set(header, "hide", saved_header.hide);
            header.order = saved_header.order;
          } else {
            header.order = 99 + headers.length + ii;
          }
        }

        // ----

        headers.sort((a, b) => a.order - b.order);
      }
    }
  },
  methods: {
    setSidePanel(val) {
      if (this.side_panel == val) {
        val = false;
      }
      this.side_panel = val;
    },
    checkMove(e) {
      let source = this.headers[e.draggedContext.index];
      let target = this.headers[e.relatedContext.index];

      return !(source.persistent || target.persistent);
    },
    resetHeaders() {
      for (let header of this.headers) {
        header.hide = false;
      }

      this.headers.sort((a, b) => a.id - b.id);
    },
  },
};
</script>

<style lang="scss" scoped>
.root {
  display: flex;
  flex-direction: row;
  height: 100%;
  width: 100%;
  overflow: hidden;
  gap: 10px;
}

.main-card {
  display: flex;
  width: 100%;
  flex-grow: 1;
  flex-direction: column;
  overflow-y: auto;
}

.side-card {
  width: 47ch;
  overflow: auto;

  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;

  .v-card__text {
    overflow: auto;
    flex-grow: 1;
  }
}

.filters {
  gap: 8px;
}

.header {
  height: 72px;
  gap: 10px;
}

.footer {
  // height: 59px;
}

.header-items {
  display: flex;
  flex-direction: column;
  overflow: auto;
  flex-grow: 1;
  // gap: 8px;
}
.header-item {
  display: flex;
  border-bottom: solid #555 1px;
  margin-left: -1px;
  margin-top: -1px;
  // border-radius: 4px;
  padding: 8px;
  gap: 10px;

  background: var(--background-color);

  .handle {
    cursor: ns-resize;
  }

  &.dragging {
    opacity: 0.6;
    background: #888;
  }
}
</style>
