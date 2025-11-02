import PriorityEnumIcon from '@/components/Icon/PriorityEnumIcon.vue'
import StatusEnumIcon from '@/components/Icon/StatusEnumIcon.vue'

export default ({ app, store }, inject) => {
  inject('action_utils', {
    // -----------------------------------------
    // REQUIRED FIELDS
    // -----------------------------------------
    required_fields: {
      // required
      title: true,
      description: true,
      owner_id: true,
      status: true,
      priority: true,

      // not required
      completed: true,
      supervisor_id: true,
      member_ids: true,
      functional_location: true,
      work_center: true,
      link: true,
      start_date: true,
      date_due: true,
      date_closed: true,
    },
    // -----------------------------------------
    // EDITABLE FIELDS BY ACTION SOURCE
    // -----------------------------------------
    editable_action_fields: {
      ACE: {
        // BASE ACTION FIELDS
        // required
        title: true,
        description: true,
        owner_id: true,
        status: true,
        priority: true,

        // not required
        completed: true,
        supervisor_id: true,
        member_ids: true,
        functional_location: true,
        work_center: true,
        link: true,
        start_date: true,
        date_due: true,
        date_closed: true,
      },
      BMS_ACT: {
        // BASE ACTION FIELDS
        // required
        title: false,
        description: false,
        owner_id: false,
        status: false,
        priority: false,

        // not required
        completed: true,
        supervisor_id: false,
        member_ids: false,
        functional_location: true,
        work_center: true,
        link: false,
        start_date: false,
        date_due: false,
        date_closed: true,
      },
      BMS_CR: {
        // BASE ACTION FIELDS
        // required
        title: false,
        description: false,
        owner_id: false,
        status: false,
        priority: false,

        // not required
        completed: true,
        supervisor_id: false,
        member_ids: false,
        functional_location: true,
        work_center: true,
        link: false,
        start_date: false,
        date_due: false,
        date_closed: true,
      },
      BMS_HZD: {
        // BASE ACTION FIELDS
        // required
        title: false,
        description: false,
        owner_id: false,
        status: false,
        priority: false,

        // not required
        completed: true,
        supervisor_id: false,
        member_ids: false,
        functional_location: true,
        work_center: true,
        link: false,
        start_date: false,
        date_due: false,
        date_closed: true,
      },
      BMS_ITR: {
        // BASE ACTION FIELDS
        // required
        title: false,
        description: false,
        owner_id: false,
        status: false,
        priority: false,

        // not required
        completed: true,
        supervisor_id: false,
        member_ids: false,
        functional_location: true,
        work_center: true,
        link: false,
        start_date: false,
        date_due: false,
        date_closed: true,
      },
      SMH: {
        // BASE ACTION FIELDS
        // required
        title: false,
        description: false,
        owner_id: false,
        status: false,
        priority: false,

        // not required
        completed: true,
        supervisor_id: true,
        member_ids: false,
        functional_location: false,
        work_center: true,
        link: false,
        start_date: false,
        date_due: false,
        date_closed: false,
      },
      AHM: {
        // BASE ACTION FIELDS
        // required
        title: false,
        description: true,
        owner_id: true,
        status: false,
        priority: false,

        // not required
        completed: true,
        supervisor_id: true,
        member_ids: true,
        functional_location: false,
        work_center: true,
        link: false,
        start_date: false,
        date_due: true,
        date_closed: true,
      },
      SAP_Work_Order: {
        // BASE ACTION FIELDS
        // required
        title: false,
        description: true,
        owner_id: true,
        status: false,
        priority: false,

        // not required
        completed: true,
        supervisor_id: true,
        member_ids: true,
        functional_location: false,
        work_center: false,
        link: false,
        start_date: false,
        date_due: false,
        date_closed: false,
      },
      SAP_Notification: {
        // BASE ACTION FIELDS
        // required
        title: false,
        description: true,
        owner_id: true,
        status: false,
        priority: false,

        // not required
        completed: true,
        supervisor_id: true,
        member_ids: true,
        functional_location: false,
        work_center: false,
        link: false,
        start_date: false,
        date_due: false,
        date_closed: false,
      },
      Teams: {
        // BASE ACTION FIELDS
        // required
        title: false,
        description: false,
        owner_id: false,
        status: false,
        priority: false,

        // not required
        completed: false,
        supervisor_id: false,
        member_ids: false,
        functional_location: true,
        work_center: true,
        link: true,
        start_date: false,
        date_due: false,
        date_closed: false,
      },
      DEP: {
        // BASE ACTION FIELDS
        // required
        title: false,
        description: false,
        owner_id: false,
        status: false,
        priority: false,

        // not required
        completed: false,
        supervisor_id: false,
        member_ids: false,
        functional_location: false,
        work_center: true,
        link: false,
        start_date: true,
        date_due: false,
        date_closed: false,
      },
    },
    // -----------------------------------------
    // TABLE HEADERS
    // -----------------------------------------
    base_headers: [
      {
        text: 'Act',
        value: 'act',
        align: 'center',
        divider: true,
        sortable: false,
        hide: false,
        width: '10',
      },
      {
        text: 'State',
        value: 'state',
        align: 'center',
        divider: true,
        sortable: false,
        hide: false,
        width: '10',
      },
      {
        text: 'Meta',
        value: 'metadata',
        align: 'center',
        divider: true,
        sortable: false,
        hide: false,
        width: '10',
      },
      {
        text: 'Action',
        value: 'title',
        cellClass: 'title-cell',
        divider: true,
      },
      {
        text: 'Source',
        value: 'type',
        width: '10',
        formatter: (x) => x.replaceAll('_', ' '),
        cellClass: 'nowrap',
        divider: true,
      },
      {
        text: 'Assigned To',
        value: 'owner_id',
        cellClass: 'nowrap',
        formatter: (x) => app.$utils.getUserName(x),
        width: '10',
        divider: true,
      },
      {
        text: 'Members',
        value: 'member_ids',
        hide: false,
        formatter: (x) =>
          x
            .map((a) => app.$utils.getUserName(a))
            .sort()
            .join(', '),
        cellClass: 'title-cell',
        divider: true,
        sortable: false,
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
        formatter: (x) => app.$format.date(x),
        width: '10',
        divider: true,
      },
      {
        text: 'FLOC',
        value: 'functional_location',
        cellClass: 'nowrap',
        divider: true,
        width: '10',
      },
      {
        text: 'Work Center',
        value: 'work_center',
        cellClass: 'nowrap',
        divider: true,
      },
      // other action fields
      {
        text: 'Supervisor',
        value: 'supervisor_id',
        formatter: (x) => app.$utils.getUserName(x),
        cellClass: 'nowrap',
        hide: false,
        divider: true,
      },
      {
        text: 'Start Date',
        value: 'start_date',
        formatter: (x) => app.$format.date(x),
        width: '10',
        divider: true,
      },
      {
        text: 'Date Closed',
        value: 'date_closed',
        cellClass: 'nowrap',
        hide: false,
        formatter: (x) => (x ? app.$format.date(x) : ''),
        width: '10',
        divider: true,
      },
      {
        text: 'Archive',
        value: 'is_archived',
        align: 'center',
        divider: true,
        hide: false,
        width: '10',
      },
    ],
    metadata_headers: {
      ACE: [],
      BMS_ACT: [
        {
          text: 'Discipline',
          value: 'action_metadata.discipline',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Category',
          value: 'action_metadata.category',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Location',
          value: 'action_metadata.location',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
      ],
      BMS_CR: [
        {
          text: 'Discipline',
          value: 'action_metadata.discipline',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Category',
          value: 'action_metadata.category',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Location',
          value: 'action_metadata.location',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
      ],
      BMS_HZD: [
        {
          text: 'Discipline',
          value: 'action_metadata.discipline',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Category',
          value: 'action_metadata.category',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Location',
          value: 'action_metadata.location',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
      ],
      BMS_ITR: [
        {
          text: 'Discipline',
          value: 'action_metadata.discipline',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Category',
          value: 'action_metadata.category',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Location',
          value: 'action_metadata.location',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
      ],
      SAP_Work_Order: [
        {
          text: 'System Status',
          value: 'action_metadata.system_status',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'User Status',
          value: 'action_metadata.user_status',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Group',
          value: 'action_metadata.group',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Notification Number',
          value: 'action_metadata.notification_number',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Order Type',
          value: 'action_metadata.order_type',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
      ],
      SAP_Notification: [
        {
          text: 'System Status',
          value: 'action_metadata.system_status',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'User Status',
          value: 'action_metadata.user_status',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Notification Type',
          value: 'action_metadata.notification_type',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
      ],
      SMH: [
        {
          text: 'Classification',
          value: 'action_metadata.classification',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Last Comments',
          value: 'action_metadata.last_comments',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
      ],
      AHM: [
        {
          text: 'Notification Number',
          value: 'action_metadata.notification_number',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Asset ID',
          value: 'action_metadata.asset_id',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Equipment Description',
          value: 'action_metadata.equipment_description',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Object Type',
          value: 'action_metadata.object_type',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Technology',
          value: 'action_metadata.technology',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
      ],
      Teams: [
        {
          text: 'Checklist',
          value: 'action_metadata.checklist',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Bucket',
          value: 'action_metadata.bucket',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
        {
          text: 'Board',
          value: 'action_metadata.board',
          cellClass: 'nowrap',
          divider: true,
          sortable: false,
        },
      ],
    },
  })
}
