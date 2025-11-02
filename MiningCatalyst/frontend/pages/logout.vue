<template>
  <v-card class="root">
    <v-card-text> You have signed out of Catalyst.</v-card-text>
    <v-card-actions>
      <save-btn to="/auth"> Log In </save-btn>
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
