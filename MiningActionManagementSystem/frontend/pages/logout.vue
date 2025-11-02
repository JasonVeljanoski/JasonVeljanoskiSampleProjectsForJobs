<template>
  <v-card class="root">
    <v-card-text> You have signed out of ACE.</v-card-text>
    <v-card-actions>
      <e-btn v-bind="$bind.btn" to="/auth"> Log In </e-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  auth: false,
}
</script>

<style lang="scss" scoped>
.root {
  margin: 10px auto;
  width: 500px;
}
</style>
