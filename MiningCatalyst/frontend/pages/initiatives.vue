<template>
  <filter-table
    :headers="visible_headers"
    :items="items"
    :filters="filters"
    :server-items-length="total_items"
    :loading="loading"
    :options.sync="options"
    :show-header-filters="false"
    title=""
    save_key="initiatives"
    @reload="loadData"
    @changeTab="changeGroup"
  >
    <template #header>
      <thead>
        <tr>
          <th
            v-for="(header, index) in top_headers"
            :key="index"
            :colspan="header.colspan"
            :style="getBottomBorder(header.color)"
            class="grouped-header"
            @click="hideGroup(header.group)"
          >
            <v-icon left small> {{ header.icon }} </v-icon>
            {{ header.group }}
          </th>
        </tr>
      </thead>
    </template>

    <!-- CARD HEADER -->
    <template #card:header>
      <v-btn-toggle v-model="selected_groups" multiple tile color="primary">
        <div :style="getBottomBorder(group.color)" v-for="group in groups" :key="group.name">
          <v-btn :value="group.name" elevation="0" style="border-radius: 0px !important">
            <v-icon left small>{{ group.icon }}</v-icon>
            {{ group.name }}
          </v-btn>
        </div>
      </v-btn-toggle>

      <!-- NAVBAR -->
      <portal to="navbar">
        <v-btn color="primary" v-bind="$bind.btn" @click="createInitiative()">
          <v-icon left>mdi-pencil</v-icon>
          new initiative
        </v-btn>
      </portal>
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
      <div class="d-flex align-center justify-center">
        <e-icon-btn x-small tooltip="Open" @click="updateInitiative(item.id)"> mdi-open-in-new </e-icon-btn>
        <!-- <e-icon-btn x-small tooltip="Archive" @click="archive"> mdi-archive </e-icon-btn> -->
      </div>
    </template>
    <template #item.title="{ item }">
      <hover-title :title="item.title">
        <div
          :class="{ markdown_light: !$vuetify.theme.dark, markdown_dark: $vuetify.theme.dark }"
          class="markdown"
          v-html="item.description"
        />
      </hover-title>
    </template>
  </filter-table>
</template>

<script>
import FilterTable from '@/components/tables/FilterTable.vue'
import HoverTitle from '@/components/tables/format/HoverTitle.vue'
import EnumIcon from '@/components/enco/EnumIcon.vue'
import EnumIcons from '@/components/utils/EnumIcons.vue'

