<template>
  <div>
    <div class="root">
      <v-card
        class="main-card d-flex"
        width="66%"
        :height="windowHeiht * 0.29"
        outlined
      >
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
        <div class="d-flex">
          <h3 class="mt-auto mb-auto mr-0 pr-1 vertical-header">FLOC6</h3>

          <v-card-text class="pa-0 ma-0">
            <base-rems-chart
              class="max-width pr-2 ma-0"
              :key="keyFloc6"
              :chartItems="chartItems.floc6"
              @clicked="handleClicked($event)"
              :height="windowHeiht * 0.27"
            />
          </v-card-text>
        </div>
      </v-card>
      <v-card
        v-if="side_panel && !hide_filters"
        outlined
        class="side-card pa-0 ma-0 d-flex flex-column"
        width="34%"
        :height="windowHeiht * 0.29"
      >
        <div class="filter-title">
          <div class="title">
            <h4>Filters</h4>
            <e-icon-btn
              @click="resetFilter()"
              class="ml-auto mr-1"
              tooltip="Reset Filter"
            >
              mdi-replay
            </e-icon-btn>
            <e-icon-btn
              @click="side_panel = false"
              class="mr-3"
              tooltip="Hide Filters"
            >
              mdi-close
            </e-icon-btn>
          </div>
          <v-divider class="mt-1" />
        </div>
        <div class="mt-1 filter-content">
          <v-card-text class="pt-1 pb-0">
            <div class="d-flex justify-center">
              <div class="full-width">
                <h4>Date Range</h4>
                <!-- <e-date-time
                  v-model="filter.startDate"
                  v-bind="$bind.select"
                  :time="false"
                  class="mr-2"
                  hide-details="auto"
                  @change="getPoleChartData(true)"
                /> -->
                <v-select
                  class="mr-1"
                  dense
                  outlined
                  v-model="dateBack"
                  hide-details="auto"
                  :items="dateItem"
                  @change="getPoleChartData(true)"
                />
              </div>
              <div class="ml-1 full-width">
                <h4>Site</h4>
                <v-autocomplete
                  v-bind="$bind.select"
                  :items="siteItems"
                  item-text="name"
                  item-value="name"
                  hide-details="auto"
                  clearable
                  @change="getPoleChartData(true)"
                  v-model="filter.site[0]"
                />
              </div>
            </div>
            <div class="d-flex justify-center">
              <div class="mr-1 full-width">
                <h4>Fleet Type</h4>
                <v-autocomplete
                  v-model="filter.fleeType[0]"
                  v-bind="$bind.select"
                  item-text="name"
                  item-value="name"
                  :items="fleeTypeItems"
                  hide-details="auto"
                  clearable
                  @change="getPoleChartData(true)"
                />
              </div>
              <div class="ml-1 full-width">
                <h4>Model</h4>
                <v-autocomplete
                  v-model="filter.model"
                  v-bind="$bind.select"
                  :items="modelItems"
                  item-text="name"
                  item-value="name"
                  hide-details="auto"
                  clearable
                  @change="getPoleChartData(true)"
                />
              </div>
            </div>
            <div class="d-flex justify-center">
              <div class="mr-1 full-width">
                <h4>FLOC 6</h4>
                <v-autocomplete
                  v-model="filter.floc6"
                  v-bind="$bind.select"
                  :items="floc6Items"
                  item-text="name"
                  item-value="name"
                  hide-details="auto"
                  clearable
                  @change="getPoleChartData(true)"
                />
              </div>
              <div class="ml-1 full-width">
                <h4>FLOC 7</h4>
                <v-autocomplete
                  v-model="filter.floc7"
                  v-bind="$bind.select"
                  :items="floc7Items"
                  item-text="name"
                  item-value="name"
                  hide-details="auto"
                  clearable
                  @change="getPoleChartData(true)"
                />
              </div>
            </div>
            <div class="d-flex justify-center">
              <div class="mr-1 full-width">
                <h4>FLOC 8</h4>
                <v-autocomplete
                  v-model="filter.floc8"
                  v-bind="$bind.select"
                  :items="floc8IFiltertems"
                  item-text="name"
                  item-value="name"
                  hide-details="auto"
                  clearable
                  @change="getPoleChartData(true)"
                />
              </div>
              <div class="full-width d-flex justify-center">
                <!-- <h4>FLOC 8</h4>
                <v-autocomplete
                  v-model="filter.floc8"
                  v-bind="$bind.select"
                  :items="floc8IFiltertems"
                  item-text="name"
                  item-value="name"
                  hide-details="auto"
                  clearable
                  @change="getPoleChartData(true)"
                /> -->
              </div>
            </div>
          </v-card-text>
        </div>
        <!-- <v-divider class="mt-15" /> -->
        <!-- <v-card-actions>
          <v-btn @click="resetFilter()" class="mt-1 mb-2 ml-2" color="warning">
            Reset
          </v-btn>
        </v-card-actions> -->
      </v-card>
    </div>

    <div
      class="root mt-2"
      style="gap: 8px; height: 60vh; position: relative"
      outlined
    >
      <div style="width: 66%">
        <v-card width="100%" :height="windowHeiht * 0.29" outlined>
          <div class="d-flex max-width">
            <h3 class="mt-auto mb-auto mr-0 pr-0 vertical-header">FLOC7</h3>
            <v-card-text style="gap: 8px" class="d-flex pa-0 ma-0">
              <base-rems-chart
                class="one-third"
                :key="keyNum + 4"
                :chartItems="chartItems.floc7_1"
                :maxFloc7="maxFloc7"
                :maxCount="maxCount"
                :subChartTitle="chartItems.floc6"
                :height="windowHeiht * 0.27"
                :colorIndex="0"
                @clicked="handleClicked($event)"
              />

              <base-rems-chart
                class="one-third"
                :key="keyNum + 8"
                :chartItems="chartItems.floc7_2"
                :maxFloc7="maxFloc7"
                :maxCount="maxCount"
                :subChartTitle="chartItems.floc6"
                :height="windowHeiht * 0.27"
                :colorIndex="1"
                @clicked="handleClicked($event)"
              />

              <base-rems-chart
                class="one-third pr-2"
                :key="keyNum + 6"
                :chartItems="chartItems.floc7_3"
                :maxFloc7="maxFloc7"
                :maxCount="maxCount"
                :subChartTitle="chartItems.floc6"
                :height="windowHeiht * 0.27"
                :colorIndex="2"
                @clicked="handleClicked($event)"
              />
            </v-card-text>
          </div>
        </v-card>
        <v-card
          class="mt-2"
          :height="windowHeiht * 0.3"
          style="gap: 8px"
          outlined
        >
          <div class="d-flex" style="width: 100%">
            <h3 class="mt-auto mb-auto mr-0 pr-0 vertical-header">
              {{ floc8Name }}
            </h3>
            <v-card-text class="pa-0 ma-0">
              <base-rems-chart
                class="pr-2"
                :key="floc8Key"
                :subChartTitle="
                  floc8Items[0] && floc8Items[0].name == 'floc7'
                    ? [floc8Name]
                    : null
                "
                :chartItems="floc8Items"
                :height="windowHeiht * 0.27"
                @clicked="handleClicked($event)"
              />
            </v-card-text>
          </div>
        </v-card>
      </div>

      <v-card width="34%" outlined>
        <e-data-table
          fixed-header
          :headers="headers"
          :items="items"
          :hide-default-footer="true"
          :footer-props="{ 'items-per-page-options': [-1] }"
        >
          <template v-slot:item.prepend="{ item }">
            <e-icon-btn
              :to="`/investigation?id=${item.id}&type=REMS`"
              tooltip="Create Investigation"
            >
              mdi-pencil
            </e-icon-btn>
          </template>
        </e-data-table>
      </v-card>
    </div>
  </div>
