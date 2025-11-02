<template>
  <e-icon-btn v-bind="{ ...$props, ...$attrs }" :tooltip="tooltip" v-on="$listeners" @click="handleCopy">
    {{ icon_text }}
  </e-icon-btn>
</template>

<script>
export default {
  name: 'CopyIconBtn',
  props: {
    tooltip_text: {
      type: String,
      required: false,
      default: 'Copy',
    },
  },
  data() {
    return {
      is_copied: false,
    }
  },
  computed: {
    icon_text() {
      return this.is_copied ? 'mdi-clipboard-check-outline' : 'mdi-content-paste'
    },
    tooltip() {
      return this.is_copied ? 'Copied' : this.tooltip_text
    },
  },
  methods: {
    handleCopy() {
      this.is_copied = true
      setTimeout(() => (this.is_copied = false), 1500)
    },
  },
}
</script>
