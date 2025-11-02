<template>
  <div>
    <i v-if="!$perms.is_admin">You are not an admin</i>

    <template v-else>
      <v-tabs v-model="tab" outlined class="mb-4">
        <v-tab>User Permissions</v-tab>
        <v-tab>Dashboard Edit</v-tab>
        <v-tab>Distribution List</v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab" class="tab-items">
        <v-tab-item class="tab-items">
          <permissions-table />
        </v-tab-item>

        <v-tab-item class="tab-items">
          <dashboard-edit-table />
        </v-tab-item>
        <v-tab-item class="tab-items">
          <distribution-list-table />
        </v-tab-item>
      </v-tabs-items>
    </template>
  </div>
</template>

<script>
import PermissionsTable from "@/components/Admin/PermissionsTable";
import DistributionListTable from "@/components/Admin/DistributionListTable";
import DashboardEditTable from "@/components/Dashboards/DashboardEditTable.vue";

export default {
  components: {
    PermissionsTable,
    DashboardEditTable,
    DistributionListTable,
  },
  head() {
    return {
      title: "Admin",
    };
  },
  data() {
    return {
      tab: 0,
    };
  },
};
</script>

<style lang="scss" scoped>
.tab-items {
  .theme--light & {
    background: #f8f8f8;
  }
  .theme--dark & {
    background: rgb(18, 18, 18);
  }
}
</style>
