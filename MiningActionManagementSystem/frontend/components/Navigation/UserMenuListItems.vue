<template>
  <div>
    <v-list-item @click="openUserProfileDialog">
      <v-list-item-icon>
        <v-icon left>mdi-account-edit</v-icon>
      </v-list-item-icon>

      <v-list-item-title>Edit Profile</v-list-item-title>
    </v-list-item>
    <v-divider />
    <!--
    <template v-if="$perms.is_super">
      <v-list-item @click="impersonateUser">
        <v-list-item-icon>
          <v-icon>mdi-clipboard-account-outline</v-icon>
        </v-list-item-icon>

        <v-list-item-title> Impersonate User </v-list-item-title>
      </v-list-item>
      <v-divider />
    </template>
     -->
    <v-list-item @click="$auth.logout()">
      <v-list-item-icon>
        <v-icon>mdi-logout</v-icon>
      </v-list-item-icon>
      <v-list-item-content>
        <v-list-item-title> Sign Out </v-list-item-title>
      </v-list-item-content>
    </v-list-item>

    <!-- DIALOGS -->
    <user-profile-dialog ref="user_profile_dialog" />
    <user-selector-dialog ref="user_selector_dialog" />
  </div>
</template>

<script>
import UserProfileDialog from '@/components/Navigation/UserProfileDialog.vue'
import UserSelectorDialog from '@/components/Dialogs/UserSelectorDialog.vue'

export default {
  components: {
    UserProfileDialog,
    UserSelectorDialog,
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
  methods: {
    openUserProfileDialog() {
      // note: timeout is set to allow dialog to open inside of v-menus and the like
      // https://github.com/vuetifyjs/vuetify/issues/7021
      setTimeout(() => {
        this.$refs.user_profile_dialog
          .open()
          .then((res) => {
            // dialog cancelled
            if (res == false) return

            // dialog submit
            if (confirm('Are you sure you wish to make these changes to your profile?')) {
              this.$axios.$put('/user', res).then((res) => {
                this.$snackbar.add('Your user profile was updated successfully')

                // refresh page to force $auth.user to update
                // is there a way to safely mutate $auth.user without refresh?
                this.$nextTick(() => {
                  location.reload()
                })
              })
            }
          })
          .catch((err) => console.error(err))
      })
    },
    /*
    impersonateUser() {
      // note: timeout is set to allow dialog to open inside of v-menus and the like
      // https://github.com/vuetifyjs/vuetify/issues/7021
      setTimeout(() => {
        this.$refs.user_selector_dialog.open().then((res) => {
          if (res) {
            this.$axios.$get('/user/impersonate', { params: { id: res.id } }).then((res) => {
              const token = `Bearer ${res.access_token}`
              this.$auth.strategy.token.set(token)
              window.location.reload()
            })
          }
        })
      })
    },*/
  },
}
</script>

<style lang="scss" scoped>
table {
  border-collapse: separate;
  border-spacing: 1em 0.5em;
}
</style>
