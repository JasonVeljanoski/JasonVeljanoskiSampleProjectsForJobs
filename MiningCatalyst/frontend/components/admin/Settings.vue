<template>
  <div v-if="$perms.is_super" class="root">
    <div class="settings-tiles">
      <v-card outlined>
        <v-card-title>Options</v-card-title>
        <v-divider />
        <v-card-text>
          <v-switch v-model="settings.green_nav_bar" label="Green Nav Bar" @change="saveSettings" />
          <v-switch v-model="settings.use_whitelist" label="Use Whitelist" @change="saveSettings" />
        </v-card-text>
      </v-card>

      <v-card v-if="settings.use_whitelist" outlined>
        <v-card-title>
          User Whitelist

          <v-spacer />

          <hidden-text-field placeholder="Enter Email" @submit="addUser">
            <template #activator="{ on }">
              <e-icon-btn tooltip="Add User" v-on="on">mdi-plus</e-icon-btn>
            </template>
          </hidden-text-field>
        </v-card-title>
        <v-divider />
        <v-simple-table>
          <thead>
            <tr>
              <th>Email</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in settings.user_whitelist" :key="user">
              <td>{{ user }}</td>
              <td>
                <e-icon-btn :disabled="user == $auth.user.email" color="error" @click="removeUser(user)">
                  mdi-delete
                </e-icon-btn>
              </td>
            </tr>
          </tbody>
        </v-simple-table>
      </v-card>

      <!-- <v-card outlined>
        <v-card-title>
          Super Users

          <v-spacer />
          <hidden-text-field placeholder="Enter Email" @submit="addSuperUser">
            <template #activator="{ on }">
              <e-icon-btn tooltip="Add User" v-on="on">mdi-plus</e-icon-btn>
            </template>
          </hidden-text-field>
        </v-card-title>
        <v-divider />
        <v-simple-table>
          <thead>
            <tr>
              <th>Email</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in settings.admin_list" :key="user">
              <td>{{ user }}</td>
              <td>
                <e-icon-btn :disabled="user == $auth.user.email" color="error" @click="removeSuperUser(user)">
                  mdi-delete
                </e-icon-btn>
              </td>
            </tr>
          </tbody>
        </v-simple-table>
      </v-card> -->
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  middleware({ $auth, redirect }) {
    if (!$auth.user.is_super) {
      return redirect('/')
    }
  },
  data() {
    return {
      settings: {},
    }
  },
  computed: {
    ...mapGetters({
      store_settings: 'settings/settings',
    }),
  },
  created() {
    this.loadSettings()
  },
  methods: {
    loadSettings() {
      this.$axios.$get('/settings').then((res) => {
        this.settings = res
      })
    },
    // ------------------------------------------------------
    saveSettings() {
      this.$axios.$post('/settings', this.settings).then(() => {
        this.$store.dispatch('settings/load')
      })
    },
    // ------------------------------------------------------
    addUser(email) {
      this.settings.user_whitelist.push(email)
      this.settings.user_whitelist.sort((a, b) => a.localeCompare(b))

      this.saveSettings()
    },
    removeUser(email) {
      this.settings.user_whitelist = this.settings.user_whitelist.filter((e) => e != email)

      this.saveSettings()
    },
    // ------------------------------------------------------
    addSuperUser(email) {
      this.settings.admin_list.push(email)
      this.settings.admin_list.sort((a, b) => a.localeCompare(b))

      this.saveSettings()
    },
    removeSuperUser(email) {
      this.settings.admin_list = this.settings.admin_list.filter((u) => u != email)

      this.saveSettings()
    },
  },
}
</script>

<style lang="scss" scoped>
.root {
  height: 100%;
  overflow: hidden;

  display: flex;
  gap: 8px;
}

.settings-tiles {
  display: flex;
  gap: 8px;

  flex-wrap: wrap;

  > * {
    min-width: 300px;
    flex-shrink: 0;
  }

  height: fit-content;
}
</style>
