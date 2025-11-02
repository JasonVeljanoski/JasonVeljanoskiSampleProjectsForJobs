<template>
  <v-data-table v-bind="binded_props" :headers="filtered_headers" :class="{ nowrap: nowrap }" v-on="$listeners">
    <template v-for="(index, name) in $scopedSlots" #[name]="data">
      <slot :name="name" v-bind="data"></slot>
    </template>
    <template v-for="header in filtered_headers" #[`item.${header.value}`]="slot_props">
      <slot :name="`item.${header.value}`" v-bind="{ ...slot_props }">
        <template v-if="header.component">
          <component
            :is="header.component"
            :value="getValue(slot_props.item, header)"
            :item="slot_props.item"
            :all_items="$attrs.items"
            :header="header"
            v-bind="getHeaderProps(slot_props.item, header)"
            v-on="$listeners"
          />
        </template>
        <template v-else>
          {{ getValue(slot_props.item, header) }}
        </template>
      </slot>
    </template>
  </v-data-table>
</template>

<script>
export default {
  props: {
    headers: {
      type: Array,
      default: () => [],
    },
    nowrap: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      cloned_headers: [],
    }
  },
  computed: {
    binded_props() {
      const props = { ...this.$attrs, ...this.$props }
      delete props.headers

      return props
    },
    filtered_headers() {
      return this.headers.filter((header) => !('hide' in header) || !header.hide)
    },
  },
  methods: {
    getHeaderProps(item, header) {
      if (header.component_props) {
        return header.component_props(item)
      }
    },
    getValue(item, header) {
      let value = null

      try {
        value = header.value.split('.').reduce((o, i) => o[i], item)
      } catch {}

      if (header.formatter) {
        try {
          value = header.formatter(value, item)
        } catch (e) {
          value = null
        }
      }

      return value
    },
  },
}
</script>

<style lang="scss" scoped>
.nowrap ::v-deep {
  td,
  th {
    white-space: nowrap;
  }
}

.theme--light {
  --header-color: #f5f5f5;
}
.theme--dark {
  --header-color: #263238;
}

.v-data-table ::v-deep {
  th {
    white-space: nowrap !important;
    background-color: var(--header-color) !important;
  }

  border-radius: 0px !important;
}
</style>
