<template>
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
        <v-list-item>
          <v-list-item-subtitle>
            <table>
              <tr v-for="item in user_data" :key="item.key">
                <td>
                  <b>{{ item.key }}: </b>
                </td>
                <td style="color: var(--v-primary-base)">
                  {{ item.value }}
                </td>
              </tr>
            </table>
          </v-list-item-subtitle>
        </v-list-item>
        <v-divider />
        <user-menu-list-items />
      </v-list>
    </v-card>
  </v-menu>
</template>

<script>
import UserMenuListItems from '@/components/Navigation/UserMenuListItems.vue'

export default {
  components: {
    UserMenuListItems,
  },
  computed: {
    // ---------------------
    // USER DETAILS
    // ---------------------
    user_access() {
      return this.$enums.access[this.$auth.user.access]
    },
    user_sap_number() {
      const sap_num = this.$auth.user.sap_number
      return sap_num || 'NA'
    },
    user_functional_location() {
      if (this.$auth.user.functional_locations) return this.$auth.user.functional_locations.join(', ')
      return 'NA'
    },
    user_workcenters() {
      if (this.$auth.user.work_centers) return this.$auth.user.work_centers.join(', ')
      return 'NA'
    },
    user_back_to_back_email() {
      const back_to_back_email = this.$auth.user.back_to_back_email
      return back_to_back_email || 'NA'
    },
    user_tx_oil_sample() {
      const txoilsample = this.$auth.user.txoilsample
      return txoilsample ? 'Yes' : 'No'
    },
    user_data() {
      return [
        { key: 'Access', value: this.user_access },
        { key: 'SAP #', value: this.user_sap_number },
        { key: 'Functional location', value: this.user_functional_location },
        { key: 'Workcenter', value: this.user_workcenters },
        { key: 'Back to back', value: this.user_back_to_back_email },
        { key: 'TX oil sample', value: this.user_tx_oil_sample },
      ]
    },
  },
}
</script>

<style lang="scss" scoped>
table {
  border-collapse: separate;
  border-spacing: 1em 0.5em;
}
</style>
