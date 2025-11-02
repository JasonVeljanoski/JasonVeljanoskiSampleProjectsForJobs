<template>
  <e-btn class="btn--cancel" outlined color="warning" v-bind="{ ...$attrs, ...$props }" v-on="$listeners">
    <slot>
      <v-icon left>mdi-close</v-icon>
      Cancel
    </slot>
  </e-btn>
</template>

<script>
export default {
  inheritAttrs: false,
}
</script>
