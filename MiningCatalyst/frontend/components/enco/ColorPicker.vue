<template>
  <v-menu
    v-model="open"
    offset-x
    :close-on-content-click="false"
    @input="
      () => {
        if (!open) {
          $emit('change', value_)
        }
      }
    "
  >
    <template #activator="{ on, attrs }">
      <slot name="activator" v-bind="attrs" v-on="on">
        <div class="dot mx-auto" :style="'background-color: ' + value_" />
      </slot>
    </template>
    <v-color-picker v-model="value_" mode="hexa" hide-mode-switch @input="$emit('input', $event)" />
  </v-menu>
</template>

<script>
export default {
  props: {
    value: null,
  },
  data() {
    return {
      open: false,
      value_: this.value,
    }
  },
  watch: {
    value() {
      this.value_ = this.value
    },
  },
}
</script>

<style lang="scss" scoped>
$size: 24px;

.dot {
  height: $size;
  width: $size;
  border-radius: 3px;
}
</style>
