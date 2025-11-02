<template>
  <input
    v-bind="{ ...$attrs }"
    ref="input"
    v-model.number="fake_value"
    class="simple-input"
    type="number"
    @focus="selectInput"
    @blur="selected = false"
    v-on="{ ...$listeners, input: () => {}, change: change }"
  />
</template>

<script>
export default {
  props: {
    value: null,
  },
  data() {
    return {
      value_: this.value,
      selected: false,
    }
  },
  computed: {
    fake_value: {
      get() {
        return this.selected ? this.value_ : this.value_ || ''
      },
      set(val) {
        this.value_ = val
      },
    },
  },
  watch: {
    value() {
      this.value_ = this.value
    },
  },
  created() {},
  methods: {
    change() {
      this.$nextTick(() => {
        this.$emit('input', this.value_ || 0)
        this.$emit('change', this.value_ || 0)
      })
    },
    selectInput() {
      this.selected = true
      this.$nextTick(() => {
        this.$refs.input.select()
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.simple-input {
  width: 100%;
  text-align: center;
  color: inherit;
  // outline: solid red 1px;
  // display: contents;
}
</style>
