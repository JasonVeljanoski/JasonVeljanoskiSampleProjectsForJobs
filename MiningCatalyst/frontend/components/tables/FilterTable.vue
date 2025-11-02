<template>
  <v-card class="flex-card" outlined>
    <div class="header d-flex align-center mr-4">
      <slot name="card:header" />

      <v-spacer />

      <!-- PREVIEW FILTERS -->
      <v-menu :close-on-content-click="false" offset-y>
        <template #activator="{ on }">
          <e-icon-btn tooltip="Filters" v-on="on">mdi-filter-cog-outline</e-icon-btn>
        </template>
        <filter-preview-card :filters="filters" @reload="$emit('reload')" />
      </v-menu>

      <v-menu :close-on-content-click="false" offset-y>
        <template #activator="{ on }">
          <e-icon-btn v-if="showHeaderFilters" tooltip="Headers" v-on="on"> mdi-format-list-checkbox </e-icon-btn>
        </template>

        <!-- HEADER FILTERS -->
        <v-card min-width="320">
          <v-card-title>Headers</v-card-title>

          <v-divider />

          <span class="body-wrapper">
            <draggable :list="headers" dense tag="v-list" v-bind="drag_options">
              <v-card v-for="(header, ii) in headers" :key="ii">
                <v-list-item :key="header.text" @click="toggleHeader(header)">
                  <v-list-item-icon class="mr-0 handle">
                    <v-icon :class="{ handle: header.persistent }" small color="primary"
                      >mdi-format-line-spacing</v-icon
                    >
                  </v-list-item-icon>
                  <v-list-item-action class="mr-2">
                    <v-checkbox :input-value="header.visible ?? true" hide-details :disabled="header.persistent" />
                  </v-list-item-action>
                  <v-list-item-title>{{ header.text }}</v-list-item-title>
                </v-list-item>
                <v-divider />
              </v-card>
            </draggable>
          </span>

          <v-card-actions>
            <cancel-btn @click="resetHeaders()">Reset</cancel-btn>
          </v-card-actions>
        </v-card>
      </v-menu>

      <slot name="card:title">
        <span style="font-size: 14pt">{{ title }}</span>
      </slot>
    </div>

    <v-divider />

    <!-- TABLE -->
    <e-data-table
      class="bordered filter-table"
      v-bind="$attrs"
      :headers="visible_headers"
      :options.sync="options_"
      :footer-props="{
        'items-per-page-options': [20, 30, 50, 100],
      }"
      :item-class="itemClass"
      disable-sort
      fixed-header
      v-on="$listeners"
    >
      <!-- HEADER -->
      <template v-for="(header, ii) in visible_headers" #[`header.${header.value}`]>
        <div :key="ii" class="d-flex align-center">
          <span style="font-size: 10pt">{{ header.text }}</span>

          <v-spacer />

          <v-menu
            v-if="!!header.filters"
            :key="ii"
            v-model="menus[header.value]"
            :close-on-content-click="false"
            offset-y
            @input="triggerReload($event)"
          >
            <template #activator="{ on }">
              <div style="margin-left: -10px">
                <v-icon small :color="hasRules(header.value) ? 'primary' : null">
                  {{ sorting[header.value]?.icon ?? '' }}
                </v-icon>
                <label
                  v-if="sorting[header.value]?.order"
                  style="position: relative; bottom: -5px; right: 7px; font-size: 10px; font-weight: 500"
                  :style="{ color: hasRules(header.value) ? 'var(--v-primary-base)' : null }"
                >
                  {{ sorting[header.value]?.order }}
                </label>
              </div>

              <e-btn
                icon
                small
                :ripple="false"
                :color="hasRules(header.value) ? 'primary' : null"
                @click.stop
                v-on="on"
              >
                <v-icon small>
                  {{ !hasRules(header.value) ? 'mdi-arrow-down-box' : 'mdi-filter' }}
                </v-icon>
              </e-btn>
            </template>

            <filter-card
              :key="filter_key"
              v-model="filters[header.value]"
              :header="header"
              :options="options_"
              @save="close(header.value)"
            />
          </v-menu>
        </div>
      </template>

      <!-- DATA -->
      <template v-for="(index, name) in $scopedSlots" #[name]="data">
        <slot :name="name" v-bind="data" />
      </template>
    </e-data-table>
  </v-card>
</template>

<script>
import Draggable from 'vuedraggable'

import FilterCard from '@/components/tables/FilterCard.vue'
import FilterPreviewCard from '@/components/tables/FilterPreviewCard.vue'

