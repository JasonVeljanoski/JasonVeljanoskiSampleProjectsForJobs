<template>
  <e-icon-btn :disabled="disabled" :color="color" :tooltip="text" @click="$emit('toggle')">{{ icon }}</e-icon-btn>
</template>

<script>
export default {
  props: {
    value: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
  },
  computed: {
    text() {
      return this.value ? "Archived" : "Active";
    },
    color() {
      return this.value ? "warning" : "success";
    },
    icon() {
      return this.value ? "mdi-archive-outline" : "mdi-package-variant";
    },
  },
};
</script>

<style></style>
