<template>
  <e-btn :icon="!('fab' in $attrs)" v-bind="$attrs" v-on="$listeners">
    <v-icon :color="iconColor"> <slot /></v-icon>
  </e-btn>
</template>

<script>
export default {
  props: {
    iconColor: {
      type: String,
      default: null,
    },
  },
}
</script>

<style></style>
