export default ({ app }, inject) => {
  inject('enums', {
    priority: {
      1: 'Urgent',
      2: 'High',
      3: 'Medium',
      4: 'Low',
      5: 'Unknown',
    },
    source_systems: {
      ACE: 'ACE',
      AHM: 'AHM',
      BMS_ACT: 'BMS-ACT',
      BMS_CR: 'BMS-CR',
      BMS_HZD: 'BMS-HZD',
      BMS_ITR: 'BMS-ITR',
      DEP: 'DEP',
      SAP_Notification: 'SAP Notification',
      SAP_Work_Order: 'SAP Work Order',
      SMH: 'SMH',
      Teams: 'Teams',
    },
    source_logos: {
      ACE: {
        path: '/ace_logo_light.svg',
        width: 50,
      },
      AHM: {
        path: '/system_logos/ahm.png',
        width: 80,
      },
      BMS_ACT: {
        path: '/system_logos/bms.png',
        width: 60,
      },
      BMS_CR: {
        path: '/system_logos/bms.png',
        width: 60,
      },
      BMS_HZD: {
        path: '/system_logos/bms.png',
        width: 60,
      },
      BMS_ITR: {
        path: '/system_logos/bms.png',
        width: 60,
      },
      DEP: {
        path: '/system_logos/dep.png',
        width: 100,
      },
      SAP_Notification: {
        path: '/system_logos/sap.png',
        width: 60,
      },
      SAP_Work_Order: {
        path: '/system_logos/sap.png',
        width: 60,
      },
      SMH: {
        path: '/system_logos/smh.png',
        width: 60,
      },
      Teams: {
        path: '/system_logos/teams.png',
        width: 40,
      },
    },
    status: {
      1: 'Overdue',
      2: 'Open',
      3: 'On Hold',
      4: 'Closed',
    },
    archive_status: {
      1: 'Active',
      2: 'Archived',
    },
    // -------------------------------------------
    // WORKGROUP
    privacy: {
      1: 'Public',
      3: 'Confidential',
    },

    action_privacy: {
      1: 'Public',
      3: 'Confidential',
    },
    // -----------------------------------------
    // FILE PATHS
    document_paths: {
      general_attachments: '/attachments/general',
    },

    // -------------------------------------------
    // USER
    access: {
      0: 'Reader',
      1: 'Writer',
      2: 'Admin',
      3: 'Super Admin',
    },

    // -------------------------------------------
    // FEEDBACK
    feedback_types: {
      1: 'Bug',
      2: 'General Feedback',
    },
    feedback_status: {
      1: 'Open',
      2: 'On Hold',
      3: 'Closed (Complete)',
      4: 'Closed (Duplicate)',
      5: 'Closed (Feedback Only)',
    },
    // -----------------------------------------

    converter(items) {
      if (Array.isArray(items)) {
        return items
      }

      return Object.entries(items).map(([k, v]) => ({
        value: parseInt(k) || k,
        text: v,
      }))
    },
  })
}
