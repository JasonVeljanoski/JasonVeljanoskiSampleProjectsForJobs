<template>
  <div>
    <div class="root">
      <v-card class="main-card" outlined>
        <v-card-text>
          <div class="d-flex">
            <v-spacer />
            <e-icon-btn
              v-if="!side_panel"
              tooltip="Show Filters"
              @click="setFilter"
            >
              mdi-filter-plus-outline
            </e-icon-btn>
          </div>
          <base-aplus-stacked-chart
            :key="keyNum"
            :chartItems="chartItems"
            :threshold_5_why="threshold_5_why"
            chartTitle="Top Downtime Events By Equipment Cause"
            :height="550"
            :width="130"
            @clicked="handleClicked($event)"
          />
        </v-card-text>
      </v-card>
      <v-card v-if="side_panel" outlined class="side-card" height="100%">
        <div class="d-flex side-card-header" style="height: 47px">
          <h3>Filters</h3>
          <e-icon-btn
            @click="
              () => {
                side_panel = false;
                keyNum++;
              }
            "
            class="ml-auto mr-3"
            tooltip="Hide Filters"
          >
            mdi-close
          </e-icon-btn>
        </div>
        <v-divider />
        <v-card-text class="mb-3">
          <h4>Date Range</h4>
          <v-autocomplete
            v-model="dateRange"
            v-bind="$bind.select"
            :items="$enums.aplus_date_range"
            hide-details="auto"
            @change="changeFilter()"
          />

          <h4>Site</h4>
          <v-autocomplete
            v-model="filter.regionSelected"
            v-bind="$bind.select"
            :items="$enums.aplus_site_reference"
            item-text="name"
            item-value="name"
            clearable
            multiple
            @change="changeFilter(true)"
          />
          <h4>Area Name</h4>
          <v-autocomplete
            v-model="filter.areaSelected"
            v-bind="$bind.select"
            :items="$enums.aplus_area_reference"
            item-text="name"
            item-value="name"
            clearable
            multiple
            @change="changeFilter(true)"
          />
          <h4>Circuit</h4>
          <v-autocomplete
            v-model="filter.circuitSelected"
            v-bind="$bind.select"
            :items="circuitItems"
            item-text="name"
            item-value="name"
            clearable
            multiple
            @change="changeFilter(true)"
          />
          <h4>Time Usage</h4>
          <v-autocomplete
            v-model="filter.timeUsageSelected"
            v-bind="$bind.select"
            :items="$enums.converter(timeUsageItems)"
            item-text="name"
            item-value="name"
            clearable
            multiple
            @change="changeFilter(true)"
          />
        </v-card-text>
        <v-divider class="mt-15" />
        <v-card-actions>
          <v-btn outlined color="warning" @click="resetFilter()"> Clear </v-btn>
        </v-card-actions>
      </v-card>
    </div>
    <div class="d-flex mt-2" outlined>
      <v-card class="mr-1" width="50%" outlined>
        <e-data-table
          :height="350"
          fixed-header
          :headers="headers"
          :items="items"
          :items-per-page="-1"
          hide-default-footer
        >
          <template v-slot:item.prepend="{ item, index }">
            <e-icon-btn
              v-if="item.investigation_id != null"
              :to="navigateInvestigationForm(item)"
              tooltip="Go to Investigation"
            >
              mdi-pencil
            </e-icon-btn>
            <v-checkbox v-else v-model="selectedBoxed[index]" class="ml-auto" />
          </template>
          <template v-slot:item.ids="{ item }">
            <span v-if="item['ids'].length == 1">{{ item["ids"][0] }}</span>
            <v-tooltip v-else bottom>
              <template v-slot:activator="{ on, attrs }">
                <span v-bind="attrs" v-on="on">
                  {{ item["ids"][0] + "..." }}
                </span>
              </template>
              <span>
                <span v-for="(id, index) in item['ids']"
                  >{{ id }} {{ index == item["ids"].length - 1 ? " " : ", " }}
                </span>
              </span>
            </v-tooltip>
          </template>
          <template v-slot:header.prepend="{ item }">
            <v-checkbox
              v-if="!allEventInvestCreated"
              v-model="selectAll"
              class="ml-auto"
            />
          </template>

          <template v-slot:footer="{ item }">
            <v-divider />
            <v-dialog v-model="actions_dialog" width="500">
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  v-bind="{ ...$bind.btn, attrs }"
                  :disabled="aplus_ids.length == 0 || allEventInvestCreated"
                  class="my-2 mx-2"
                  style="max-width: 320px"
                  v-on="on"
                >
                  <v-icon left>mdi-plus</v-icon>
                  Create or Add to Investigation
                </v-btn>
              </template>
              <v-card>
                <v-card-title>Event Options</v-card-title>

                <v-divider />

                <v-tabs v-model="action_dialog_tab" class="mb-4">
                  <v-tab>New Investigation</v-tab>
                  <v-tab>Existing Investigation</v-tab>
                </v-tabs>

                <v-card-text v-if="action_dialog_tab == 0">
                  Do you want to create a new investigation with the selected
                  events?
                </v-card-text>
                <v-card-text v-if="action_dialog_tab == 1">
                  Choose an existing investigation to add the selected events
                  to.

                  <v-autocomplete
                    v-model="investigation_selected"
                    :items="investigation_titles"
                    v-bind="$bind.select"
                    autofocus
                    item-text="title"
                    placeholder="Start typing the investigation title..."
                    return-object
                  />
                </v-card-text>

                <v-divider />

                <v-card-actions>
                  <v-btn
                    color="warning"
                    outlined
                    @click="actions_dialog = false"
                  >
                    <v-icon left>mdi-close</v-icon> Cancel
                  </v-btn>
                  <v-spacer />
                  <v-btn
                    v-if="action_dialog_tab == 0"
                    v-bind="$bind.btn"
                    @click="navigateInvestigationForm()"
                  >
                    Create New
                  </v-btn>
                  <v-btn
                    v-if="action_dialog_tab == 1"
                    v-bind="$bind.btn"
                    @click="addExistingInvestigation()"
                  >
                    Add To Existing
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </template>
        </e-data-table>
      </v-card>
      <v-card class="ml-1" width="50%" outlined>
        <v-card-text>
          <base-aplus-chart
            :key="keyNum"
            :chartTitle="subChartTitle"
            :chartItems="subChartItems"
            :height="350"
            @clicked="subChartClick($event)"
          />
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script>
import BaseAplusStackedChart from "@/components/Dashboards/BaseAplusStackedChart";
import BaseAplusChart from "@/components/Dashboards/BaseAplusChart";

