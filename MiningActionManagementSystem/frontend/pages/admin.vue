<template>
  <v-card outlined height="100%">
    <v-tabs v-model="tab">
      <v-tab>Permissions</v-tab>
      <v-tab>User Updates</v-tab>
    </v-tabs>
    <v-divider />
    <v-card-text>
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <permission-helper />
        </v-tab-item>
        <v-tab-item>
          <user-update-helper />
        </v-tab-item>
      </v-tabs-items>
    </v-card-text>
  </v-card>
</template>

<script>
import PermissionHelper from '@/components/Admin/PermissionHelper.vue'
import UserUpdateHelper from '@/components/Admin/UserUpdateHelper.vue'

export default {
  components: {
    PermissionHelper,
    UserUpdateHelper,
  },
  middleware({ $perms, redirect }) {
    if (!$perms.is_admin) {
      return redirect('/actions')
    }
  },
  data() {
    return {
      tab: 0,
    }
  },
  head() {
    return {
      title: 'Admin',
    }
  },
}
</script>

<style lang="scss" scoped></style>
