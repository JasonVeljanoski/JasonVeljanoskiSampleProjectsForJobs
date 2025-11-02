<template>
  <v-menu v-model="show" :close-on-content-click="false">
    <template #activator="slot_props">
      <slot name="activator" v-bind="{ ...slot_props }" />
    </template>
    <v-card>
      <v-text-field
        v-model="value"
        v-bind="$bind.generic"
        :placeholder="placeholder"
        hide-details
        autofocus
        append-icon="mdi-content-save"
        @keypress.enter="submit"
        @click:append="submit"
      />
    </v-card>
  </v-menu>
</template>

<script>
export default {
  props: {
    placeholder: { type: String, default: 'Enter Value' },
  },
  data() {
    return {
      show: false,
      value: null,
    }
  },
  methods: {
    submit() {
      this.show = false
      this.$emit('submit', this.value)
      this.value = null
    },
  },
}
</script>

<style></style>
