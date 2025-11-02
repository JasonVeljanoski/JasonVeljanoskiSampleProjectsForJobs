<template>
  <v-text-field
    v-bind="$attrs"
    :value="is_focused ? value : comma_value"
    :type="is_focused ? 'number' : 'text'"
    :class="{ focused: is_focused }"
    v-on="{
      ...$listeners,

      input: (e) => submit('input', e),
      change: (e) => submit('change', e),
    }"
    @focus="is_focused = true"
    @blur="is_focused = false"
  />
</template>

<script>
export default {
  props: { value: null },
  data() {
    return {
      is_focused: false,
    }
  },
  computed: {
    comma_value() {
      if (this.value == null) {
        return ''
      }

      return this.$format.commarize(this.value)
    },
    props() {
      if (this.is_focused) {
        return { type: 'number' }
      } else {
        return { type: 'text' }
      }
    },
  },
  methods: {
    submit(event, value) {
      value = value == '' ? null : +value
      this.$emit(event, value)
    },
  },
}
</script>

<style lang="scss" scoped></style>
