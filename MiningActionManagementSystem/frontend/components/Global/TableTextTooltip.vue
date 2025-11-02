<template>
  <v-tooltip bottom max-width="300">
    <template #activator="{ on, attrs }">
      <span v-bind="attrs" v-on="on">{{ text_value }}</span>
    </template>
    <p>{{ tooltip_text }}</p>
  </v-tooltip>
</template>

<script>
export default {
  props: {
    text: {
      type: String,
      required: true,
    },
    tooltip: {
      type: String,
      required: false,
      default: null,
    },
  },
  computed: {
    text_value() {
      return this.text || ''
    },
    tooltip_text() {
      return this.tooltip || this.text
    },
  },
}
</script>
