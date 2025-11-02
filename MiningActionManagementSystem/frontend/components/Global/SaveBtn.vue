<template>
  <e-btn elevation="0" color="primary" v-bind="{ ...$attrs, ...$props }" v-on="$listeners">
    <slot>
      <v-icon left>mdi-content-save</v-icon>
      Save
    </slot>
  </e-btn>
</template>

<script>
export default {
  inheritAttrs: false,
}
</script>

<style></style>
