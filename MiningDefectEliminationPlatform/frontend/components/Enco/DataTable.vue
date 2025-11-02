<template>
  <v-data-table
    v-bind="binded_props"
    :headers="filtered_headers"
    v-on="$listeners"
    :class="{ nowrap: nowrap }"
  >
    <template v-for="(index, name) in $scopedSlots" v-slot:[name]="data">
      <slot :name="name" v-bind="data"></slot>
    </template>
    <template
      v-for="header in altered_headers"
      v-slot:[`item.${header.value}`]="slot_props"
    >
      <slot :name="`item.${header.value}`" v-bind="{ ...slot_props }">
        <template v-if="header.component">
          <component
            :is="header.component"
            v-on="getHeaderListeners(slot_props.item, header)"
            v-bind="getItemProps(slot_props.item, header)"
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
    };
  },
  computed: {
    binded_props() {
      let props = { ...this.$attrs, ...this.$props };
      delete props.headers;

      return props;
    },
    filtered_headers() {
      return this.headers.filter((x) => !("hide" in x) || !x.hide);
    },
    altered_headers() {
      return this.filtered_headers.filter(
        (x) => x.value != "data-table-expand" || x.formatter || x.component
      );
    },
  },
  methods: {
    getItemProps(item, header) {
      let props = {
        value: this.getValue(item, header),
        item: item,
        all_items: this.$attrs.items,
        header: header,
      };

      if (header.component_props) {
        props = { ...props, ...header.component_props(item) };
      }

      return props;
    },
    getHeaderListeners(item, header) {
      let temp = header.listeners || {};

      let final = {};

      for (let key of Object.keys(temp)) {
        final[key] = (x) => temp[key](item, x);
      }
      return final;
    },
    getValue(item, header) {
      let value = null;

      try {
        value = header.value.split(".").reduce((o, i) => o[i], item);
      } catch {}

      if (header.formatter) {
        try {
          value = header.formatter(value, item);
        } catch (e) {
          value = null;
        }
      }

      return value;
    },
  },
};
</script>

<style lang="scss" scoped>
.v-data-table ::v-deep {
  // td,
  th {
    white-space: nowrap;
  }
}
</style>
