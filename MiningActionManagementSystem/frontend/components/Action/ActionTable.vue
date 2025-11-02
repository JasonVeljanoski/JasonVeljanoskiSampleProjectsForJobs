<template>
  <v-card outlined elevation="0">
    <v-card-title class="att-title">
      Actions
      <v-spacer />
      <slot name="card:header" />
    </v-card-title>
    <v-divider />
    <v-card-text v-if="actions.length == 0" class="my-2"> No actions. </v-card-text>
    <e-data-table
      v-else
      :headers="headers"
      :items="actions"
      fixed-header
      :options="{
        itemsPerPage: 10,
        sortBy: ['priority', 'status', 'date_due'],
        sortDesc: [false, false, false],
      }"
      :footer-props="{
        'items-per-page-options': [],
      }"
      class="action-table"
    >
      <template #item.id="{ item }">
        <e-icon-btn tooltip="Edit Action" @click="$emit('edit', item)"> mdi-pencil </e-icon-btn>
      </template>
      <template #item.title="{ item }">
        <v-tooltip bottom max-width="300">
          <template #activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">{{ item.title }}</span>
          </template>
          <span>{{ item.description }}</span>
        </v-tooltip>
      </template>
    </e-data-table>
  </v-card>
</template>

<script>
import ShowMetadataPopup from '@/components/Action/ShowMetadataPopup.vue'
import PrivacyEnumIcon from '@/components/Icon/PrivacyEnumIcon.vue'
import PriorityEnumIcon from '@/components/Icon/PriorityEnumIcon.vue'
import StatusEnumIcon from '@/components/Icon/StatusEnumIcon.vue'

export default {
  props: {
    actions: { type: Array, default: () => [] },
  },
  data() {
    return {
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
          text: 'Privacy',
          value: 'privacy',
          component: PrivacyEnumIcon,
          width: '10',
          divider: true,
          align: 'center',
        },
        {
          text: 'Action',
          value: 'title',
          cellClass: 'wrap-text',
          width: '320',
          divider: true,
        },
        {
          text: 'Source',
          value: 'type',
          width: '10',
          divider: true,
        },
        {
          text: 'Priority',
          value: 'priority',
          align: 'center',
          component: PriorityEnumIcon,
          width: '10',
          divider: true,
        },
        {
          text: 'Status',
          value: 'status',
          align: 'center',
          component: StatusEnumIcon,
          width: '10',
          divider: true,
        },
        {
          text: 'Date Due',
          value: 'date_due',
          formatter: (x) => this.$format.date(x),
          width: '10',
          divider: true,
        },
        {
          text: 'Start Date',
          value: 'start_date',
          formatter: (x) => this.$format.date(x),
          width: '10',
          divider: true,
        },

        {
          text: 'Date Closed',
          value: 'date_closed',
          cellClass: 'nowrap',
          hide: false,
          formatter: (x) => (x ? this.$format.date(x) : ''),
          width: '10',
          divider: true,
        },
        // {
        //   text: 'Date Created',
        //   value: 'created',
        //   formatter: (x) => this.$format.date(x),
        //   width: '125',
        //   width: '10',
        //   divider: true,
        // },
        // {
        //   text: 'Last Updated',
        //   value: 'updated',
        //   formatter: (x) => this.$format.date(x),
        //   width: '125',
        //   width: '10',
        //   divider: true,
        // },

        {
          text: 'Owner',
          value: 'owner_id',
          cellClass: 'nowrap',
          formatter: (x) => this.$utils.getUserName(x),
          width: '10',
          divider: true,
        },
        {
          text: 'Members',
          value: 'member_ids',
          hide: false,
          formatter: (x) =>
            x
              .map((a) => this.$utils.getUserName(a))
              .sort()
              .join(', '),
          cellClass: 'title-cell',
          divider: true,
          sortable: false,
        },
        {
          text: 'Supervisor',
          value: 'supervisor_id',
          formatter: (x) => this.$utils.getUserName(x),
          cellClass: 'nowrap',
          hide: false,
          divider: true,
        },
        {
          text: 'Metadata',
          value: 'action_metadata',
          align: 'center',
          width: '10',
          divider: true,
          sortable: false,
          component: ShowMetadataPopup,
        },
      ],
    }
  },

  methods: {
    copyActionUrl(id) {
      const text = `${window.location.origin}/actions?id=${id}`
      navigator.clipboard.writeText(text)
    },
  },
}
</script>

<style lang="scss" scoped>
.att-title {
  font-size: 16px;
}

::v-deep {
  .action-table > * > table > * > tr > * {
    &:nth-child(-n + 1) {
      position: sticky;
      z-index: 2;
      background: var(--default-background);
    }

    &:nth-child(1) {
      left: 0;
    }
  }
  .action-table > * > table > * > tr > th {
    &:nth-child(-n + 1) {
      z-index: 5;
    }
  }
}
</style>
