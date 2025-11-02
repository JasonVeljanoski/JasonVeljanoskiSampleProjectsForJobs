<template>
  <v-btn
    v-bind="{ ...$attrs, ...$props }"
    v-on="$listeners"
    @mouseenter="
      setPos($event)
      show = true
    "
    @mouseleave="show = false"
  >
    <slot />
    <v-tooltip bottom :value="show" :disabled="!tooltip" :position-x="x" :position-y="y">
      <span>{{ tooltip }}</span>
    </v-tooltip>
  </v-btn>
</template>

<script>
export default {
  props: {
    tooltip: {
      type: String,
      default: null,
    },
  },
  data() {
    return {
      x: 0,
      y: 0,
      show: false,
    }
  },
  methods: {
    setPos(event) {
      const { x, y, width, height, top, left } = event.target.getBoundingClientRect()
      this.x = x + width / 2
      this.y = y + height
    },
  },
}
</script>

<style scoped></style>
