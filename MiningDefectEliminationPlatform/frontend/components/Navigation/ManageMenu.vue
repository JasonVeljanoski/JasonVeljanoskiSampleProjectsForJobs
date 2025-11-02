<template>
  <div>
    <v-menu open-on-hover offset-y>
      <template v-slot:activator="{ on, attrs }">
        <v-btn text tile v-bind="attrs" v-on="on">
          <v-icon left>mdi-account-cog</v-icon>
          Manage
        </v-btn>
      </template>
      <v-card>
        <v-list>
          <v-list-item link to="/feedback">
            <v-icon left>mdi-bug</v-icon>
            <v-list-item-title>Feedback</v-list-item-title>
          </v-list-item>
          <v-list-item v-if="$perms.is_admin" link to="/admin">
            <v-icon left>mdi-cogs</v-icon>
            <v-list-item-title>Admin</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
export default {};
</script>

<style lang="scss" scoped></style>
