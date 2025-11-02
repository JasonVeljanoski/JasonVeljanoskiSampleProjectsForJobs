<template>
  <v-btn :style="style" :small="small" @click="nextState">
    {{ stateLabel }}
  </v-btn>
</template>

<script>
export default {
  props: {
    value: null,
    item: Object,
    header: Object,
  },
  data() {
    return {
      stateIndex: null,
      unknown: false,
    }
  },
  computed: {
    readonly() {
      return this.$attrs.readonly
    },
    small() {
      return this.$attrs.small
    },
    statesCount() {
      if (this.$attrs.states) return this.$attrs.states.length
      else return 0
    },
    stateLabel() {
      if (this.readonly || this.stateIndex == null) return this.value
      if (this.$attrs.labels) return this.$attrs.labels[this.stateIndex]
      else if (this.$attrs.states) return this.$attrs.states[this.stateIndex]
    },
    style() {
      let style = ''
      if (this.$attrs.styles) {
        style = style + '; ' + this.$attrs.styles[this.stateIndex]
      }
      if (this.$attrs.styleAll) {
        style = style + '; ' + this.$attrs.styleAll
      }
      if (this.unknown && !this.readonly) {
        if (this.$attrs.styleUnknown) {
          style = style + '; ' + this.$attrs.styleUnknown
        }
      }
      if (this.readonly && this.$attrs.styleReadonly) {
        style = style + '; ' + this.$attrs.styleReadonly
      }
      return style
    },
  },
  watch: {
    value() {
      this.initState()
    },
  },
  mounted() {
    this.initState()
  },

  methods: {
    nextState() {
      if (!this.readonly) {
        this.stateIndex = (this.stateIndex + 1) % this.statesCount
        this.submitEdit()
      }
    },
    submitEdit() {
      this.$emit('editColumn', this.item, this.header.value, this.$attrs.states[this.stateIndex])
    },
    initState() {
      this.unknown = true
      if (this.$attrs.states) {
        for (const index in this.$attrs.states) {
          if (this.$attrs.states[index] == this.value) {
            this.stateIndex = parseInt(index)
            this.unknown = false
          }
        }
      }
    },
  },
}
</script>

<style lang="scss" scoped>
::v-deep input {
  // width: auto;
  font-size: 14px;
}
</style>
