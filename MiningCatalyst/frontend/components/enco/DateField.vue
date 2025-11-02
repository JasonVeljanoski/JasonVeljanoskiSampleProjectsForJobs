<template>
  <v-menu v-model="menu" bottom offset-y v-bind="menuProps" :disabled="disabled || readonly" min-width="auto">
    <template #activator="{ on, attrs }">
      <e-date-time
        v-bind="{ ...attrs, ...$attrs, ...$props }"
        :time="false"
        :show_validate="false"
        no-offset
        v-on="{ ...on, ...$listeners }"
        @click.native="menu = true"
        @blur="menu = false"
      />
    </template>
    <v-date-picker v-if="!hideCalendar" v-model="iso_value" no-title scrollable />
  </v-menu>
</template>

<script>
export default {
  props: {
    menuProps: { type: Object, default: () => {} },
    hideCalendar: { type: Boolean, default: false },
  },
  data() {
    return {
      menu: false,
    }
  },
  computed: {
    value() {
      return this.$attrs.value
    },
    disabled() {
      return this.$attrs.disabled
    },
    readonly() {
      return this.$attrs.readonly
    },
    iso_value: {
      get() {
        if (this.value) {
          return this.$format.toISO(this.value)
        }
        return null
      },
      set(x) {
        let val = new Date(x)
        val = new Date(val.getTime() + val.getTimezoneOffset() * 60000)

        this.$emit('input', val)
        this.$emit('change', val)
      },
    },
  },
}
</script>

<style></style>
