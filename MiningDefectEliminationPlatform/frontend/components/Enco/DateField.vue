<template>
  <v-menu v-model="menu" bottom offset-y v-bind="menuProps" min-width="auto">
    <template #activator="{ on, attrs }">
      <e-date-time
        v-bind="{ ...attrs, ...$attrs, ...$props }"
        v-on="{ ...on, ...$listeners }"
        :time="false"
        :show_validate="false"
        no-offset
        @click.native="menu = true"
      />
    </template>
    <v-date-picker v-model="iso_value" no-title scrollable />
  </v-menu>
</template>

<script>
export default {
  props: {
    menuProps: { type: Object, default: () => {} },
  },
  data() {
    return {
      menu: false,
    };
  },
  computed: {
    value() {
      return this.$attrs.value;
    },
    iso_value: {
      get() {
        if (this.value) {
          return this.$format.toISO(this.value);
        }
      },
      set(x) {
        let val = new Date(x);
        val = new Date(val.getTime() + val.getTimezoneOffset() * 60000);

        this.$emit("input", val);
        this.$emit("change", val);
      },
    },
  },
};
</script>

<style></style>
