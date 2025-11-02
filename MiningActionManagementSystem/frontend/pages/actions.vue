<template>
  <span>
    <filter-table
      ref="action_table"
      :headers="headers"
      :items="items"
      :filters="filters"
      :server-items-length="total_items"
      :loading="loading"
      :options.sync="options"
      title="Actions"
      save_key="actions"
      @reload="loadData"
    >
      <!-- CARD TITLE -->
      <template #card:title>
        {{ action_title }}
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

        <v-btn v-bind="$bind.btn" @click="handleAction()">
          <v-icon left>mdi-pencil</v-icon>
          new ace action
        </v-btn>

        <v-btn-toggle
          v-model="ace_filter"
          mandatory
          class="d-flex justify-center"
          outlined
          dense
          active-class="primary--text"
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
      <template #item.act="{ item }">
        <div class="d-flex align-center" style="gap: 4px">
          <v-badge
            color="primary"
            overlap
            offset-x="16"
            offset-y="20"
            :content="numToFill(item)"
            :value="numToFill(item)"
          >
            <e-icon-btn tooltip="Edit Action" @click="handleAction(item)"> mdi-pencil </e-icon-btn>
          </v-badge>

          <div class="d-flex align-center ml-1" style="gap: 4px">
            <v-menu offset-y>
              <template #activator="{ on }">
                <e-icon-btn v-on="on"> mdi-share-variant </e-icon-btn>
              </template>
              <v-list>
                <v-list-item @click="navigateToSource(item.link)">
                  <v-list-item-title> Go to Source</v-list-item-title>
                  <div class="system_image mr-2">
                    <v-img :src="sourceImgPath(item.type)" :width="sourceImgWidth(item.type)" contain />
                  </div>
                </v-list-item>
                <v-divider />
                <v-list-item @click="copyActionUrl(item.id)">
                  <v-list-item-title>Copy Action Link</v-list-item-title>
                  <div class="system_image mr-2">
                    <v-icon right>mdi-content-paste</v-icon>
                  </div>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </div>
      </template>

      <template #item.metadata="{ item }">
        <show-metadata-popup :value="item.action_metadata" />
      </template>

      <template #item.is_archived="{ item }">
        <archive-toggle
          :value="item.is_archived"
          :disabled="!$perms.canArchive(item.owner_id)"
          @toggle="updateArchiveStatus(item.id, item.is_archived)"
        />
      </template>

      <template #item.title="{ item }">
        <title-hover-text :main_text="item.title">
          <div>
            <h4>Action</h4>
            <p>{{ item.title }}</p>
            <template v-if="item.description">
              <h4>Description</h4>
              <p>{{ item.description }}</p>
            </template>
          </div>
        </title-hover-text>
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
    </filter-table>

    <!-- DIALOGS -->
    <create-update-action-form ref="action_form" @trigger_reload="loadData" />
  </span>
</template>

<script>
import { mapGetters } from 'vuex'
import FilterTable from '@/components/FilterTable/FilterTable.vue'
import PrivacyEnumIcon from '@/components/Icon/PrivacyEnumIcon.vue'
import ProgressBar from '@/components/Icon/ProgressBar.vue'
import CreateUpdateActionForm from '@/components/Action/CreateUpdateActionForm.vue'
import ArchiveToggle from '@/components/Icon/ArchiveToggle.vue'
import ShowMetadataPopup from '@/components/Action/ShowMetadataPopup.vue'
import PriorityEnumIcon from '@/components/Icon/PriorityEnumIcon.vue'
import StatusEnumIcon from '@/components/Icon/StatusEnumIcon.vue'