export default {
  components: {
    BaseAplusStackedChart,
    BaseAplusChart,
  },
  props: {
    dateRangeFilter: { type: String, require: false },
    regionSelectedFilter: { type: String, require: false },
    areaSelectedFilter: { type: String, require: false },
    hide_filters: { type: Boolean, required: false, default: false },
    threshold_5_why: { type: Number, require: false, default: 2 },
    circuitSelectedFilter: { type: Array, require: false, default: () => [] },
  },
  data() {
    return {
      investigation_selected: null,
      investigation_titles: [],
      action_dialog_tab: 0,
      actions_dialog: false,

      // ---

      problemItems: [],
      actionItems: [],
      currentStack: { datasetIndex: null, index: null },
      filter: {
        startDate: new Date(new Date().setDate(new Date().getDate() - 30)),
        exactDate: null,
        problemSelected: [],
        actionSelected: [],
        regionSelected: this.$enums.aplus_site_reference.filter(
          (x) => x != "Iron Bridge"
        ),
        areaSelected: [],
        circuitSelected: [],
        timeUsageSelected: ["OD", "UM"], // REQUIREMENT: by default OD and UM are selected (Campbells Request)
      },
      selectAll: false,
      dateRange: "30 Days",
      circuitItems: [],
      timeUsageItems: [],
      selectedBoxed: [],
      currentName: null,
      currentCause: null,
      chartItems: [],
      allItems: [],
      subChartItems: [],
      subChartTitle: "Trend",
      pageNumber: [],
      currentPage: 1,
      clickedIndex: null,
      side_panel: true,
      keyNum: 0,
      headers: [
        {
          text: "",
          value: "prepend",
          sortable: false,
          divider: true,
          width: "10",
        },
        { text: "IDs", value: "ids", divider: true, width: "110" },
        { text: "Date", value: "date", divider: true, width: "110" },
        { text: "Problem", value: "problem", divider: true, width: "210" },
        { text: "Action", value: "action", divider: true, width: "210" },
        { text: "Circuit", value: "circuit", divider: true, width: "110" },
        {
          text: "Time Usage",
          value: "time_usage",
          divider: true,
          width: "110",
        },
        {
          text: "Effective Duration (hrs)",
          value: "effective_dt",
          divider: true,
          width: "110",
        },
        {
          text: "Number of Records",
          value: "count",
          divider: true,
          width: "110",
        },
      ],
      items: [],
    };
  },
  computed: {
    aplus_ids() {
      return this.selectedBoxed.reduce((acc, value, index) => {
        if (value && this.items[index]?.investigation_id == null)
          acc.push(this.items[index]);
        return acc;
      }, []);
    },
    allEventInvestCreated() {
      if (
        this.items.length > 0 &&
        this.items.every((item) => item.investigation_id !== null)
      )
        return true;
      return false;
    },
  },
  mounted() {
    this.getPoleChartData();
    this.getInvestigationTitles();

    this.$nextTick(() => {
      this.setPreFilters();
    });
  },
  watch: {
    currentPage() {
      this.changePage();
    },
    // this one is to achieve the select all and undo all function
    selectAll() {
      if (this.selectedBoxed.length > 0) {
        if (this.selectAll)
          this.selectedBoxed = this.selectedBoxed.map((res) => (res = true));
        else
          this.selectedBoxed = this.selectedBoxed.map((res) => (res = false));
      }
    },
  },
  methods: {
    async subChartClick(event) {
      if (event != null) {
        let date = new Date(
          new Date().setDate(new Date().getDate() - 29 + event.index)
        );
        if (this.dateRange == "7 Days") {
          date = new Date();
          date.setDate(date.getDate() - (7 - event.index) + 1);
        }

        this.filter.exactDate = date;
        const tableURL = `/snowflake/get_equipment`;
        await this.$axios
          .$post(tableURL, null, {
            params: {
              name: this.currentName,
              cause: this.currentCause,
              period: event.period,
              filters: this.makeFilterInArray(this.cleanDict(this.filter)),
            },
          })
          .then((res) => {
            this.items = [];
            this.selectAll = false;
            this.selectedBoxed = [];
            res.forEach((r, i) => {
              let item = {};
              item.date =
                r.date.slice(8, 10) +
                "/" +
                r.date.slice(5, 7) +
                "/" +
                r.date.slice(0, 4);
              item.id = r.id;
              item.ids = r.ids;
              item.investigation_id = r.investigation_id;
              item.problem = r.problem;
              item.action = r.action;
              item.time_usage = r.time_usage_code;
              item.circuit = r.circuit;
              item.effective_dt = r.sum_duration
                ? r.sum_duration.toFixed(1)
                : r.sum_duration;
              item.actionwithin_a_week = r.within_a_week;
              item.count = r.equipment_count;
              this.items.push(item);
              this.selectedBoxed.push(true);
            });
            this.selectAll = true;
          });
      }
    },
    setPreFilters() {
      if (this.dateRangeFilter) this.dateRange = [this.dateRangeFilter];

      if (this.regionSelectedFilter)
        this.filter.regionSelected = [this.regionSelectedFilter];

      if (this.areaSelectedFilter)
        this.filter.areaSelected = [this.areaSelectedFilter];

      if (this.circuitSelectedFilter.length > 0)
        this.filter.circuitSelected = this.circuitSelectedFilter;

      this.changeFilter();
    },
    setFilter() {
      this.side_panel = !this.side_panel;
    },
    resetFilter() {
      this.filter = {
        startDate: new Date(new Date().setDate(new Date().getDate() - 30)),
        problemSelected: [],
        actionSelected: [],
        regionSelected: [],
        areaSelected: [],
        circuitSelected: [],
        timeUsageSelected: [],
      };
      this.dateRange = "30 Days";

      this.changeFilter();
    },
    cleanDict(val) {
      let hasValue = (v) => {
        if (!v) {
          if (v == "") return false;
          if (v == 0) return true;
          return false;
        }

        if (Array.isArray(v) && v.length == 0) return false;
        if (Array.isArray(v) && v[0] == null) return false;
        return true;
      };

      if (!val) return val;

      return Object.entries(val).reduce(
        (a, [k, v]) => (hasValue(v) ? ((a[k] = v), a) : a),
        {}
      );
    },
    checkItem(item, isProblem = true) {
      if (!isProblem) return this.filter.actionSelected.includes(item);
      return this.filter.problemSelected.includes(item);
    },
    makeFilterInArray(filters) {
      Object.keys(filters).forEach((f) => {
        if (typeof filters[f] !== "object" && f !== "startDate") {
          filters[f] = [filters[f]];
        }
      });
      return filters;
    },
    async changeFilter(isSite = null) {
      if (isSite != null && this.filter.regionSelected != null) {
        const areaURL = `/snowflake/get_equipment_date`;
        let filter = this.cleanDict(this.filter);
        filter = this.makeFilterInArray(filter);
        await this.$axios.$get(areaURL, { params: { filter } }).then((res) => {
          // the if statement is to make sure it will not change the items able to selected when that filter has things inside
          if (this.filter.areaSelected.length == 0)
            this.areaNameItems = res.map((r) => r.area_name);
          if (this.filter.circuitSelected.length == 0)
            this.circuitItems = res.map((r) => r.circuit);
          if (this.filter.timeUsageSelected.length == 0)
            this.timeUsageItems = res.map((r) => r.time_usage_code);
        });
      }
      if (this.filter.regionSelected == null) this.getFilterOptions();

      const url = `/snowflake/get_chart`;

      this.filter.startDate = new Date(
        new Date().setDate(new Date().getDate() - 30)
      );
      if (this.dateRange == "7 Days")
        this.filter.startDate = new Date(
          new Date().setDate(new Date().getDate() - 7)
        );

      let filters = this.cleanDict(this.filter);
      filters = this.makeFilterInArray(filters);
      this.chartItems.forEach((r) => (r.clicked = null));
      this.items = [];
      this.subChartItems = [];
      this.subChartTitle = "Trend";
      await this.$axios.$get(url, { params: { filters } }).then((res) => {
        this.selectAll = false;
        this.pageNumber = [];
        this.currentPage = 1;
        this.allItems = res;
        if (res.length > 10) {
          this.chartItems = res.slice(0, 10);
          const pages = Math.floor(res.length / 10);
          for (let i = 1; i < pages + 1; i++) {
            this.pageNumber.push(i);
          }
          if (res.length / 10 > pages) this.pageNumber.push(pages + 1);
        } else {
          this.pageNumber = [1];
          this.chartItems = res;
        }
        this.keyNum += 1;
      });
    },
    changePage(direction = null) {
      if (direction == "left") this.currentPage -= 1;
      else if (direction == "right") this.currentPage += 1;
      if (this.clickedIndex != null)
        this.chartItems[this.clickedIndex].clicked = null;
      this.items = [];
      this.subChartItems = [];
      this.subChartTitle = "Trend";
      const end = this.currentPage * 10;
      const start = end - 10;
      this.chartItems = this.allItems.slice(start, end);
      this.keyNum += 1;
    },
    async handleClicked(name) {
      this.currentName = null;
      this.currentCause = null;
      if (name !== null) {
        this.filter.exactDate = null;
        const index = name.index;
        this.clickedIndex = index;

        let period = name.period;
        const currentStack = name.currentStack;
        name = name.data;

        this.currentName = name[0];
        this.currentCause = name[1];
        const tableURL = `/snowflake/get_equipment`;
        const chartURL = `/snowflake/get_equipment_date`;

        let params = {
          name: name[0],
          cause: name[1],
          period: period,
          filters: this.makeFilterInArray(this.cleanDict(this.filter)),
        };
        await this.$axios
          .$post(tableURL, null, {
            params: params,
          })
          .then((res) => {
            // empty the selected boxes and table items before add in data
            this.items = [];
            this.selectAll = false;
            this.selectedBoxed = [];
            // add the index to the item to enable the table checkbox multiple selection
            let index = 0;
            res.forEach((r, i) => {
              let item = {};
              item.date =
                r.date.slice(8, 10) +
                "/" +
                r.date.slice(5, 7) +
                "/" +
                r.date.slice(0, 4);
              item.id = r.id;
              item.index = index;
              item.investigation_id = r.investigation_id;
              item.problem = r.problem;
              item.action = r.action;
              item.ids = r.ids;
              item.time_usage = r.time_usage_code;
              item.circuit = r.circuit;
              item.effective_dt = r.sum_duration
                ? r.sum_duration.toFixed(1)
                : r.sum_duration;
              item.actionwithin_a_week = r.within_a_week;
              item.count = r.equipment_count;
              this.items.push(item);
              this.selectedBoxed.push(true);
              index++;
            });
            this.selectAll = true;
          });
        await this.$axios
          .$post(chartURL, null, {
            params: {
              name: name[0],
              cause: name[1],
              period: period,
              filters: this.makeFilterInArray(this.cleanDict(this.filter)),
            },
          })
          .then((res) => {
            this.subChartItems = [];
            this.subChartTitle = name[0] + " " + name[1];
            let days = 30;
            if (this.dateRange == "7 Days") days = 7;
            let today = new Date();
            for (let i = 0; i < days; i++) {
              let date = new Date(new Date().setDate(new Date().getDate() - i))
                .toISOString()
                .split("T")[0];
              let payload = {
                date: date,
                count: 0,
                sum: 0,
                yLabel: name[0] + " " + name[1],
              };
              res.forEach((r) => {
                if (r.date == date) {
                  payload = {
                    date: r.date,
                    count: r.equipment_count,
                    sum: r.sum_duration,
                    within_a_week: r.within_a_week,
                    yLabel: name[0] + " " + name[1],
                  };
                }
              });
              this.subChartItems.push(payload);
            }
            this.subChartItems.reverse();
          });
        // if the bar is clicked, then empty the sub chart and table
        if (this.chartItems[index].clicked != true) {
          this.chartItems.forEach((c) => (c.clicked = null));
          this.chartItems[index].clicked = currentStack;
        } else if (this.currentName == null) {
          this.chartItems[index].clicked = null;
          this.items = [];
          this.subChartItems = [];
          this.subChartTitle = "Trend";
        }
      } else {
        this.selectAll = false;
        this.chartItems.forEach((r) => (r.clicked = null));
        this.items = [];
        this.subChartItems = [];
        this.subChartTitle = "Trend";
        //
      }
      this.keyNum += 1;
    },
    async getFilterOptions() {
      const filterURL = `/snowflake/get_filter_options`;
      await this.$axios.$get(filterURL).then((res) => {
        this.problemItems = res.problems.map((r) => r.name);
        this.actionItems = res.actions.map((r) => r.name);
        // this.regionNameItems = res.region_names;
        // this.areaNameItems = res.area_names;
        this.circuitItems = res.circuits;
        this.timeUsageItems = res.time_usage_codes;
      });
    },
    getPoleChartData() {
      this.changeFilter();
      this.getFilterOptions();
    },
    // ---------------------
    // INVESTIGATION HELPERS
    // ---------------------
    getInvestigationTitles() {
      this.$axios
        .$get("/investigation/titles")
        .then((res) => {
          this.investigation_titles = res;
        })
        .catch((err) => console.error(err));
    },
    navigateInvestigationForm(item = null) {
      if (item == null && this.selectedBoxed.length >= 1) {
        this.$router.push({
          path: "/investigation",
          query: { items: this.aplus_ids, type: "APLUS" },
        });
      } else if (item.investigation_id != null) {
        return `/investigation?id=${item.investigation_id}`;
      }
    },
    addExistingInvestigation() {
      if (
        this.investigation_selected &&
        confirm(
          `Are you sure you want to add the selected events to ${this.investigation_selected.title}?`
        )
      ) {
        this.$router.push({
          path: `/investigation?id=${this.investigation_selected.id}`,
          query: {
            items: this.aplus_ids,
            type: "APLUS",
            id: this.investigation_selected.id,
          },
        });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
// ::v-deep .v-list-item {
//   padding: 0;
// }
.root {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100%;
  overflow: hidden;
  gap: 16px;
}
.main-card {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  width: 100%;
  overflow: hidden;
}

.side-card {
  width: 40ch;
  overflow: auto;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;

  .side-card-header {
    flex-shrink: 0;
    display: flex;
    text-transform: capitalize;
    align-items: center;
    margin-left: 16px;
  }
}

.side-card-toggler {
  position: absolute;
  z-index: 3;

  top: 19px;
  right: 0px;

  .wrapper {
    padding-left: 20px;
    width: 100px;
    background: conic-gradient(
      rgba(65, 143, 222, 0.7) 0deg,
      rgba(65, 143, 222, 0.7) 90deg,
      rgba(255, 193, 5, 0.7) 90deg,
      rgba(255, 193, 5, 0.7) 270deg,
      rgba(65, 143, 222, 0.7) 270deg,
      rgba(65, 143, 222, 0.7) 360deg
    );

    border-top-left-radius: 999px;
    border-bottom-left-radius: 999px;

    position: absolute;
    right: -80px;

    transition: 0.3s;

    &:hover {
      right: 0;
    }
  }

  .extra {
    width: 200px;
    height: 100%;

    position: absolute;
    left: calc(50% - 2px);
  }
}
</style>
