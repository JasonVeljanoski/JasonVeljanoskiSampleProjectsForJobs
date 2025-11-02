<template>
  <v-card v-bind="$bind.card">
    <v-card-title v-if="selected_location_id">
      {{ team_name }}
      <div class="tab-rack">
        <v-tabs v-model="tab_index" mandatory @change="changeTab">
          <v-tab v-for="(tab, ii) in tabs" :key="ii">
            {{ tab.title }}
          </v-tab>
        </v-tabs>
      </div>

      <v-spacer />

      <div class="d-flex justify-center">
        <e-icon-btn tooltip="Change Team" @click="$refs.user_teams_hierarchy.open()"> mdi-family-tree </e-icon-btn>
      </div>

      <teams-hierarchy ref="user_teams_hierarchy" :update_db="false" />
    </v-card-title>

    <v-card-text>
      <template v-if="!selected_location_id">
        <i>Please update your team through the user profile.</i>
      </template>
      <template v-else>
        <div v-for="(tab, ii) in processed_tabs" :key="ii">
          <div
            v-if="isTableau(tab.tab_type)"
            v-show="tab_index == ii"
            :id="`tableau_${tab.id}`"
            class="dashboard-container"
          />
          <rems-chart
            ref="rems_charts"
            v-else-if="isRems(tab.tab_type)"
            v-show="tab_index == ii"
            :dateRangeFilter="tab.rems_date_range"
            :regionSelectedFilter="tab.rems_site"
            :areaSelectedFilter="tab.rems_area"
            :preFilter="constructRemsFilter(tab)"
            hide_filters
          />
          <!-- hide_filters -->
          <aplus-chart
            ref="aplus_charts"
            v-else-if="isAplus(tab.tab_type)"
            v-show="tab_index == ii"
            :dateRangeFilter="tab.aplus_date_range"
            :regionSelectedFilter="tab.aplus_site"
            :areaSelectedFilter="tab.aplus_area"
            :circuitSelectedFilter="tab.aplus_circuits"
            :threshold_5_why="tab.threshold_5_why"
            hide_filters
          />
        </div>
      </template>
    </v-card-text>
  </v-card>
</template>

<script>
import * as tableau from "tableau-api-js";
import TeamsHierarchy from "@/components/Dashboards/TeamsHierarchy";
import AplusChart from "@/components/Dashboards/AplusChart";
import RemsChart from "@/components/Dashboards/RemsChart";

export default {
  components: {
    TeamsHierarchy,
    AplusChart,
    RemsChart,
  },
  head() {
    return {
      title: "Dashboards",
    };
  },
  data() {
    return {
      vizs: [],
      tabs: [],
      tab_index: null,
      dialog: false,
      loaded_tableaus: {},
      node: null,
    };
  },
  computed: {
    team_name() {
      return this.node?.text || this.$auth.user.team_name;
    },
    selected_location_id() {
      return this.$auth.user.location_id || this.node;
    },
    current_tab() {
      return this.tabs[this.tab_index];
    },
    processed_tabs() {
      let results = [];
      this.tabs.forEach((tab) => {
        let t = { ...tab };
        if (t.aplus_circuits.length > 0) {
          t.aplus_circuits = t.aplus_circuits.map((r) => r.aplus_circuit);
        }
        results.push(t);
      });
      return results;
    },
    dashboard_title() {
      return this.current_tab?.title;
    },
  },
  created() {
    this.$nuxt.$on("change_team", (node, update_db) => {
      if (update_db) window.location.reload();

      this.node = node;
      this.getTabData(node.id);
    });

    if (this.selected_location_id) this.getTabData(this.$auth.user.location_id);
  },
  methods: {
    constructRemsFilter(payload) {
      return {
        startDate: this.$format.initDate(payload.rems_date_start),
        endDate: this.$format.initDate(payload.rems_date_due),
        site: payload.rems_site,
        fleeType: payload.rems_fleet_type,
      };
    },
    changeTab() {
      if (this.isTableau(this.current_tab?.tab_type)) {
        this.$nextTick(this.initViz);
      } else if (this.isAplus(this.current_tab?.tab_type)) {
        this.$nextTick(() => {
          for (let x of this.$refs.aplus_charts) {
            x.setPreFilters();
          }
        });
      } else if (this.isRems(this.current_tab?.tab_type)) {
        for (let x of this.$refs.rems_charts) {
          x.getPoleChartData();
        }
      }
    },
    isTableau(type) {
      if (type) return this.$enums.dashboard_types["TABLEAU"] == type;
      return false;
    },
    isRems(type) {
      if (type) return this.$enums.dashboard_types["REMS"] == type;
      return false;
    },
    isAplus(type) {
      if (type) return this.$enums.dashboard_types["APLUS"] == type;
      return false;
    },
    getTabData(location_id) {
      // clear tableau vizs
      for (let viz of this.vizs) viz.dispose();
      this.vizs = [];

      this.$axios.$get("/dashboard", { params: { location_id: location_id } }).then((res) => {
        this.tabs = res;
        this.loaded_tableaus = {};
        this.dialog = false;
        this.tab_index = 0;
        this.changeTab();
      });
    },
    initViz() {
      const tab = this.current_tab;
      if (tab.tableau_url && !this.loaded_tableaus[tab.id]) {
        this.loaded_tableaus[tab.id] = true;

        const tableau_options = {
          hideTabs: true,
        };
        let el = document.getElementById(`tableau_${tab.id}`);

        let x = new tableau.Viz(el, tab.tableau_url, tableau_options);
        this.vizs.push(x);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.dashboard-container {
  display: flex;
  justify-content: center;
  width: 100%;
  margin: 10px;
  padding: 5px;
  border: solid 1px var(--v-accent-base);
}

.team_text {
  font-size: 10pt;
  text-align: center;
  font-weight: 600;
  cursor: pointer;
}

.tab-rack {
  max-width: 90%;
}
</style>
