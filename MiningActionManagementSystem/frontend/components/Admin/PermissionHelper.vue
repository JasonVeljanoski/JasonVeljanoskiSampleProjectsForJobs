<template>
  <div class="admin-root">
    <v-card class="table-wrapper" outlined>
      <v-card-title class="d-flex justify-end align-center header">
        Users
        <v-spacer />
        <v-text-field
          v-model="search"
          v-bind="$bind.select"
          placeholder="Global Text Search"
          clearable
          style="max-width: 250px"
        />
      </v-card-title>

      <v-divider />

      <e-data-table
        class="table"
        fixed-header
        :headers="headers"
        :items="users"
        :search="search"
        :loading="loading"
        :footer-props="{
          'items-per-page-options': [20, 30, 50, 100],
        }"
      >
        <template #item.access="{ item }">
          <div class="d-flex">
            <e-icon-btn
              :color="item.access == 1 ? 'success' : ''"
              :disabled="$auth.user.id == item.id || (!$perms.is_super && item.access == 3)"
              tooltip="Writer"
              @click="changeAccess(item, 1)"
            >
              mdi-pencil
            </e-icon-btn>
            <e-icon-btn
              :color="item.access == 2 ? 'success' : ''"
              :disabled="(!$perms.is_super && item.access == 3) || $auth.user.id == item.id"
              tooltip="Admin"
              @click="changeAccess(item, 2)"
            >
              mdi-account-cog
            </e-icon-btn>
            <e-icon-btn
              :color="item.access == 3 ? 'success' : ''"
              tooltip="Super Admin"
              :disabled="!$perms.is_super || $auth.user.id == item.id"
              @click="changeAccess(item, 3)"
            >
              mdi-shield-crown-outline
            </e-icon-btn>
          </div>
        </template>
      </e-data-table>
    </v-card>
    <settings v-if="$perms.is_super" />
  </div>
</template>

<script>
import Settings from '@/components/Admin/Settings.vue'

export default {
  components: {
    Settings,
  },
  data() {
    return {
      search: null,
      loading: false,
      users: [],
      headers: [
        {
          text: 'Name',
          value: 'name',
          divider: true,
          hide: false,
        },
        {
          text: 'Email',
          value: 'email',
          divider: true,
          hide: false,
        },
        {
          text: 'Job Title',
          value: 'job_title',
          divider: true,
          hide: false,
        },
        {
          text: 'Last Logged In',
          value: 'last_logged_in',
          formatter: (x) => this.$format.date(x),
          divider: true,
          hide: false,
          width: '10',
        },
        {
          text: 'Access',
          value: 'access',
          hide: false,
          width: '10',
        },
      ],
    }
  },
  created() {
    this.getUsers()
  },
  methods: {
    changeAccess(user, access) {
      user.access = access
      this.$axios.$put('/user', user)
    },
    getUsers() {
      this.loading = true
      this.$axios
        .$get('/user/all/basic')
        .then((res) => {
          this.users = res
          this.loading = false
        })
        .catch((err) => {
          console.error(err)
          this.loading = false
        })
    },
  },
}
</script>

<style lang="scss" scoped>
.admin-root {
  height: 100%;
  gap: 8px;
  overflow: hidden;
  display: flex;
  margin-right: auto;
}

.table-wrapper {
  border-radius: 5px;
  max-width: 1200px;

  max-height: 100%;
  display: flex;
  flex-direction: column;
  height: fit-content;
}
</style>
