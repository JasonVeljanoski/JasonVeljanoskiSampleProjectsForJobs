<template>
  <v-card class="table-wrapper" outlined>
    <v-card-title class="d-flex justify-end align-center header">
      Users
      <v-spacer />

      <div style="width: 350px">
        <v-text-field
          v-model="filters.user"
          v-bind="$bind.textfield"
          prepend-inner-icon="mdi-magnify"
          clearable
        />
      </div>
    </v-card-title>

    <v-divider />

    <e-data-table
      class="table"
      fixed-header
      :headers="headers"
      :items="users"
      :loading="loading"
      :options.sync="options"
      :server-items-length="total_items"
      :footer-props="{
        'items-per-page-options': [20, 30, 50, 100],
      }"
    >
      <!-- DATA TABLE SLOTS -->
      <template #item.access="{ item }">
        <div class="d-flex">
          <e-icon-btn
            :color="item.access == 1 ? 'success' : ''"
            :disabled="$auth.user.id == item.id"
            tooltip="Reader"
            @click="updatePermissions(item, 1)"
          >
            mdi-eye
          </e-icon-btn>
          <e-icon-btn
            :color="item.access == 2 ? 'success' : ''"
            :disabled="$auth.user.id == item.id"
            tooltip="Writer"
            @click="updatePermissions(item, 2)"
          >
            mdi-pencil
          </e-icon-btn>
          <e-icon-btn
            :color="item.access == 3 ? 'success' : ''"
            tooltip="Admin"
            @click="updatePermissions(item, 3)"
          >
            mdi-account-cog
          </e-icon-btn>
        </div>
      </template>
    </e-data-table>
  </v-card>
</template>

<script>
export default {
  components: {},
  data() {
    return {
      loading: false,
      search: "",
      options: {
        itemsPerPage: 20,
        sortBy: ["name"],
        sortDesc: [false],
      },
      total_items: 0,
      users: [],
      filters: {
        user: null,
      },
      // table
      headers: [
        {
          text: "Name",
          value: "name",
          divider: true,
          hide: false,
        },
        {
          text: "Email",
          value: "email",
          divider: true,
          hide: false,
        },
        {
          text: "Job Title",
          value: "job_title",
          divider: true,
          hide: false,
        },
        {
          text: "Last Logged In",
          value: "last_logged_in",
          formatter: (x) => this.$format.date(x),
          divider: true,
          hide: false,
          width: "10",
        },
        {
          text: "Access",
          value: "access",
          hide: false,
          width: "10",
        },
      ],
    };
  },
  watch: {
    "filters.user"() {
      this.loadData();
    },
    options: {
      handler() {
        this.loadData();
      },
      deep: true,
    },
  },
  methods: {
    updatePermissions(user, access) {
      if (user.access && user.access == access) return;

      user.access = access;

      this.$axios
        .$put("/user/update_permissions", user)
        .then((res) => {
          let idx = this.users.findIndex((x) => x.id == res.id);
          this.users[idx] = res;
        })
        .catch((err) => {
          console.error(err);
        });
    },
    loadData() {
      let { sortBy, sortDesc, page, itemsPerPage } = this.options;

      if (!page) page = 1;

      let dates = ["date_closed", "incident_date", "updated_date"];
      let X = (v, k) => {
        if (Array.isArray(v)) {
          return v.length > 0 ? true : undefined;
        }

        if (dates.includes(k)) {
          return !!v.min_date || !!v.max_date || undefined;
        }

        return v ? true : undefined;
      };

      let api_filters = {};

      for (let [k, v] of Object.entries(this.filters)) {
        let temp = X(v, k);
        if (temp != undefined) {
          api_filters[k] = v;
        }
      }

      if (!sortBy || sortBy.length == 0) {
        sortBy = ["name"];
        sortDesc = [false];
      }

      let data = {
        sort_by: sortBy,
        sort_desc: sortDesc,
        filters: api_filters,
      };

      this.loading = true;
      this.$axios
        .$post("/user/get_page", data, {
          params: {
            page: page,
            count: itemsPerPage,
          },
        })
        .then((res) => {
          this.total_items = res.count;
          this.users = res.items;
        })
        .finally(() => (this.loading = false));
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;

.table-wrapper {
  border: solid 1px var(--v-accent-base);
  border-radius: 5px;
  max-width: 1200px;
  margin: auto;

  .table {
    max-height: calc(100vh - #{$header-height} - 180px);
    overflow-y: auto;
  }
}
</style>
