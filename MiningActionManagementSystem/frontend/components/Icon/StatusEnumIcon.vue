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
    text() {
      return this.$enums.status[this.value]
    },
    color() {
      if (this.text == this.$enums.status[1]) return 'error'
      else if (this.text == this.$enums.status[2]) return 'secondary'
      else if (this.text == this.$enums.status[3]) return 'warning'
      else if (this.text == this.$enums.status[4]) return 'success'
    },
    icon() {
      if (this.text == this.$enums.status[1]) return 'mdi-calendar-remove'
      else if (this.text == this.$enums.status[2]) return 'mdi-package-variant'
      else if (this.text == this.$enums.status[3]) return 'mdi-package-variant-minus'
      else if (this.text == this.$enums.status[4]) return 'mdi-package-variant-closed-check'
    },
  },
}
</script>

<style></style>
