<template>
  <v-dialog v-model="dialog" persistent class="workgroup-root">
    <filter-table
      :loading="loading"
      :headers="filtered_headers"
      :items="filtered_workgroups"
      :options.sync="options"
      :server-items-length="total_items"
      @dblclick:row="onRowDoubleClick"
      @clear="clearFilters()"
    >
      <!-- CARD TITLE -->
      <template #card:title>
        <span>
          Workgroups
          <span v-show="filters.show_mine">for {{ $auth.user.name }}</span>
        </span>
      </template>

      <!-- DATA -->
      <template #item.id="{ item }">
        <e-btn tooltip="Copy Url" text @click="copyWorkgroupUrl(item.id)">
          {{ item.id }}
        </e-btn>
      </template>

      <template #item.is_archived="{ item }">
        <v-progress-circular v-if="loaders.archive_status" indeterminate color="primary" />
        <template v-else>
          <e-icon-btn
            :color="!item.is_archived ? 'success' : ''"
            tooltip="Active"
            @click="updateArchiveStatus(item.id, false)"
          >
            mdi-account-supervisor-circle
          </e-icon-btn>
          <e-icon-btn
            :color="item.is_archived ? 'warning' : ''"
            tooltip="Archive"
            @click="updateArchiveStatus(item.id, true)"
          >
            mdi-archive-outline
          </e-icon-btn>
        </template>
      </template>

      <template #item.edit="{ item }">
        <e-icon-btn tooltip="Edit Workgroup" @click="handleWorkgroup(item)"> mdi-pencil </e-icon-btn>
      </template>

      <template #item.title="{ item }">
        <v-tooltip bottom max-width="300">
          <template #activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">{{ item.title }}</span>
          </template>
          <span>{{ item.description }}</span>
        </v-tooltip>
      </template>
    </filter-table>
    <!-- ACTIONS -->
    <v-card-actions>
      <cancel-btn @click="cancel()" />
      <v-spacer />
      <save-btn @click="submit()" />
    </v-card-actions>
  </v-dialog>
</template>

