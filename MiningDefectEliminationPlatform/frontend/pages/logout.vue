<template>
  <v-card class="root">
    <v-card-text>
      You have signed out of DEP. Click here to log back in

      <e-btn to="/auth"> Log In </e-btn>
    </v-card-text>
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
  height: 400px;
}
</style>
