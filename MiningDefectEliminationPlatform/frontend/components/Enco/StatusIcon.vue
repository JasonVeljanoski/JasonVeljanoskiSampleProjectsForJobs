<template>
  <v-icon v-if="value" color="success"> mdi-check </v-icon>
  <v-icon v-else color="error"> mdi-close </v-icon>
</template>

<script>
export default {
  props: {
    value: { type: Boolean, default: false },
  },
};
</script>

<style></style>