</template>

<script>
import BaseRemsChart from "@/components/Dashboards/BaseRemsChart";

export default {
  components: {
    BaseRemsChart,
  },
  props: {
    preFilter: { type: Object, require: false },
    hide_filters: { type: Boolean, required: false, default: false },
  },
  data() {
    return {
      filter: {
        startDate: new Date(new Date().setDate(new Date().getDate() - 30)),
        endDate: new Date(),
        site: [null],
        fleeType: [null],
        model: [],
        floc6: null,
        floc7: null,
        floc8: null,
      },
      theme: null,
      siteItems: [],
      fleeTypeItems: [],
      modelItems: [],
      floc6Items: [],
      floc7Items: [],
      floc8IFiltertems: [],
      chartItems: [],
      floc8Items: [],
      colorIndex: null,
      side_panel: true,
      floc8Name: "FLOC8",
      keyNum: 1,
      maxFloc7: null,
      maxCount: null,
      floc8Key: 1,
      keyFloc6: 1,
      windowHeiht: window.innerHeight,
      dateItem: ["Last 30 Days", "Last 7 Days"],
      dateBack: "Last 30 Days",
      headers: [
        { text: "", value: "prepend", width: 20 },
        { text: "FLOC8", value: "floc8", width: "90px" },
        { text: "Machine Name", value: "equipment_name" },
        { text: "Event Start", value: "event_datetime" },
        { text: "Last Comment", value: "last_comment" },
        { text: "Event Duration (hrs)", value: "event_duration" },
      ],
      items: [],
    };
  },
  mounted() {
    this.setPreFilters();
  },
  methods: {
    countMax(number, pace) {
      let max = 0;

      while (max < number) {
        max += pace;
      }
      return max;
    },
    setFilter() {
      this.side_panel = !this.side_panel;
    },
    setPreFilters() {
      this.filter.startDate = this.preFilter?.startDate;
      this.filter.endDate = this.preFilter?.endDate;
      this.filter.site[0] = this.preFilter?.site;
      this.filter.fleeType[0] = this.preFilter?.fleeType;
      this.getPoleChartData();
    },
    resetFilter() {
      this.filter = {
        startDate: new Date(new Date().setDate(new Date().getDate() - 30)),
        endDate: new Date(),
        site: [null],
        fleeType: [null],
        model: [],
        floc6: null,
        floc7: null,
        floc8: null,
      };
      this.dateBack = "Last 30 Days";
      this.floc8Items = [];
      this.floc8Key++;
      this.getPoleChartData();
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

    async handleClicked(name) {
      const filters = this.cleanDict(this.filter);
      this.chartItems.floc6.forEach((r) => (r.clicked = null));
      this.chartItems.floc7_1.forEach((r) => (r.clicked = null));
      this.chartItems.floc7_2.forEach((r) => (r.clicked = null));
      this.chartItems.floc7_3.forEach((r) => (r.clicked = null));
      this.floc8Items.forEach((r) => (r.clicked = null));
      let url = `/snowflake/get_floc8_table?floc6=${name.floc6}&floc7=${name.floc7}&floc8=${name.floc8}`;
      if (name.name == "floc6") {
        this.chartItems.floc6[name.clickedIndex].clicked = true;
        url = `/snowflake/get_floc8_table?floc6=${
          name.floc6
        }&floc6_table=${true}`;
        const chartURL = `/snowflake/get_floc7_top10?floc6=${
          name.floc6
        }&floc6_table=${true}`;
        await this.$axios
          .$get(chartURL, { params: { filters } })
          .then((res) => {
            res.forEach((r) => (r.colorIndex = name.clickedIndex));
            this.floc8Items = res;
            this.floc8Name = name.floc6;
          });
      }
      if (name.name == "floc7") {
        if (name.floc6 == null) name.floc6 = "";
        url = `/snowflake/get_floc8_table?floc6=${name.floc6}&floc7=${name.floc7}`;
        if (!name.other) {
          const chartURL = `/snowflake/get_floc8?floc7=${name.floc7}&floc6=${name.floc6}`;
          await this.$axios
            .$get(chartURL, { params: { filters } })
            .then((res) => {
              const floc_name = "floc7_" + (name.index + 1).toString();
              this.chartItems[floc_name][name.clickedIndex].clicked = true;
              this.floc8Items = [];
              this.items = [];
              this.floc8Name = "FLOC8";
              this.floc8Items = res;
              this.floc8Items.colorIndex = name.index;
              this.keyNum += 1;
              this.floc8Key += 1;
            });
        } else {
          this.floc8Items[name.clickedIndex].clicked = true;
        }
      }
      await this.$axios.$get(url, { params: { filters } }).then((res) => {
        if (name.name == "floc6" && this.headers[1].text !== "FLOC7")
          this.headers = [
            { text: "", value: "prepend", width: 20 },
            { text: "FLOC7", value: "floc7" },
            ...this.headers.slice(1, this.headers.length),
          ];
        else if (name.name !== "floc6" && this.headers[1].text == "FLOC7")
          this.headers = [
            { text: "", value: "prepend", width: 20 },
            ...this.headers.slice(2, this.headers.length),
          ];
        res = res.map((r) => {
          if (name.name == "floc6" && r.floc7 == null) r.floc7 = "NO FLOC7";
          if (r.floc8 == null) r.floc8 = "NO FLOC8";
          let formatted = { ...r };
          const new_datetime = new Date(formatted.event_datetime + "Z");

          formatted.event_datetime =
            (new_datetime.getUTCDate() < 10 ? "0" : "") +
            new_datetime.getUTCDate() +
            "/" +
            (new_datetime.getUTCMonth() + 1 < 10 ? "0" : "") +
            (new_datetime.getUTCMonth() + 1) +
            "/" +
            new_datetime.getUTCFullYear() +
            " " +
            (new_datetime.getUTCHours() < 10 ? "0" : "") +
            new_datetime.getUTCHours() +
            ":" +
            (new_datetime.getMinutes() < 10 ? "0" : "") +
            new_datetime.getUTCMinutes();
          if (formatted.event_duration !== null)
            formatted.event_duration = formatted.event_duration.toFixed(1);
          return formatted;
        });
        this.items = res.slice(0, 100);
        if (name.name == "floc8")
          this.floc8Items[name.clickedIndex].clicked = true;
        this.keyFloc6++;
        this.keyNum += 1;
        this.floc8Key += 1;
      });
    },
    async getFilterOptions() {
      const filterURL = `/snowflake/get_filter_rems_options`;
      const filters = this.cleanDict(this.filter);

      await this.$axios.$get(filterURL, { params: { filters } }).then((res) => {
        if (this.filter.site[0] == null) this.siteItems = res.sites;
        if (this.filter.fleeType[0] == null)
          this.fleeTypeItems = res.flee_types;
        if (this.filter.model == null) this.modelItems = res.models;
        if (this.filter.floc6 == null) this.floc6Items = res.floc6s;
        if (this.filter.floc7 == null) this.floc7Items = res.floc7s;
        if (this.filter.floc8 == null) this.floc8IFiltertems = res.floc8s;
      });
    },
    async getPoleChartData(filter = false) {
      if (filter) this.floc8Items = [];

      const url = `/snowflake/get_floc67`;
      if (this.dateBack == "Last 7 Days")
        this.filter.startDate = new Date(
          new Date().setDate(new Date().getDate() - 7)
        );
      else
        this.filter.startDate = new Date(
          new Date().setDate(new Date().getDate() - 30)
        );
      const filters = this.cleanDict(this.filter);
      this.floc8Items = [];
      this.items = [];

      await this.$axios.$get(url, { params: { filters } }).then((res) => {
        this.chartItems = res;
        let allY = [];
        let allCount = [];
        this.chartItems.floc7_1.forEach((i) => {
          allY.push(i.duration);
          allCount.push(i.count);
        });
        this.chartItems.floc7_2.forEach((i) => {
          allY.push(i.duration);
          allCount.push(i.count);
        });
        this.chartItems.floc7_3.forEach((i) => {
          allY.push(i.duration);
          allCount.push(i.count);
        });
        // the following code is to set up the y axis of floc7
        this.maxFloc7 = Math.round(Math.max(...allY) / 100) * 100;
        if (this.maxFloc7 < Math.max(...allY)) this.maxFloc7 += 100;
        this.maxCount = Math.round(Math.max(...allCount) / 20) * 20;
        if (this.maxCount < Math.max(...allCount)) this.maxCount += 20;
        if (this.preFilter != null) {
          this.maxFloc7 = this.countMax(Math.max(...allY), 10);
          this.maxCount = this.countMax(Math.max(...allCount), 4);
        }
      });
      this.getFilterOptions();
      this.keyNum += 1;
      this.keyFloc6++;
      this.floc8Key += 1;
    },
  },
};
</script>

<style lang="scss" scoped>
// ::v-deep .v-list-item {
//   padding: 0;
// }
.full-width {
  width: 100%;
}
.max-width {
  max-width: 100%;
}
.one-third {
  max-width: 32%;
  min-width: 32%;
}
.vertical-header {
  transform-origin: 0 2;
  transform: rotate(270deg);
  max-height: 4%;
}

.root {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100%;
  // overflow: scroll;
  gap: 8px;
}
.main-card {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  width: 100%;
  // overflow: hidden;
}

.side-card {
  width: 40ch;
  display: flex;
  flex-direction: column;
  height: 100%;
  // overflow: hidden;
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
      rgb(65, 143, 222) 0deg,
      rgb(65, 143, 222) 90deg,
      rgb(255, 193, 5) 90deg,
      rgb(255, 193, 5) 270deg,
      rgb(65, 143, 222) 270deg,
      rgb(65, 143, 222) 360deg
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

.filter-title {
  height: 38px;
  position: sticky;
  margin-top: 10px;
  margin-bottom: 10px;
  .title {
    opacity: 1;
    display: flex;
    padding: 0px 0px;
    margin: 0px 0px;
    text-transform: capitalize;
    align-items: center;
    margin-left: 16px;
  }
}
.filter-content {
  height: 300px;
  overflow: scroll;
}
</style>