<script>
export default {
  data() {
    return {
      dialog: false,

      // loading
      loading: false,
      loaders: {
        filters: false,
        archive_status: false,
        options: false,
      },
      // workgroup
      workgroups: [],
      // table props
      total_items: 0,
      options: {
        itemsPerPage: 20,
        sortBy: ['updated'],
        sortDesc: [true],
      },
      // table header
      headers: [
        {
          text: '#',
          align: 'center',
          value: 'id',
          sortable: false,
          divider: true,
          hide: false,
          width: '10',
        },
        {
          text: 'Edit',
          value: 'edit',
          align: 'center',
          sortable: false,
          hide: false,
          width: '10',
          divider: true,
        },
        {
          text: 'Date Created',
          value: 'created',
          formatter: (x) => this.$format.date(x),
          hide: false,
          width: '10',
          divider: true,
        },
        {
          text: 'Last Updated',
          value: 'updated',
          formatter: (x) => this.$format.date(x),
          hide: false,
          width: '10',
          divider: true,
        },
        {
          text: 'Workgroup',
          value: 'title',
          cellClass: 'wrap-text',
          hide: false,
          width: '500',
          divider: true,
        },
        {
          text: 'Owners',
          value: 'owner_ids',
          hide: false,
          formatter: (x) =>
            x
              .map((a) => this.$utils.getUserName(a))
              .sort()
              .join(', '),
          width: '350',
          divider: true,
          sortable: false,
        },
        {
          text: 'Admins',
          value: 'admin_ids',
          hide: false,
          formatter: (x) =>
            x
              .map((a) => this.$utils.getUserName(a))
              .sort()
              .join(', '),
          width: '350',
          divider: true,
          sortable: false,
        },
        {
          text: 'Functional Location',
          value: 'functional_location',
          hide: false,
          width: '320',
          divider: true,
        },
        {
          text: 'Is Active',
          value: 'closed',
          hide: false,
          width: '10',
          divider: true,
          formatter: (x) => (x ? 'Inactive' : 'Active'),
        },
      ],

      // // filters
      // global_text: null,
      // title_text: null,
      filters: {
        //   show_mine: false,
        //   global_text: null,
        id: null,
        //   function_location: [],
        //   site: [],
        //   department: [],
        //   status: [],
        //   source: [],
        //   priority: [],
        //   date_closed: {
        //     min_date: null,
        //     max_date: null,
        //   },
        //   date_due: {
        //     min_date: null,
        //     max_date: null,
        //   },
        //   date_closed: {
        //     min_date: null,
        //     max_date: null,
        //   },
        //   created_date: {
        //     min_date: null,
        //     max_date: null,
        //   },
        //   updated_date: {
        //     min_date: null,
        //     max_date: null,
        //   },
        //   title: null,
        //   description: null,
        //   owner_ids: [],
        //   supervisor_id: [],
        //   archive_status: null,
      },
    }
  },
  computed: {
    filtered_workgroups() {
      if (this.$perms.is_admin) return this.workgroups
      else return this.workgroups.filter((x) => !x.is_archived)
    },
    filtered_headers() {
      this.headers.push({
        text: 'Archive',
        value: 'is_archived',
        align: 'center',
        divider: true,
        hide: !this.$perms.is_admin,
        width: '10',
      })

      return this.headers
    },
  },
  watch: {
    // trigger loadData when /workgroup?id=x <-> /workgroup
    '$route.query'() {
      this.loadData()
    },
    options: {
      handler() {
        this.loaders.options = true
        // do not loadData if `filter handler` is triggered (expensive task)
        if (!this.loaders.filter) this.loadData()
      },
      deep: true,
    },
    filters: {
      handler() {
        this.loaders.filter = true
        // do not loadData if `options handler` is triggered (expensive task)
        if (!this.loaders.options) this.loadData()
      },
      deep: true,
    },
  },
  methods: {
    open() {
      this.dialog = true

      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },
    cancel(status = false) {
      this.resolve(status)
      this.dialog = false
    },
    submit() {
      // handle data how you want and resolve res
      // e.g.
      // this.resolve(this.data)
      // this.dialog = false
    },
    // -----------------------------
    // TABLE DATA
    // -----------------------------
    filterWorkgroupsFromID(workgroup_id) {
      this.loading = true
      this.$axios
        .$get('/workgroup', { params: { id: workgroup_id } })
        .then((res) => {
          this.workgroups = res
          this.total_items = res.length
          this.loading = false
        })
        .catch((err) => console.error(err))
    },
    loadData() {
      const query = this.$route.query
      if (Object.keys(query).includes('id')) {
        this.filterWorkgroupsFromID(query.id)
        return
      }

      // ---------------------------------------

      let { sortBy, sortDesc, page, itemsPerPage } = this.options

      if (!page) page = 1

      const dates = ['date_closed', 'incident_date', 'updated_date']
      const X = (v, k) => {
        if (Array.isArray(v)) {
          return v.length > 0 ? true : undefined
        }

        if (dates.includes(k)) {
          return !!v.min_date || !!v.max_date || undefined
        }

        return v ? true : undefined
      }

      const api_filters = {}

      // standard users can only see non-archived items, admins can see everything
      if (!this.$perms.is_admin) api_filters.archive_status = 2

      for (const [k, v] of Object.entries(this.filters)) {
        const temp = X(v, k)
        if (temp != undefined) {
          api_filters[k] = v
        }
      }

      if (!sortBy || sortBy.length == 0) {
        sortBy = ['updated']
        sortDesc = [true]
      }

      const data = {
        sort_by: sortBy,
        sort_desc: sortDesc,
        filters: api_filters,
      }

      this.loading = true
      this.$axios
        .$post('/workgroup/get_page', data, {
          params: {
            page,
            count: itemsPerPage,
          },
        })
        .then((res) => {
          this.total_items = res.count
          this.workgroups = res.items

          // ------------------

          // reset loaders
          this.loaders.filter = false
          this.loaders.options = false
        })
        .finally(() => (this.loading = false))
    },
    // -----------------------------
    // WORKGROUP
    // -----------------------------
    handleWorkgroup(workgroup) {
      this.$refs.workgroup_form
        .open(workgroup)
        .then((res) => {
          // dialog cancelled
          if (res == false) return

          // handle res from submit
          this.updateWorkgroup(res)
        })
        .catch((err) => console.error(err))
    },
    updateWorkgroup(payload) {
      this.$axios
        .$put('/workgroup', payload)
        .then((res) => {
          this.loadData()

          // --------------------------------

          this.$snackbar.add(`Workgroup Created Successfully`)
        })
        .catch((err) => console.error(err))
    },
    // -----------------------------
    // ARCHIVE STATUS
    // -----------------------------
    updateArchiveStatus(id, flag) {
      // don't update if you don't need to
      const workgroup = this.workgroups.filter((x) => x.id == id)[0]
      if (workgroup.is_archived == flag) return

      // update process
      this.loaders.archive_status = true
      this.$axios
        .$patch('/workgroup/update_archive_status', null, {
          params: {
            workgroup_id: id,
            is_archived: flag,
          },
        })
        .then(() => {
          const idx = this.workgroups.findIndex((x) => x.id == id)
          this.workgroups[idx].is_archived = flag

          // --------------------------------------------

          this.loaders.archive_status = false
        })
        .catch((err) => {
          console.error(err)
        })
    },
    // -----------------------------
    // OTHER
    // -----------------------------
    onRowDoubleClick(_, payload) {
      this.handleWorkgroup(payload.item)
    },
    copyWorkgroupUrl(id) {
      const text = `${window.location.origin}/workgroups?id=${id}`
      navigator.clipboard.writeText(text)

      this.$snackbar.add(`Workgroup URL Copied!`, 'info')
    },
  },
}
</script>

<style lang="scss" scoped>
.workgroup-root {
  height: 100%;

  ::v-deep {
    .wrap-text {
      overflow-wrap: anywhere;
    }
  }
}
</style>
