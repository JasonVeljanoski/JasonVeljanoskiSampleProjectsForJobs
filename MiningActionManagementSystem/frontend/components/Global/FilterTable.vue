<template>
  <div class="root">
    <v-card class="main-card" outlined>
      <v-card-title class="d-flex justify-end align-center header">
        <slot name="card:title">{{ title }}</slot>
        <v-spacer />

        <slot name="card:header" />
        <e-icon-btn :tooltip="!headers_panel ? 'Show Headers' : 'Hide Headers'" @click="setSidePanel('headers')">
          mdi-format-list-numbered
        </e-icon-btn>
        <e-icon-btn v-if="!filters_panel" tooltip="Show Filters" @click="setSidePanel('filters')">
          mdi-filter-plus-outline
        </e-icon-btn>
        <e-icon-btn v-else tooltip="Hide Filters" @click="setSidePanel('filters')">
          mdi-filter-minus-outline
        </e-icon-btn>
      </v-card-title>
      <v-divider />
      <e-data-table
        :headers="header_vals"
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
        class="filter-table"
        v-on="$listeners"
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
        <e-icon-btn class="mr-2" @click="setSidePanel('filters')"> mdi-close </e-icon-btn>
      </v-card-title>

      <v-divider />
      <v-card-text class="filters">
        <slot name="filters"> Add Filters here </slot>
      </v-card-text>
      <v-spacer />
      <v-divider />
      <v-card-actions class="d-flex footer">
        <v-btn outlined :elevation="0" color="warning" @click="$emit('clear')"> Clear </v-btn>
      </v-card-actions>
    </v-card>
    <v-card v-show="headers_panel" class="side-card" outlined>
      <v-card-title class="d-flex justify-between align-center header">
        Headers
        <v-spacer />
        <e-icon-btn class="mr-2" @click="setSidePanel('headers')"> mdi-close </e-icon-btn>
      </v-card-title>
      <v-divider />
      <v-card-text class="filters ma-0 pa-0">
        <draggable :list="header_vals" class="header-items" :move="checkMove" v-bind="drag_options">
          <div v-for="header in header_vals" :key="header.text" class="header-item">
            <v-icon v-if="header.persistent" small>mdi-format-line-spacing</v-icon>
            <v-icon v-else small class="handle">mdi-format-line-spacing</v-icon>
            <v-checkbox
              :input-value="!header.hide"
              hide-details
              class="mt-0 pt-0"
              style="width: 100%"
              :label="header.text"
              :disabled="header.persistent"
              @click="toggleHide(header)"
            />
          </div>
        </draggable>
      </v-card-text>
      <v-divider />
      <v-card-actions class="d-flex footer">
        <template v-if="headers_panel">
          <e-btn color="warning" outlined @click="resetHeaders">Reset</e-btn>
          <v-spacer />
        </template>
        <template v-if="filters_panel">
          <e-btn color="warning">Reset</e-btn>
        </template>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import Draggable from 'vuedraggable'

export default {
  components: {
    Draggable,
  },
  props: {
    title: { type: String },
    hideSearchBar: { type: Boolean, required: false, default: false },
    items: { type: Array, default: () => [] },
    headers: { type: Array, default: () => [] },
    filter: { type: Function, default: null },
    loading: { type: Boolean, default: false },
    serverItemsLength: { type: Number, default: undefined },
    itemClass: { type: Function, default: null },
  },
  data() {
    return {
      item_vals: [],
      header_vals: [],
      search: null,
      side_panel: 'filters',
      drag_options: {
        animation: 200,
        group: 'description',
        disabled: false,
        ghostClass: 'dragging',
        handle: '.handle',
      },
    }
  },
  computed: {
    filtered_items() {
      if (this.filter) return this.filter(this.items)
      return this.items
    },
    filters_panel() {
      return this.side_panel == 'filters'
    },
    headers_panel() {
      return this.side_panel == 'headers'
    },
  },
  watch: {
    headers: {
      handler() {
        this.resetHeaderVals()
      },
      deep: true,
    },
  },
  mounted() {
    this.resetHeaderVals()
  },
  methods: {
    resetHeaderVals() {
      // add id and hide key for draggable headers to work
      this.header_vals = [...this.headers]
      for (const ii in this.header_vals) {
        const header = this.header_vals[ii]
        header.hide ||= false
        header.id ||= +ii
      }
    },
    setSidePanel(val) {
      if (this.side_panel == val) {
        val = false
      }
      this.side_panel = val
    },
    checkMove(e) {
      const source = this.header_vals[e.draggedContext.index]
      const target = this.header_vals[e.relatedContext.index]

      return !(source.persistent || target.persistent)
    },
    resetHeaders() {
      for (const header of this.header_vals) {
        header.hide = false
      }

      this.header_vals.sort((a, b) => a.id - b.id)
    },
    toggleHide(header) {
      if (header.hide == undefined) {
        this.$set(header, 'hide', false)
      }
      header.hide = !header.hide
    },
  },
}
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
