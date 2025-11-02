<template>
  <div>
    <v-menu v-if="$auth.user" offset-y>
      <template #activator="{ on, attrs }">
        <e-icon-btn fab small color="primary" v-bind="attrs" v-on="on"> mdi-account </e-icon-btn>
      </template>
      <v-card>
        <v-list>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title class="text-h6">
                {{ $auth.user.name }}
              </v-list-item-title>
              <v-list-item-subtitle>
                {{ $auth.user.email }}
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
          <v-divider />
          <v-list-item @click="$auth.logout()">
            <v-list-item-icon>
              <v-icon>mdi-logout</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title> Sign Out </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
export default {}
</script>

<style lang="scss" scoped></style>
