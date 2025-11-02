<template>
  <v-progress-linear outlined :value="value" v-bind="{ ...$props, ...$attrs }" :color="color" height="17" />
</template>

<script>
export default {
  name: 'CircularProgress',
  props: {
    value: {
      type: Number,
      required: true,
    },
  },
  computed: {
    color() {
      if (this.value == 0) return 'accent'

      if (this.value <= 25) {
        return 'error'
      } else if (this.value <= 75) {
        return 'warning'
      } else {
        return 'success'
      }
    },
  },
}
</script>