export default {
  components: {
    FilterTable,
    PrivacyEnumIcon,
    CreateUpdateActionForm,
    ArchiveToggle,
    ShowMetadataPopup,
    ProgressBar,
  },
  data() {
    return {
      tab_headers: [
        { text: 'My ACE', icon: 'mdi-account' },
        { text: 'My Team', icon: 'mdi-account-multiple' },
        { text: 'My Group', icon: 'mdi-account-group' },
        { text: 'All', icon: 'mdi-earth' },
      ],
      // ---
      items: [],
      filters: {},
      global_text: null,
      ace_filter: 0,
      extra_filters: {
        my_ace: true,
        my_team: false,
        my_groups: false,
        all: false,

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
    }
  },
  head() {
    return {
      title: 'Actions',
    }
  },
  computed: {
    ...mapGetters({
      users: 'user/getUsers',
      functional_locations: 'lists/getFunctionalLocsPermutations',
      work_centers: 'lists/getWorkcenters',
    }),
    action_title() {
      if (this.extra_filters.my_ace) return 'My Actions'
      if (this.extra_filters.my_team) return 'My Team Actions'
      if (this.extra_filters.my_groups) return 'My Group Actions'
      return 'All Actions'
    },
  },
  watch: {
    total_items() {
      // reset page if table data has changed from filters etc
      if (this.options.page != 1) this.options.page = 1
    },
    options: {
      handler() {
        this.loadData()
      },
      deep: true,
    },
  },
  mounted() {
    this.resetHeaders()
  },
  methods: {
    // -----------------------------
    // DATA
    // -----------------------------
    filterActionFromID(action_id) {
      this.loading = true
      this.$axios
        .$get('/action', { params: { id: action_id } })
        .then((res) => {
          this.items = res
          this.total_items = res.length
          this.loading = false
        })
        .catch((err) => console.error(err))
    },
    loadData() {
      const query = this.$route.query
      if (Object.keys(query).includes('id')) {
        this.filterActionFromID(query.id)
        return
      }

      // ----------------------------------------

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
        .$post('/action/get_page', data, {
          params: {
            page,
            count: itemsPerPage,
          },
        })
        .then((res) => {
          // res
          this.total_items = res.count
          this.items = res.items

          // update table headers if needed
          this.changeSourceSystem()

          // reset loaders
          this.loaders.filter = false
          this.loaders.options = false
        })
        .finally(() => (this.loading = false))
    },
    // -----------------------------
    // HEADERS
    // -----------------------------
    changeSourceSystem() {
      // type rules exist
      if (this.filters?.type?.rules == undefined || this.filters?.type?.rules.length == 0) return

      // rules
      const combine = this.filters?.type?.combine
      const all_sources = Object.keys(this.$enums.source_systems)
      const equals_filters = this.filters?.type?.rules.filter((x) => x.type === 'equals' && x.value).map((x) => x.value)
      const not_equals_filters = this.filters?.type?.rules
        .filter((x) => x.type === 'does_not_equal' && x.value)
        .map((x) => x.value)
      // const is_empty_filters = this.filters?.type.rules.filter((x) => x.type === 'is_empty').length > 0
      // const is_not_empty_filters = this.filters?.type.rules.filter((x) => x.type === 'is_not_empty').length > 0

      // ----------------------------------------

      // get all sources that exist after filtering rows
      let sources = []

      if (combine === 'or') {
        let x = []
        for (const source of not_equals_filters) x = [...x, ...all_sources.filter((x) => x !== source)]
        x = [...new Set(x)]

        sources = [...new Set([...equals_filters, ...x])]
      } else {
        sources = all_sources.filter((x) => !not_equals_filters.includes(x))

        if (equals_filters.length) {
          sources = sources.filter((x) => equals_filters.includes(x))
        }
      }

      // ----------------------------------------

      // add metadata headers
      this.headers = [...this.headers]

      if (this.filters?.type.rules.length) {
        const headers_without_meta = this.headers.filter((header) => !header.value.includes('metadata'))
        this.headers = [...headers_without_meta]
      }

      for (const source of sources) {
        const meta = this.$action_utils.metadata_headers[source]
        // if any meta in headers
        if (meta) {
          for (const header of meta) {
            if (!this.headers.some((x) => x.value == header.value)) {
              this.headers.push(header)
            }
          }
        }
      }

      // ----------------------------------------

      // always place archive at the end
      this.headers = this.headers.filter((x) => x.value != 'is_archived')
      this.headers.push({
        text: 'Archive',
        value: 'is_archived',
        align: 'center',
        width: '10',
        filters: {
          field_type: 'boolean',
        },
      })
    },
    // -----------------------------
    // ACTIONS
    // -----------------------------
    handleAction(item = null) {
      this.$refs.action_form
        .open(item)
        .then((res) => {
          // dialog cancelled
          if (res == false) return

          // handle res from submit
          this.createUpdateAction(res)
        })
        .catch((err) => console.error(err))
    },
    createUpdateAction(payload) {
      this.loading = true

      const form_data = new FormData()
      const action = payload.action
      const attachments = payload.attachments

      for (const x of attachments) form_data.append('attachments', x.file)
      form_data.append('action', JSON.stringify(action))

      this.$axios
        .$put('/action', form_data)
        .then((res) => {
          this.loadData()

          // --------------------------------
          const message = action.id ? `Action Updated Successfully` : `Action Created Successfully`
          this.$snackbar.add(message)
          this.loading = false
          // --------------------------------

          if (payload.to_email) {
            this.$axios
              .$post('/action/send_email', null, {
                params: { action_id: res.id },
              })
              .catch((err) => console.error(err))
          }
        })
        .catch((err) => {
          console.error(err)
        })
    },
    copyActionUrl(id) {
      const text = `${window.location.origin}/actions?id=${id}`
      navigator.clipboard.writeText(text)
    },
    navigateToSource(link) {
      if (link) window.open(link, '_blank').focus()
    },
    // -----------------------------
    // FILTER
    // -----------------------------
    aceFilterChange(ii) {
      // JW. 2022-11-17: my ace filter removes closed tasks as well
      this.extra_filters.my_ace = ii === 0
      this.extra_filters.my_team = ii === 1
      this.extra_filters.my_groups = ii === 2
      this.extra_filters.all = ii === 3

      this.loadData()
    },
    resetHeaders() {
      this.headers = [
        {
          text: 'Act',
          value: 'act',
          align: 'center',
          width: '10',
          sortable: false,
        },
        {
          text: 'Complete',
          value: 'completed',
          align: 'center',
          width: '10',
          component: ProgressBar,
          sortable: false,
        },
        {
          text: 'Privacy',
          value: 'privacy',
          align: 'center',
          width: '10',
          component: PrivacyEnumIcon,
          filters: {
            field_type: 'select',
            preferred_text: 'Privacy',
            items: this.$enums.converter(this.$enums.privacy),
            or_only: true,
          },
        },
        {
          text: 'Meta',
          value: 'metadata',
          align: 'center',
          width: '10',
          sortable: false,
        },
        {
          text: 'Action',
          value: 'title',
          cellClass: 'title-cell',
          filters: {
            field_type: 'string',
            preferred_text: 'Action',
          },
        },
        {
          text: 'Source',
          value: 'type',
          cellClass: 'nowrap',
          width: '10',
          formatter: (x) => x.replaceAll('_', ' '),
          filters: {
            field_type: 'select',
            preferred_text: 'Source',
            items: this.$enums.converter(this.$enums.source_systems),
            or_only: true,
          },
        },
        {
          text: 'Assigned To',
          value: 'owner_id',
          cellClass: 'nowrap',
          width: '10',
          formatter: (x) => this.$utils.getUserName(x),
          filters: {
            field_type: 'select',
            preferred_text: 'Assigned To',
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
          cellClass: 'title-cell',
          formatter: (x) =>
            x
              .map((a) => this.$utils.getUserName(a))
              .sort()
              .join(', '),
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
          text: 'Priority',
          value: 'priority',
          align: 'center',
          width: '10',
          component: PriorityEnumIcon,
          filters: {
            field_type: 'select',
            items: this.$enums.converter(this.$enums.priority),
            or_only: true,
          },
        },
        {
          text: 'Status',
          value: 'status',
          align: 'center',
          width: '10',
          component: StatusEnumIcon,
          filters: {
            field_type: 'select',
            items: this.$enums.converter(this.$enums.status),
            formatter: (x) => this.$enums.status[x],
            or_only: true,
          },
        },
        {
          text: 'Date Due',
          value: 'date_due',
          width: '10',
          formatter: (x) => this.$format.date(x),
          filters: {
            field_type: 'date',
            formatter: (x) => this.$format.date(x),
          },
        },
        {
          text: 'FLOC',
          value: 'functional_location',
          cellClass: 'nowrap',
          width: '10',
          filters: {
            field_type: 'string',
          },
        },
        {
          text: 'Work Center',
          value: 'work_center',
          cellClass: 'nowrap',
          width: '10',
          filters: {
            field_type: 'string',
          },
        },
        // other action fields
        {
          text: 'Supervisor',
          value: 'supervisor_id',
          cellClass: 'nowrap',
          formatter: (x) => this.$utils.getUserName(x),
          filters: {
            field_type: 'select',
            preferred_text: 'Supervisor',
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
          text: 'Start Date',
          value: 'start_date',
          cellClass: 'nowrap',
          width: '10',
          formatter: (x) => this.$format.date(x),
          filters: {
            field_type: 'date',
            formatter: (x) => this.$format.date(x),
          },
        },
        {
          text: 'Date Closed',
          value: 'date_closed',
          cellClass: 'nowrap',
          width: '10',
          formatter: (x) => (x ? this.$format.date(x) : ''),
          filters: {
            field_type: 'date',
            formatter: (x) => (x ? this.$format.date(x) : ''),
          },
        },
        {
          text: 'Archive',
          value: 'is_archived',
          align: 'center',
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
      this.$refs.action_table.options_ = {
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
      this.ace_filter = 3

      // -------------------------

      this.filters = {}

      this.extra_filters = {
        my_ace: false,
        my_team: false,
        my_groups: false,
        all: true,

        global_text: null,
      }

      // -------------------------

      this.resetHeaders()
      this.changeSourceSystem()

      // -------------------------

      // re-render filters for state to reset
      this.$refs.action_table.renderFilters()

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
    // ARCHIVE STATUS
    // -----------------------------
    updateArchiveStatus(id, is_archived) {
      const change_status = !is_archived

      // update process
      this.loading = true
      this.$axios
        .$patch('/action/update_archive_status', null, {
          params: {
            action_id: id,
            is_archived: change_status,
          },
        })
        .then(() => {
          this.loadData() // reload data on clear
          this.loading = false
        })
        .catch((err) => {
          console.error(err)
        })
    },
    // -----------------------------
    // UTILITY
    // -----------------------------
    numToFill(action) {
      let counter = 0
      const editable_fields = this.$action_utils.editable_action_fields[action.type]
      const required_fields = this.$action_utils.required_fields

      for (const [key, value] of Object.entries(editable_fields)) {
        if (!value || !required_fields[key]) continue
        if (action[key] == null || action[key] == '') counter += 1
      }

      return counter
    },
    // -----------------------------
    // LOGO
    // -----------------------------
    sourceImgPath(source) {
      return this.$enums.source_logos[source].path
    },
    sourceImgWidth(source) {
      return this.$enums.source_logos[source].width * 0.65
    },
  },
}
</script>

<style lang="scss" scoped>
::v-deep {
  .filter-table > * > table > * > tr > * {
    &:nth-child(-n + 1) {
      position: sticky;
      z-index: 2;
      background: var(--default-background);
    }

    &:nth-child(1) {
      left: 0;
    }

    // &:nth-child(2) {
    //   left: 69px;
    // }
  }
  .filter-table > * > table > * > tr > th {
    &:nth-child(-n + 1) {
      z-index: 4;
    }
  }
}

.system_image {
  background-color: white;
  padding: 3px;
  border-radius: 5px;
}
</style>
