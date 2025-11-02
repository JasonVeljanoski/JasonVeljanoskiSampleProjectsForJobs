<template>
  <span>
    <filter-table
      ref="filter_table"
      :headers="headers"
      :items="items"
      :filters="filters"
      :options.sync="options"
      :server-items-length="total_items"
      :expanded.sync="expanded"
      single-expand
      disable-sort
      show-expand
      :loading="loading"
      title="Groups"
      save_key="groups"
      @reload="loadData"
    >
      <!-- CARD TITLE -->
      <template #card:title>
        {{ group_title }}
      </template>

      <!-- CARD HEADER -->
      <template #card:header>
        <v-text-field
          v-model="global_text"
          v-bind="$bind.select"
          clearable
          placeholder="Global Text Search"
          prepend-inner-icon="mdi-magnify"
          style="max-width: 350px"
          @keyup.native.enter="$event.target.blur()"
          @blur="searchGlobalText"
          @click:clear="clearGlobalText"
        />

        <v-btn v-bind="$bind.btn" @click="handleGroup()">
          <v-icon left>mdi-pencil</v-icon>
          new group
        </v-btn>

        <v-btn-toggle
          v-model="ace_filter"
          mandatory
          class="d-flex justify-center"
          active-class="primary--text"
          outlined
          dense
          @change="aceFilterChange"
        >
          <v-btn v-for="(tab, ii) in tab_headers" :key="ii" :value="ii">
            <span>{{ tab.text }}</span>
            <v-icon :color="ace_filter == ii ? 'primary' : ''" right>
              {{ tab.icon }}
            </v-icon>
          </v-btn>
        </v-btn-toggle>
      </template>

      <!-- CARD FOOTER -->
      <template #footer.prepend>
        <cancel-btn tooltip="Reset Filters" @click="resetFilters">
          <v-icon left>mdi-restart</v-icon>
          Filters
        </cancel-btn>
      </template>

      <!-- DATA -->
      <template #item.id="{ item }">
        <copy-icon-btn tooltip_text="Copy Group Link" @click="copyGroupUrl(item.id)">
          {{ item.id }}
        </copy-icon-btn>
      </template>

      <template #item.privacy="{ item }">
        <privacy-updater :value="item.privacy" />
      </template>

      <template #item.is_archived="{ item }">
        <archive-toggle
          :value="item.is_archived"
          :disabled="!$workgroup_perms.canEdit(item.owner_id, item.admin_ids)"
          @toggle="updateArchiveStatus(item.id, item.is_archived)"
        />
      </template>

      <template #item.edit="{ item }">
        <e-icon-btn
          :disabled="!$workgroup_perms.canEdit(item.owner_id, item.admin_ids)"
          tooltip="Edit Group"
          @click="handleGroup(item)"
        >
          mdi-pencil
        </e-icon-btn>
      </template>

      <template #item.title="{ item }">
        <v-tooltip bottom max-width="300">
          <template #activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">{{ item.title }}</span>
          </template>
          <span>{{ item.description }}</span>
        </v-tooltip>
      </template>

      <template #item.data-table-expand="{ item, isExpanded }">
        <v-badge
          :color="getActionCount(item) ? 'error' : ''"
          overlap
          offset-x="14"
          offset-y="18"
          :content="String(getActionCount(item)) ? getActionCount(item) : null"
          @click="isExpanded = !isExpanded"
        >
          <e-icon-btn :tooltip="groupActionsTooltip(item)" @click="handleExpansion(item, isExpanded)">
            {{ isExpanded ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
          </e-icon-btn>
        </v-badge>
      </template>

      <template #expanded-item="{ headers, item }">
        <td :colspan="headers.length" class="expanded-cell">
          <div :style="{ width: table_width + 'px' }">
            <simple-action-table :workgroup="item" :loading="actionsLoading" @trigger_reload="triggerReload">
              <template #card:header>
                <e-icon-btn tooltip="Fullscreen Mode" @click="fullScreenMode(item)">mdi-fullscreen</e-icon-btn>
              </template>
            </simple-action-table>
          </div>
        </td>
      </template>

      <template #item.member_ids="{ item }">
        <title-hover-text
          :main_text="
            item.member_ids
              .map((a) => $utils.getUserName(a))
              .sort()
              .join(', ')
          "
        >
          <ul v-for="id in item.member_ids" :key="id" style="list-style-type: none; padding: 0">
            <li>{{ $utils.getUserName(id) }}</li>
          </ul>
        </title-hover-text>
      </template>

      <template #item.admin_ids="{ item }">
        <title-hover-text
          :main_text="
            item.admin_ids
              .map((a) => $utils.getUserName(a))
              .sort()
              .join(', ')
          "
        >
          <ul v-for="id in item.admin_ids" :key="id" style="list-style-type: none; padding: 0">
            <li>{{ $utils.getUserName(id) }}</li>
          </ul>
        </title-hover-text>
      </template>
    </filter-table>

    <!-- DIALOGS -->
    <create-update-workgroup-form ref="group_form" @trigger_reload="triggerReload" />
    <group-fullscreen-dialog ref="group_dialog" @trigger_reload="triggerReload" />
  </span>
</template>

<script>
import { mapGetters } from 'vuex'
import CreateUpdateWorkgroupForm from '@/components/Workgroup/CreateUpdateWorkgroupForm.vue'
import FilterTable from '@/components/FilterTable/FilterTable.vue'
import ArchiveToggle from '@/components/Icon/ArchiveToggle.vue'
import BooleanIcon from '@/components/Icon/BooleanIcon.vue'
import CopyIconBtn from '@/components/Icon/CopyIconBtn.vue'
import PrivacyUpdater from '@/components/Workgroup/PrivacyUpdater.vue'
import SimpleActionTable from '@/components/Action/SimpleActionTable.vue'
import GroupFullscreenDialog from '@/components/Workgroup/GroupFullscreenDialog.vue'

export default {
  components: {
    CreateUpdateWorkgroupForm,
    FilterTable,
    ArchiveToggle,
    CopyIconBtn,
    PrivacyUpdater,
    SimpleActionTable,
    GroupFullscreenDialog,
  },
  data() {
    return {
      tab_headers: [
        { text: 'My Groups', icon: 'mdi-account-group' },
        { text: 'All', icon: 'mdi-earth' },
      ],
      // ---
      items: [],
      expanded: [],
      filters: {},
      global_text: null,
      ace_filter: 0,
      extra_filters: {
        my_groups: true,

        global_text: null,
      },
      // ---
      // table props
      loading: false,
      loaders: {
        filters: false,
        archive_status: false,
        options: false,
      },
      total_items: 0,
      options: {
        itemsPerPage: 20,
        sortBy: [],
        sortDesc: [],
      },
      headers: [],
      table_width: 0,
      actionsLoading: false,
    }
  },
  head() {
    return {
      title: 'Groups',
    }
  },
  computed: {
    ...mapGetters({
      users: 'user/getUsers',
      functional_locations: 'lists/getFunctionalLocsPermutations',
      work_centers: 'lists/getWorkcenters',
    }),
    group_title() {
      return this.extra_filters.my_groups ? 'My Groups' : 'All Groups'
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
    total_items() {
      // reset page if table data has changed from filters etc
      if (this.options.page != 1) this.options.page = 1
    },
  },
  mounted() {
    const table = this.$refs.filter_table.$el.querySelector('.filter-table')

    const ro = new ResizeObserver(() => {
      this.table_width = table.clientWidth
    })

    ro.observe(table)

    // ---------------------

    this.resetHeaders()
  },
  methods: {
    // -----------------------------
    // DATA
    // -----------------------------
    filterGroupsFromID(group_id) {
      this.loading = true
      this.$axios
        .$get('/workgroup', { params: { id: group_id } })
        .then((res) => {
          this.items = [res]
          this.total_items = 1
          this.loading = false
        })
        .catch((err) => console.error(err))
    },
    loadData() {
      const query = this.$route.query
      if (Object.keys(query).includes('id')) {
        this.filterGroupsFromID(query.id)
        return
      }

      // ---------------------------------------

      // setup filters
      const filters = []
      for (const [header, { combine, rules }] of Object.entries(this.filters)) {
        if (rules.length) {
          filters.push({
            field: header,
            mode: combine,
            rules,
          })
        }
      }

      // ----------------------------------------

      // extra filters
      const X = (v, k) => {
        if (Array.isArray(v)) {
          return v.length > 0 ? true : undefined
        }

        return v ? true : undefined
      }

      const extra_filters = {}

      for (const [k, v] of Object.entries(this.extra_filters)) {
        const temp = X(v, k)
        if (temp != undefined) {
          extra_filters[k] = v
        }
      }

      // ----------------------------------------

      // setup data
      let { sortBy, sortDesc, page, itemsPerPage } = this.options
      if (!page) page = 1

      const data = {
        sort_by: sortBy,
        sort_desc: sortDesc,
        filters,
        extra_filters,
      }

      // ----------------------------------------

      // get page
      this.loading = true
      this.$axios
        .$post('/workgroup/get_page', data, {
          params: {
            page,
            count: itemsPerPage,
          },
        })
        .then((res) => {
          // res
          this.total_items = res.count
          this.initGroupsForActionsOnRequest(res.items)
          this.items = res.items

          // reset loaders
          this.loaders.filter = false
          this.loaders.options = false
        })
        .finally(() => (this.loading = false))
    },
    initGroupsForActionsOnRequest(items) {
      // init: add new actions key to each item
      for (const item of items) {
        item.actions = []
      }
    },
    getGroupActions(group) {
      if (group.actions?.length === 0) {
        this.actionsLoading = true
        this.$axios.$get('/action/for_group', { params: { workgroup_id: group.id } }).then((res) => {
          group.actions = res
          this.actionsLoading = false
        })
      }
    },
    groupActionsTooltip(item) {
      let message = 'View Actions'

      if (this.getActionCount(item)) {
        message += ` (${item.action_meta.overdue_count} Overdue, ${item.action_meta.due_count} Open and due within 7 days)`
      }

      return message
    },
    // -----------------------------
    // GROUPS
    // -----------------------------
    handleGroup(group) {
      this.$refs.group_form
        .open(group)
        .then((res) => {
          // dialog cancelled
          if (res == false) return

          // handle res from submit
          this.updateGroup(res)
        })
        .catch((err) => console.error(err))
    },
    updateGroup(payload) {
      const form_data = new FormData()
      const group = payload.workgroup
      const attachments = payload.attachments

      for (const x of attachments) form_data.append('attachments', x.file)
      form_data.append('workgroup', JSON.stringify(group))

      // -------------------------------------------------

      this.$axios
        .$put('/workgroup', form_data)
        .then((res) => {
          this.loadData()
          const tag = this.$format.dateTime(res.updated) == this.$format.dateTime(res.created) ? 'Created' : 'Updated'
          this.$snackbar.add(`Group ${tag} Successfully`)
          // --------------------------------

          if (payload.to_email) {
            this.$axios
              .$post('/workgroup/send_email', null, {
                params: { workgroup_id: res.id },
              })
              .catch((err) => console.error(err))
          }
          this.expanded = [] // close dropped down actions belonging to a group if open
        })
        .catch((err) => console.error(err))
    },
    fullScreenMode(workgroup) {
      this.$refs.group_dialog.open(workgroup).catch((err) => console.error(err))
    },
    // -----------------------------
    // FILTER
    // -----------------------------
    aceFilterChange(ii) {
      this.extra_filters.my_groups = ii === 0
      this.extra_filters.all = ii === 1

      this.loadData()
    },
    resetHeaders() {
      this.headers = [
        {
          text: 'Edit',
          value: 'edit',
          align: 'center',
          sortable: false,
          hide: false,
          width: '70',
          divider: true,
        },
        { text: 'Actions', value: 'data-table-expand', divider: true, align: 'center' },
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
          text: 'Privacy',
          value: 'privacy',
          hide: false,
          width: '10',
          divider: true,
          align: 'center',
          filters: {
            field_type: 'select',
            preferred_text: 'Source',
            items: this.$enums.converter(this.$enums.privacy),
            or_only: true,
          },
        },
        {
          text: 'Date Created',
          value: 'created',
          formatter: (x) => this.$format.date(x),
          hide: false,
          width: '10',
          divider: true,
          filters: {
            field_type: 'date',
            formatter: (x) => this.$format.date(x),
          },
        },
        {
          text: 'Last Updated',
          value: 'updated',
          formatter: (x) => this.$format.date(x),
          hide: false,
          width: '10',
          divider: true,
          filters: {
            field_type: 'date',
            formatter: (x) => this.$format.date(x),
          },
        },
        {
          text: 'Is Active',
          value: 'is_active',
          hide: false,
          width: '10',
          divider: true,
          align: 'center',
          component: BooleanIcon,
          filters: {
            field_type: 'boolean',
            or_only: true,
          },
        },
        {
          text: 'Group',
          value: 'title',
          cellClass: 'title-cell',
          hide: false,
          divider: true,
          filters: {
            field_type: 'string',
          },
        },
        {
          text: 'Assigned To',
          value: 'owner_id',
          hide: false,
          cellClass: 'nowrap',
          formatter: (x) => this.$utils.getUserName(x),
          width: '10',
          divider: true,
          filters: {
            field_type: 'select',
            preferred_text: 'Members',
            autocomplete: true,
            items: this.users,
            or_only: true,
            field_props: {
              itemText: 'name',
              itemValue: 'id',
            },
            formatter: (x) => this.$utils.getUserName(x),
          },
        },
        {
          text: 'Members',
          value: 'member_ids',
          hide: false,
          cellClass: 'title-cell',
          formatter: (x) =>
            x
              .map((a) => this.$utils.getUserName(a))
              .sort()
              .join(', '),
          width: '350',
          divider: true,
          sortable: false,
          filters: {
            field_type: 'select',
            preferred_text: 'Members',
            autocomplete: true,
            items: this.users,
            or_only: true,
            field_props: {
              itemText: 'name',
              itemValue: 'id',
            },
            formatter: (x) => this.$utils.getUserName(x),
          },
        },
        {
          text: 'Admins',
          value: 'admin_ids',
          hide: false,
          cellClass: 'title-cell',
          formatter: (x) =>
            x
              .map((a) => this.$utils.getUserName(a))
              .sort()
              .join(', '),
          width: '350',
          divider: true,
          sortable: false,
          filters: {
            field_type: 'select',
            preferred_text: 'Members',
            autocomplete: true,
            items: this.users,
            or_only: true,
            field_props: {
              itemText: 'name',
              itemValue: 'id',
            },
            formatter: (x) => this.$utils.getUserName(x),
          },
        },
        {
          text: 'Functional Location',
          value: 'functional_location',
          hide: false,
          cellClass: 'nowrap',
          divider: true,
          width: '10',
          filters: {
            field_type: 'string',
          },
        },
        {
          text: 'Archive',
          value: 'is_archived',
          align: 'center',
          divider: true,
          hide: false,
          width: '10',
          filters: {
            field_type: 'boolean',
            or_only: true,
          },
        },
      ]
    },
    resetFilters() {
      // reset table options
      this.$refs.filter_table.options_ = {
        sortBy: [],
        sortDesc: [],
        page: 1,
        itemsPerPage: 20,
      }

      // -------------------------

      // if query.id is set, reset from single action view to all action view
      const query = this.$route.query
      if (Object.keys(query).includes('id')) {
        this.$router.replace({ query: null })
      }

      // -------------------------

      // reset globals
      this.global_text = null
      this.ace_filter = 1

      // -------------------------

      this.filters = {}

      this.extra_filters = {
        my_groups: false,
        global_text: null,
      }

      // -------------------------

      this.resetHeaders()

      // -------------------------

      // re-render filters for state to reset
      this.$refs.filter_table.renderFilters()

      // -------------------------

      this.loadData()
    },
    // -----------------------------
    // TEXT SEARCH FILTER
    // -----------------------------
    searchGlobalText() {
      this.extra_filters.global_text = this.global_text

      this.loadData() // reload data on clear
    },
    clearGlobalText() {
      this.extra_filters.global_text = null

      this.loadData() // reload data on clear
    },
    // -----------------------------
    // EXPANSION HANDLERS
    // -----------------------------
    handleExpansion(item, state) {
      // expanded should only have one item in at a time so you can only expand one row at a time
      this.expanded = []
      if (!state) {
        this.getGroupActions(item)
        this.expanded.push(item)
      }
    },
    getActionCount(item) {
      // -------------------------------------------------

      // if actions are already loaded, use those
      if (item.actions?.length > 0) {
        const actions = item.actions.filter((a) => {
          // count overdue actions
          if (a.status === 1) return true

          // -----------------------------
          // count actions due within 7 days
          if (a.date_due === null) return false
          if (a.status !== 2) return false

          const date_due = new Date(a.date_due)
          const today = new Date()
          const diff = date_due - today
          const days = diff / (1000 * 60 * 60 * 24)
          return days <= 7
        })
        return actions.length
      }
      // otherwise, use the action count from server
      else {
        return item.action_meta.total_count
      }
    },
    // -----------------------------
    // ARCHIVE STATUS
    // -----------------------------
    updateArchiveStatus(id, is_archived) {
      const change_status = !is_archived

      // update process
      this.loading = true
      this.$axios
        .$patch('/workgroup/update_archive_status', null, {
          params: {
            workgroup_id: id,
            is_archived: change_status,
          },
        })
        .then(() => {
          this.loadData()
          this.loading = false
        })
        .catch((err) => {
          console.error(err)
        })
    },
    // -----------------------------
    // OTHER
    // -----------------------------
    copyGroupUrl(id) {
      const text = `${window.location.origin}/groups?id=${id}`
      navigator.clipboard.writeText(text)
    },
    triggerReload() {
      // collapse expandable tables
      this.expanded = []

      // load data
      this.loadData()
    },
  },
}
</script>

<style lang="scss" scoped>
::v-deep {
  .filter-table > * > table > * > tr > * {
    &:nth-child(-n + 2) {
      position: sticky;
      z-index: 2;
      background: var(--default-background);
    }

    &:nth-child(1) {
      left: 0;
    }

    &:nth-child(2) {
      left: 70px;
    }
  }
  .filter-table > * > table > * > tr > th {
    &:nth-child(-n + 2) {
      z-index: 4;
    }
  }

  .expanded-cell {
    z-index: 5 !important;
    padding: 0 !important;

    > * {
      padding: 8px;
      overflow: hidden;
      position: sticky;
      left: 0;
      // background-color: var(--v-accent-base);

      > * {
        width: 100%;
      }
    }
  }
}
</style>
