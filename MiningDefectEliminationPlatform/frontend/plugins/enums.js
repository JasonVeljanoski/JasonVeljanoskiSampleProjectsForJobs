export default ({ app }, inject) => {
  inject("enums", {
    // GENERAL
    priority: ["Low", "Medium", "High"],
    action_source: ["Flash Report", "5-Why", "Root Cause"],
    status: {
      1: "Open",
      2: "On Hold",
      3: "Closed",
      4: "Overdue",
    },
    notification_types: {
      1: "info",
      2: "success",
      3: "warning",
    },
    archive_status: {
      1: "Archived",
      2: "Active",
    },
    // -----------------------------------------

    // FEEDBACK
    feedback_types: {
      1: "Bug",
      2: "General Feedback",
    },
    feedback_status: {
      1: "Open",
      2: "On Hold",
      3: "Closed (Complete)",
      4: "Closed (Duplicate)",
      5: "Closed (Feedback Only)",
    },
    // -----------------------------------------

    // USER
    user_permissions: {
      1: "READER",
      2: "WRITER",
      3: "ADMIN",
    },
    access: {
      1: "Reader",
      2: "Writer",
      3: "Admin",
    },
    // -----------------------------------------

    // FILE PATHS
    document_paths: {
      five_why: "/attachments/five_why",
      flash_report: "/attachments/flash_report",
      rca: "/attachments/rca",
      general_attachments: "/attachments/general",
      shared_learnings: "/attachments/shared_learnings",
    },
    img_paths: {
      five_why: "/attachments/imgs/five_why",
      flash_report: "/attachments/imgs/flash_report",
    },
    // -----------------------------------------

    // CHARTING
    aplus_date_range: ["30 Days", "7 Days"],
    aplus_site_reference: [
      "Anderson Point",
      "Christmas Creek",
      "Cloudbreak",
      "Eliwana",
      "Energy Operations",
      "Iron Bridge",
      "Rail",
      "Solomon",
    ],
    aplus_area_reference: [
      "AP Inloading",
      "AP Outloading",
      "CB OPF",
      "CC OPF2",
      "CC Stockyard",
      "Dry Plant Magnetite",
      "EW OPF1",
      "FT Infeed and PC",
      "FT OPF",
      "KV Infeed and PC",
      "KV OPF",
      "Rail Network",
      "SM Stockyard",
    ],
    aplus_circuit_reference: [
      "CB Hopper 10",
      "CB Hopper 9",
      "CB Infeed CV101",
      "CB OPF Line 1",
      "CB OPF Line 2",
      "CB OPF Line 3",
      "CB TLO",
      "CC OPF1 Module A",
      "CC OPF1 Module B",
      "CC OPF1",
      "CC OPF2 CH",
      "CC OPF2 Module A",
      "CC OPF2 Module B",
      "CC TLO",
      "CC WHIMS Mod 1",
      "CC WHIMS Mod 2",
      "CC WHIMS Mod 3",
      "DPM.Air Classification A",
      "DPM.Air Classification B",
      "DPM.Coarse Ore Stockpile",
      "DPM.Dry Magnetic Separation A",
      "DPM.Dry Magnetic Separation B",
      "DPM.Primary Crushing A",
      "DPM.Primary Crushing B",
      "DPM.Primary Grinding A",
      "DPM.Primary Grinding B",
      "DPM.Secondary Crushing A",
      "DPM.Secondary Crushing B",
      "DPM.Tertiary Crushing A",
      "DPM.Tertiary Crushing B",
      "EW OPF1 Mod 1",
      "EW OPF1 Mod 2",
      "EW RC802",
      "EW SK802",
      "EW TLO",
      "FT CH",
      "FT OPF Line 1",
      "FT OPF Line 2",
      "General",
      "Inload 1",
      "Inload 2",
      "Inload 3",
      "KV CH Line 1",
      "KV CH Line 2",
      "KV OPF Line 1",
      "KV OPF Line 2",
      "KV OPF Line 3",
      "Outload 1",
      "Outload 2",
      "Outload 3",
      "QV CH",
      "SM TLO",
    ],
    rems_site_reference: ["Christmas Creek", "Cloudbreak", "Rail Operations", "Solomon"],
    rems_fleet_type_reference: [
      "BUSSMT",
      "COACHS",
      "Dozer",
      "Drills",
      "Excavator",
      "FL01",
      "FL03",
      "FL04",
      "FL05",
      "FL06",
      "Grader",
      "Haul Truck",
      "Hire",
      "LVEHCL",
      "Support Vehicles",
      "TELELF",
      "TRUCKS",
      "Wheel Loader",
    ],

    time_usage: ["OD", "PL", "SD", "SM", "UM", "OTHER"],

    // -----------------------------------------

    // OTHER
    investigation_types: {
      1: "5-Why",
      2: "RCA",
      3: "Flash Report Only",
    },
    dashboard_types: {
      TABLEAU: 1,
      REMS: 2,
      APLUS: 3,
    },
    event_types: {
      APLUS: 1,
      REMS: 2,
    },
    completed_steps: {
      1: "Create Investigation",
      2: "Learn From Past Failures",
      3: "Create Flash Report",
      4: "Conduct Analysis",
      5: "Root Cause Details",
      6: "Shared Learnings",
    },
    // -----------------------------------------

    converter(items) {
      if (Array.isArray(items)) {
        return items;
      }
      if (!items) return [];

      return Object.entries(items).map(([k, v]) => ({
        value: parseInt(k),
        text: v,
      }));
    },
  });
};