export default {
  components: {
    FilterTable,
    HoverTitle,
  },
  data() {
    return {
      // table
      group_tab: null,
      filters: {},
      extra_filters: {},
      loading: false,
      total_items: 0,
      options: {
        itemsPerPage: 20,
        sortBy: [],
        sortDesc: [],
      },

      headers: [
        {
          text: '#',
          value: 'id',
          width: '10',
          group: null,
          align: 'center',
        },
        {
          text: 'Initiative',
          value: 'title',
          group: null,
          formatter: (x) => this.$format.commarize(x),
          filters: {
            field_type: 'string',
            preferred_text: 'Initiative',
          },
          width: '100',
        },
        {
          text: 'Project Owner',
          value: 'project_owner_id',
          group: 'Summary',
          cellClass: 'nowrap',
          width: '10',
          formatter: (x) => this.$utils.getUserName(x),
        },
        {
          text: 'Project Supervisor',
          value: 'supervisor_id',
          group: 'Summary',
          width: '10',
          cellClass: 'nowrap',
          formatter: (x) => this.$utils.getUserName(x),
        },
        {
          text: 'Priority',
          value: 'priority',
          group: 'Summary',
          align: 'center',
          width: '10',
          component: EnumIcon,
          filters: {
            field_type: 'select',
            items: [],
            or_only: true,
          },
        },
        {
          text: 'Status',
          value: 'status',
          group: 'Summary',
          align: 'center',
          width: '10',
          component: EnumIcon,
          filters: {
            field_type: 'select',
            items: [],
            or_only: true,
          },
        },
        // DETAILS
        {
          text: 'Date Opened',
          value: 'date_opened',
          group: 'Details',
          cellClass: 'nowrap',
          width: '10',
          formatter: (x) => this.$format.date(x),
          filters: {
            field_type: 'date',
            formatter: (x) => this.$format.date(x),
          },
        },
        {
          text: 'Triggers',
          value: 'triggers',
          group: 'Details',
          align: 'center',
          width: '10',
          component: EnumIcons,
          filters: {
            field_type: 'select',
            items: [],
            or_only: true,
          },
        },
        // BENEFITS
        {
          text: 'Cost',
          value: 'cost',
          group: 'Benefits',
          align: 'right',
          width: '10',
          formatter: (x) => (x ? `$${this.$format.commarize(x)}` : ''),
          filters: {
            field_type: 'number',
          },
        },
        {
          text: 'Cost Benefit',
          value: 'cost_benefit_category',
          group: 'Benefits',
          align: 'right',
          width: '10',
          component: EnumIcon,
          filters: {
            field_type: 'select',
            items: [],
            or_only: true,
          },
        },
        {
          text: 'Tonnes',
          value: 'tonnes',
          group: 'Benefits',
          align: 'right',
          width: '10',
          formatter: (x) => this.$format.commarize(x),
          filters: {
            field_type: 'number',
          },
        },
        {
          text: 'Safety',
          value: 'safety',
          group: 'Benefits',
          align: 'right',
          width: '10',
          filters: {
            field_type: 'number',
          },
        },
        {
          text: 'Availability',
          value: 'availability',
          group: 'Benefits',
          align: 'right',
          width: '10',
          filters: {
            field_type: 'number',
          },
        },
        {
          text: 'Events',
          value: 'events',
          group: 'Benefits',
          align: 'right',
          width: '10',
          filters: {
            field_type: 'number',
          },
        },
        {
          text: 'Benefit Frequency',
          value: 'benefit_frequency',
          group: 'Benefits',
          align: 'right',
          width: '10',
          component: EnumIcon,
          filters: {
            field_type: 'select',
            items: [],
            or_only: true,
          },
        },
        {
          text: 'Estimate Notes',
          value: 'estimate_notes',
          group: 'Benefits',
          align: 'right',
          cellClass: 'title-cell',
          width: '10',
          filters: {
            field_type: 'string',
          },
        },
        // SCHEDULE
        {
          text: 'Complete By',
          value: 'target_completion_date',
          group: 'Schedule',
          cellClass: 'nowrap',
          width: '130',
          formatter: (x) => this.$format.date(x),
          filters: {
            field_type: 'date',
            formatter: (x) => this.$format.date(x),
          },
        },
        {
          text: 'Notification',
          value: 'notification',
          group: 'Schedule',
          align: 'right',
          cellClass: 'title-cell',
          width: '10',
          filters: {
            field_type: 'string',
          },
        },
        {
          text: 'Work Order',
          value: 'workorder',
          group: 'Schedule',
          align: 'right',
          cellClass: 'title-cell',
          width: '10',
          filters: {
            field_type: 'string',
          },
        },
        // EXECUTION READINESS
        // todo...
        // BMS
        // todo...
        // COST
        // todo...
        // RISK
        // todo...
      ],

      items: [],

      groups: [
        {
          name: 'Summary',
          icon: 'mdi-chart-bar',
          color: 'primary',
        },
        {
          name: 'Details',
          icon: 'mdi-information-outline',
          color: 'secondary',
        },
        {
          name: 'Benefits',
          icon: 'mdi-finance',
          color: 'success',
        },
        {
          name: 'Schedule',
          icon: 'mdi-calendar',
          color: 'accent',
        },
        {
          name: 'Execution Readiness',
          icon: 'mdi-check-circle-outline',
          color: 'warning',
        },
        {
          name: 'BMS',
          icon: 'mdi-file-document-outline',
          color: 'info',
        },
        {
          name: 'Cost',
          icon: 'mdi-currency-usd',
          color: '',
        },
        {
          name: 'Risk',
          icon: 'mdi-alert-circle-outline',
          color: 'error',
        },
      ],

      selected_groups: ['Summary'],
    }
  },
  head() {
    return {
      title: 'Initiatives',
    }
  },
  computed: {
    visible_headers() {
      return this.headers.filter((x) => {
        if (x.group) {
          return this.selected_groups.includes(x.group)
        } else {
          return true
        }
      })
    },
    top_headers() {
      let top_headers = []

      for (const [index, header] of this.visible_headers.entries()) {
        const group = header.group

        let icon = null
        let color = null

        if (group) {
          const foundGroup = this.groups.find((x) => x.name == group)
          icon = foundGroup?.icon
          color = foundGroup?.color
        }

        const colspan = 1

        let top_header = { colspan, group, icon, color }

        if (index == 0) {
          top_headers.push(top_header)
          continue
        }

        const last_pushed = top_headers[top_headers.length - 1]

        const same_group = last_pushed.group === group

        if (same_group) {
          last_pushed.colspan += 1
        } else {
          top_headers.push(top_header)
        }
      }

      return top_headers
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
    // this.resetHeaders()
  },
  methods: {
    getBottomBorder(color) {
      return { 'border-bottom': `5px solid var(--v-${color}-base) !important` }
    },
    getHeaderStyle(width) {
      return {
        width: `${width}px !important`,
        'min-width': `${width}px !important`,
        'max-width': `${width}px !important`,
      }
    },
    resetFilters() {
      this.filters = {}
      this.extra_filters = {}
      this.options.page = 1
      this.loadData()
    },
    loadData() {
      this.$axios
        .$get('/initiative/all')
        .then((res) => {
          this.items = res
          this.total_items = res.length
        })
        .catch((err) => {
          console.error(err)
        })
    },
    changeGroup(ii) {
      this.group_tab = ii
    },
    hideGroup(group) {
      this.selected_groups = this.selected_groups.filter((x) => x != group)
    },
    // -------------------------------
    // INITIATIVE HELPERS
    // -------------------------------
    createInitiative() {
      this.$router.push('/initiative/new')
    },
    updateInitiative(id) {
      this.$router.push(`/initiative/${id}`)
    },
    // -------------------------------
    // ARCHIVE HELPERS
    // -------------------------------
    archive() {
      if (confirm('Are you sure you want to archive this initiative?')) {
        // todo: archive
        return null
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.grouped-header {
  &:hover {
    cursor: pointer;
  }
}
</style>
