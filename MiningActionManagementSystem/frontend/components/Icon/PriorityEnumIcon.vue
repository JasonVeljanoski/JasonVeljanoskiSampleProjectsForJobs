<template>
  <v-chip :color="color">
    <b style="color: white">{{ text }}</b>
  </v-chip>
</template>

<script>
export default {
  props: {
    value: { type: Number, default: -1 },
  },
  computed: {
    text() {
      return this.value === 4
        ? 'Low'
        : this.value === 3
        ? 'Medium'
        : this.value === 2
        ? 'High'
        : this.value === 1
        ? 'Urgent'
        : 'Unknown'
    },
    color() {
      if (!this.value) return

      if (this.value == 4) return 'success'
      else if (this.value == 3) return 'warning'
      else if (this.value == 2) return 'error'
      else if (this.value == 1) return 'error2'

      return ''
    },
  },
}
</script>

<style lang="scss" scoped></style>
