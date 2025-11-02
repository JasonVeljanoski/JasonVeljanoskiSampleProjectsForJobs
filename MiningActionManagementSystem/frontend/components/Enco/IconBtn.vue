<template>
  <e-btn :icon="!('fab' in $attrs)" v-bind="{ ...$attrs, ...$props }" v-on="$listeners">
    <v-icon> <slot /></v-icon>
  </e-btn>
</template>

<script>
export default {}
</script>

<style></style>
