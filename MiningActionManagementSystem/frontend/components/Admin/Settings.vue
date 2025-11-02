<template>
  <div class="settings-root">
    <v-card v-for="item in lists.filter((x) => x.show)" :key="item.name" outlined>
      <v-card-title>
        {{ item.title }}

        <v-spacer />

        <hidden-text-field placeholder="Enter Email" @submit="addEmail($event, item.name)">
          <template #activator="{ on }">
            <e-icon-btn tooltip="Add User" v-on="on">mdi-plus</e-icon-btn>
          </template>
        </hidden-text-field>
      </v-card-title>
      <v-divider />
      <v-simple-table fixed-header>
        <thead>
          <tr>
            <th>Email</th>
            <th width="40px"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in settings[item.name]" :key="user">
            <td>{{ user }}</td>
            <td>
              <e-icon-btn :disabled="user == $auth.user.email" color="error" @click="removeEmail(user, item.name)">
                mdi-delete
              </e-icon-btn>
            </td>
          </tr>
        </tbody>
      </v-simple-table>
    </v-card>
  </div>
</template>

<script>
export default {
  data() {
    return {
      settings: {},
      lists: [
        {
          name: 'uat_email_whitelist',
          title: 'UAT Email Whitelist',
          show: this.$perms.is_super && process.env.ENV != 'prod',
        },
        {
          name: 'feedback_email_list',
          title: 'Feedback Email List',
          show: this.$perms.is_super,
        },
      ],
    }
  },
  created() {
    this.loadSettings()
  },
  methods: {
    // ------------------------------------------------------
    loadSettings() {
      this.$axios.$get('/settings').then((res) => {
        this.settings = res
      })
    },
    saveSettings() {
      this.$axios.$post('/settings', this.settings)
    },
    // ------------------------------------------------------
    addEmail(email, key) {
      this.settings[key].push(email)
      this.settings[key].sort((a, b) => a.localeCompare(b))

      this.saveSettings()
    },
    removeEmail(email, key) {
      this.settings[key] = this.settings[key].filter((e) => e != email)

      this.saveSettings()
    },
    // ------------------------------------------------------
  },
}
</script>

<style lang="scss" scoped>
.settings-root {
  display: flex;

  gap: 8px;

  overflow: hidden;

  .v-card {
    max-height: 100%;
    height: min-content;
    display: flex;
    flex-direction: column;
    width: 300px;
  }
}
</style>