export default {
  components: {
    Draggable,
    FilterCard,
    FilterPreviewCard,
  },
  props: {
    title: { type: String },
    headers: { type: Array, default: () => [] },
    filters: { type: Object, default: () => {} },
    options: { type: Object, default: () => {} },
    save_key: { type: String },
    itemClass: { type: Function, default: null },
    showHeaderFilters: { type: Boolean, default: true },
  },
  data() {
    return {
      LS_KEY: 'table_options',
      drag_options: {
        animation: 200,
        group: 'description',
        disabled: false,
        ghostClass: 'dragging',
        handle: '.handle',
      },
      menus: {},
      filter_key: 0,
      options_: null,
      group_tab: 0,
    }
  },
  computed: {
    visible_headers() {
      return this.headers.filter((header) => header.visible ?? true)
    },
    save_key_filters() {
      if (!this.save_key) return null
      return `${this.LS_KEY}-${this.save_key}-filters`
    },
    save_key_headers() {
      if (!this.save_key) return null
      return `${this.LS_KEY}-${this.save_key}-headers`
    },
    save_key_options() {
      if (!this.save_key) return null
      return `${this.LS_KEY}-${this.save_key}-options`
    },
    sorting() {
      let sorting = {}

      for (let ii = 0; ii < this.options.sortBy.length; ii++) {
        const key = this.options.sortBy[ii]
        const desc = this.options.sortDesc[ii]

        sorting[key] = {
          icon: desc ? 'mdi-arrow-up-thin' : 'mdi-arrow-down-thin',
          order: ii + 1,
        }
      }

      return sorting
    },
  },
  watch: {
    filters: {
      handler() {
        if (!this.save_key) return

        localStorage.setItem(this.save_key_filters, JSON.stringify(this.filters))
      },
      deep: true,
    },
    headers: {
      handler() {
        if (!this.save_key) return
        const headers = {}

        for (let ii = 0; ii < this.headers.length; ii++) {
          const header = this.headers[ii]
          headers[header.value] = {
            visible: header.visible ?? true,
            order: ii,
            id: ii,
          }
        }

        localStorage.setItem(this.save_key_headers, JSON.stringify(headers))
      },
      deep: true,
    },
    options: {
      handler() {
        this.$emit('update:options', this.options)

        if (!this.save_key) return

        localStorage.setItem(this.save_key_options, JSON.stringify(this.options))
      },
      deep: true,
    },
  },
  created() {
    if (this.save_key) {
      let saved_filters = localStorage.getItem(this.save_key_filters)
      if (saved_filters) {
        saved_filters = JSON.parse(saved_filters)

        for (const key in saved_filters) {
          this.$set(this.filters, key, saved_filters[key])
        }
      }

      // -------------------------------------------------------------------

      let saved_headers = localStorage.getItem(this.save_key_headers)

      if (saved_headers) {
        saved_headers = JSON.parse(saved_headers)
        const headers = this.headers

        for (let ii = 0; ii < headers.length; ii++) {
          const header = headers[ii]
          const saved_header = saved_headers[header.value]

          // -----

          // set default sort and visibility props in case ingested object does not have
          this.$set(header, 'id', ii)
          this.$set(header, 'order', ii)
          this.$set(header, 'visible', true)

          // ----

          if (saved_header) {
            this.$set(header, 'visible', saved_header.visible)
            header.order = saved_header.order
          } else {
            header.order = 99 + headers.length + ii
          }
        }

        // ----

        headers.sort((a, b) => a.order - b.order)
      }

      // -------------------------------------------------------------------

      let saved_options = localStorage.getItem(this.save_key_options)

      if (saved_options) {
        saved_options = JSON.parse(saved_options)

        for (const key in saved_options) {
          this.$set(this.options, key, saved_options[key])
        }

        this.options_ = JSON.parse(JSON.stringify(this.options))
      }
    }

    // -----------------------------------------------------------------------

    // init headers
    for (const header of this.headers) {
      this.menus[header] = false
    }

    // -----------------------------------------------------------------------
  },
  methods: {
    triggerReload(payload) {
      if (!payload) this.$emit('reload')
    },
    toggleHeader(header) {
      if (header.visible === undefined) {
        this.$set(header, 'visible', false)
      } else {
        header.visible = !header.visible
      }
    },
    resetHeaders() {
      for (const header of this.headers) {
        header.visible = true
      }

      this.headers.sort((a, b) => a.id - b.id)
    },
    close(key) {
      this.menus[key] = false
      this.$emit('reload')
    },
    renderFilters() {
      this.filter_key += 1
    },
    resetOptions() {
      this.options_ = JSON.parse(JSON.stringify(this.options))
    },
    hasRules(val) {
      return this.filters[val]?.rules.length
    },
    changeTab(ii) {
      // set all visibility to false
      for (const header of this.headers) {
        this.$set(header, 'visible', false)
      }

      // ----------------------------

      const fields = this.groups[ii].fields

      for (const field of fields) {
        const header = this.headers.find((header) => header.value === field)
        if (header) {
          this.$set(header, 'visible', true)
        }
      }

      // ----------------------------

      this.$emit('changeTab', ii)
    },
  },
}
</script>

<style lang="scss" scoped>
.header {
  gap: 8px;
  color: var(--v-primary-base);
}

// ---------

.handle {
  cursor: ns-resize;
}

.dragging {
  opacity: 0.6;
  background: #888;
}

// ---------

// global
.body-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: auto;

  max-height: calc(100vh - 250px);
}

::v-deep .v-sheet.v-list {
  padding: 0;
}
</style>
