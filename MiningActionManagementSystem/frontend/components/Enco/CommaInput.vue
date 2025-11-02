<template>
  <input
    v-if="activated"
    ref="main_input"
    v-bind="{ ...$attrs }"
    v-model.number="value_"
    class="simple-input"
    type="number"
    @blur="deactivateInput"
    @change="triggerChange"
    @keyup.enter="$event.target.blur()"
    @paste="$emit('paste', $event)"
  />
  <input
    v-else-if="!activated"
    class="simple-input"
    :tabindex="clickable ? 0 : -1"
    readonly
    :value="$format.commarize(decimals != null && !!value_ ? value_.toFixed(decimals) : value_) || on_empty"
    @click="activateInput"
    @focus="activateInput"
  />
</template>

<script>
export default {
  props: {
    value: null,
    on_empty: { type: String, default: '-' },
    decimals: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      value_: this.value,
      activated: false,
      has_changed: false,
    }
  },
  computed: {
    clickable() {
      const check = (x) => x !== true && x !== ''

      return check(this.$attrs.readonly) && check(this.$attrs.disabled)
    },
  },
  watch: {
    value() {
      this.value_ = this.value
    },
  },
  mounted() {},
  methods: {
    activateInput() {
      if (this.clickable) {
        this.activated = true
        this.$nextTick(() => {
          this.$refs.main_input.focus()
          this.$refs.main_input.select()
        })
        this.$emit('focus')
      }
    },
    deactivateInput() {
      const value = this.value_
      if (this.clickable && this.has_changed && this.value_ != this.value) {
        this.$emit('input', value)
        this.$emit('change', value)
      }

      if (this.activated) {
        this.$emit('blur')
      }

      this.activated = false
      this.has_changed = false
    },
    triggerChange() {
      this.has_changed = true
    },
  },
}
</script>

<style scoped>
.simple-input {
  width: 100%;
  text-align: right;
  color: inherit;
}
</style>
