<template>
  <v-chip :color="color">
    <v-icon left>{{ icon }}</v-icon>
    <b>{{ text }}</b>
  </v-chip>
</template>

<script>
export default {
  props: {
    value: { type: Number, default: false },
  },
  computed: {
    icon() {
      if (this.value == 1) return 'mdi-bug'
      else if (this.value == 2) return 'mdi-comment-text'
    },
    text() {
      if (this.value == 1) return 'Bug'
      else if (this.value == 2) return 'Feedback'
    },
    color() {
      if (this.value == 1) return 'error'
      else if (this.value == 2) return 'warning'
    },
  },
}
</script>

<style></style>
