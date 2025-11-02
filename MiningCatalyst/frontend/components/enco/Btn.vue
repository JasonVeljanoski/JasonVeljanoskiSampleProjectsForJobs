<template>
  <!-- Span is needed to allow tooltips on disabled elements -->
  <span v-if="tooltip && $attrs['disabled']" class="d-inline-block" @mouseenter="setPos" @mouseleave="show = false">
    <v-btn v-bind="$attrs" ref="btn" v-on="$listeners">
      <slot />
      <v-tooltip bottom :value="show" :disabled="!tooltip" :position-x="x" :position-y="y">
        <span>{{ tooltip }}</span>
      </v-tooltip>
    </v-btn>
  </span>

  <v-btn v-else v-bind="$attrs" ref="btn" @mouseenter="setPos" @mouseleave="show = false" v-on="$listeners">
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
    setPos() {
      if (!this.tooltip) return

      try {
        const { x, y, width, height } = this.$refs.btn.$el.getBoundingClientRect()

        this.x = x + width / 2
        this.y = y + height
        this.show = true
      } catch {}
    },
  },
}
</script>

<style lang="scss" scoped></style>
