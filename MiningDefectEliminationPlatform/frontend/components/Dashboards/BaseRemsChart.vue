<script>
import { Bar } from "vue-chartjs";

import chart_mixin from "@/assets/chart_mixin.js";

export default {
  extends: Bar,
  mixins: [chart_mixin],
  mounted() {
    // window.addEventListener("theme-changed", (event) => {
    //   this.theme = localStorage.getItem("dark_theme");
    // });
    // this.setTheme(this.theme);
    this.handleData(this.chartItems);
    this.renderChart(this.chartdata, this.options, this.plugins);
  },

  props: {
    chartItems: {
      type: Array | Object,
      default: () => [],
    },
    chartTitle: {
      type: String,
      default: "",
    },
    subChartTitle: {
      type: Array | Object,
      default: null,
    },
    colorIndex: {
      type: Number,
      default: null,
    },
    maxFloc7: {
      type: Number,
      default: null,
    },
    maxCount: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      count: [],
      labels: [],
      legend: null,
      barColors: [
        "rgba(241,123,121,0.9)",
        "rgba(117,161,199,0.9)",
        "rgba(105,170,165,0.9)",
        "rgba(186,149,130,0.9)",
        "rgba(150,141,138,0.9)",
        "rgba(231,153,179,0.9)",
        "rgba(211,179,72,0.9)",
        "rgba(249,166,85,0.9)",
        "rgba(194,144,180,0.9)",
        "rgba(105,170,165,0.9)",
      ],
      // theme: localStorage.getItem("dark_theme"),
      chartdata: {
        labels: [],
        datasets: [
          {
            type: "bar",
            label: "",
            yAxisID: "A",
            order: 2,
            data: [],
            backgroundColor: [],
            barPercentage: 1,
            borderColor: [],
            borderWidth: [],
            // borderColor: "#bae755",
          },
          {
            type: "line",
            label: "Count",
            lineTension: 0,
            yAxisID: "B",
            order: 1,
            data: [],
            backgroundColor: "rgba(241,123,121,0)",
            borderWidth: 3,
            borderColor: "rgb(200,200,200)",
            // borderColor: "#bae755",
          },
        ],
      },
      options: {
        legend: {
          display: true,
          // position: "bottom",
          labels: {
            fontColor: null,
          },
        },
        height: 300,
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          yAxes: [
            {
              id: "A",
              gridLines: {
                display: true,
                drawOnChartArea: false,
                color: null, // this is for the dark mode
              },
              display: true,
              ticks: {
                beginAtZero: true,
                precision: 0,
                fontColor: null, // this is for the dark mode
                callback: function (val, index) {
                  if (index % 2 == 0) return val;
                },
              },
              scaleLabel: {
                display: true,
                labelString: "",
                fontColor: null,
              },
            },
            {
              id: "B",
              type: "linear",
              position: "right",
              gridLines: { drawOnChartArea: false },
              ticks: {
                beginAtZero: true,
                precision: 0,
                callback: function (val, index) {
                  if (index % 2 == 0) return val;
                },
              },
              scaleLabel: {
                fontColor: null,
                display: true,
                labelString: "",
              },
            },
          ],
          xAxes: [
            {
              gridLines: {
                display: true,
                drawOnChartArea: false,
                color: null, // this is for the dark mode
              },
              ticks: {
                autoSkip: false,
                maxRotation: 0,
                minRotation: 0,
                fontColor: null, // this is for the dark mode
              },
            },
          ],
        },
        onClick: this.handleClicked,
        maintainAspectRatio: false,
        tooltips: {
          enabled: true,
          callbacks: {
            label: this.handleTooltip,
          },
        },
        title: {
          display: true,
          text: this.chartTitle,
        },
        hover: {
          onHover: function (event, chart) {
            if (chart.length > 0) event.target.style.cursor = "pointer";
          },
        },
        animation: {
          onComplete: function (e) {
            var chartInstance = this.chart,
              ctx = chartInstance.ctx;
            ctx.textAlign = "center";
            ctx.fillStyle = "rgba(0, 0, 0, 0.35)";
            ctx.textBaseline = "top";

            this.data.datasets.forEach(function (dataset, i) {
              var meta = chartInstance.controller.getDatasetMeta(i);
              meta.data.forEach(function (bar, index) {
                var data = dataset.data[index];
                if (data != undefined && data != 0) {
                  if (data % 1 !== 0) data = data.toFixed(1);
                  ctx.fillText(
                    data,
                    bar._model.x,
                    bar._model.base + (bar._model.y - bar._model.base) / 2
                  );
                }
              });
            });
          },
          onProgress: function (e) {
            var chartInstance = this.chart,
              ctx = chartInstance.ctx;
            ctx.textAlign = "center";
            ctx.fillStyle = "rgba(0, 0, 0, 0.35)";
            ctx.textBaseline = "top";

            this.data.datasets.forEach(function (dataset, i) {
              var meta = chartInstance.controller.getDatasetMeta(i);
              meta.data.forEach(function (bar, index) {
                var data = dataset.data[index];
                if (data != undefined && data != 0) {
                  if (data % 1 !== 0) data = data.toFixed(1);
                  ctx.fillText(
                    data,
                    bar._model.x,
                    bar._model.base + (bar._model.y - bar._model.base) / 2
                  );
                }
              });
            });
          },
        },
        plugins: {
          datalabels: {
            anchor: "center",
            align: "center",
            // color: "black",
            font: {
              weight: "normal",
            },
            labels: ["1", "2", "3", "4"],
          },
        },
      },
    };
  },
  watch: {
    theme(val) {
      this.setTheme(val);
      this.renderChart(this.chartdata, this.options, this.plugins);
    },
  },
  methods: {
    removeTicksHalf(val, index) {
      delete this.options.scales.yAxes[0].ticks.callback;
      delete this.options.scales.yAxes[1].ticks.callback;
    },
    setTheme(isDark) {
      this.options.scales.yAxes[0].gridLines.color = "black";
      this.options.scales.yAxes[1].gridLines.color = "black";
      this.options.scales.xAxes[0].gridLines.color = "black";
      this.options.scales.xAxes[0].ticks.fontColor = "black";
      this.options.scales.yAxes[0].ticks.fontColor = "black";
      this.options.scales.yAxes[1].ticks.fontColor = "black";
      this.options.legend.labels.fontColor = "black";
      this.options.scales.yAxes[0].scaleLabel.fontColor = "black";
      this.options.scales.yAxes[1].scaleLabel.fontColor = "black";
      if (this.theme) {
        this.options.scales.yAxes[0].gridLines.color = "#FFFFFF";
        this.options.scales.yAxes[1].gridLines.color = "#FFFFFF";
        this.options.scales.xAxes[0].gridLines.color = "#FFFFFF";
        this.options.scales.xAxes[0].ticks.fontColor = "#FFFFFF";
        this.options.scales.yAxes[0].ticks.fontColor = "#FFFFFF";
        this.options.scales.yAxes[1].ticks.fontColor = "#FFFFFF";
        this.options.legend.labels.fontColor = "#FFFFFF";
        this.options.scales.yAxes[0].scaleLabel.fontColor = "#FFFFFF";
        this.options.scales.yAxes[1].scaleLabel.fontColor = "#FFFFFF";
      }
      this.chartdata.datasets[0].borderColor = [];
      this.chartItems.forEach((i, index) => {
        let color = "";
        if (i.clicked) color = "black";
        this.chartdata.datasets[0].borderColor.push(color);
      });
      if (isDark == true) {
        this.chartdata.datasets[0].borderColor = [];
        this.chartItems.forEach((i, index) => {
          let color = "";
          if (i.clicked) color = "#FFFFFF";
          this.chartdata.datasets[0].borderColor.push(color);
        });
      }
    },
    handleClicked(e, i) {
      if (i[0] != undefined) {
        let barInfo = {};
        if (
          this.chartItems[0].floc7 === undefined &&
          this.chartItems[0].name !== "floc6" &&
          this.chartItems[0].name != "floc7"
        ) {
          barInfo = {
            name: "floc7",
            floc6: this.legend,
            floc7: this.chartItems[i[0]._index].floc,
            index: this.colorIndex,
            clickedIndex: i[0]._index,
          };
        } else if (this.chartItems[0].name == "floc6") {
          barInfo = {
            name: "floc6",
            floc6: this.chartItems[i[0]._index].floc,
            clickedIndex: i[0]._index,
          };
        } else if (this.chartItems[0].name == "floc7") {
          barInfo = {
            name: "floc7",
            floc6: this.chartItems[i[0]._index].floc6,
            floc7: this.chartItems[i[0]._index].floc,
            index: this.chartItems[0].colorIndex,
            clickedIndex: i[0]._index,
            other: true,
          };
        } else {
          barInfo = {
            name: "floc8",
            floc6: this.chartItems[0].floc6,
            floc7: this.chartItems[0].floc7,
            floc8: this.chartItems[i[0]._index].floc,
            clickedIndex: i[0]._index,
          };
        }
        this.$emit("clicked", barInfo);
      }
    },
    handleTooltip(tooltipItems, data) {
      if (tooltipItems.value == this.count[tooltipItems.index])
        return [`Count: ${tooltipItems.value}`];
      if (tooltipItems.value == undefined) tooltipItems.value = 0;
      tooltipItems.value = parseFloat(tooltipItems.value).toFixed(1);
      return [
        `Amount of hrs: ${tooltipItems.value} `,
        `Count: ${this.count[tooltipItems.index]} `,
      ];
    },
    handleData(res) {
      this.setTheme(this.theme);
      if (res.length > 0) {
        this.legend = null;

        res.forEach((r, i) => {
          if (r != null && r.clicked == true) {
            if (this.theme == true) {
              this.chartdata.datasets[0].borderColor.push("#FFFFFF");
            } else this.chartdata.datasets[0].borderColor.push("black");
            this.chartdata.datasets[0].borderWidth.push(2);
          } else {
            this.chartdata.datasets[0].borderColor.push("");
            this.chartdata.datasets[0].borderWidth.push(0);
          }
          // to assign the value to the floc7 & 8 which are in different charts
          if (r.floc == null && r.name != null)
            // r.floc = "No F" + r.name.slice(1, 5).toUpperCase();
            r.floc = "NO F" + r.name.slice(1, 5).toUpperCase();
          this.chartdata.labels.push(r.floc);
          this.chartdata.datasets[0].data.push(r.duration);
          this.chartdata.datasets[1].data.push(r.count);
          this.count.push(r.count);
          if (r.name == "floc6")
            this.chartdata.datasets[0].backgroundColor.push(this.barColors[i]);

          if (r.name == "floc7_1") {
            this.options.scales.yAxes[0].ticks.max = this.maxFloc7;
            // this.options.scales.yAxes[0].ticks.maxTicksLimit = 7;
            this.options.scales.yAxes[1].ticks.max = this.maxCount;
            // this.options.scales.yAxes[1].ticks.maxTicksLimit = 7;
            this.legend = this.subChartTitle[0].floc;
            this.chartdata.datasets[0].label = this.legend;

            this.options.scales.yAxes[0].scaleLabel.labelString =
              "Effective Duration (hrs)";
            this.chartdata.datasets[0].backgroundColor.push(this.barColors[0]);
          }
          if (r.name == "floc7_2") {
            this.options.scales.yAxes[0].ticks.max = this.maxFloc7;
            this.options.scales.yAxes[1].ticks.max = this.maxCount;
            this.legend = this.subChartTitle[1].floc;
            this.chartdata.datasets[0].label = this.legend;
            this.chartdata.datasets[0].backgroundColor.push(this.barColors[1]);
          }

          if (r.name == "floc7_3") {
            this.options.scales.yAxes[0].ticks.max = this.maxFloc7;
            this.options.scales.yAxes[1].ticks.max = this.maxCount;
            this.legend = this.subChartTitle[2].floc;
            this.chartdata.datasets[0].label = this.legend;
            this.chartdata.datasets[0].backgroundColor.push(this.barColors[2]);
            this.options.scales.yAxes[1].scaleLabel.labelString = "Count";
          }
        });

        if (res[0].name == "floc8") {
          // this.removeTicksHalf();
          this.chartdata.datasets[0].label = res[0].floc7;
        }

        // this is for remove the legend of floc6
        if (res[0].name == "floc6") {
          this.removeTicksHalf();
          this.options.legend.display = false;
          this.options.scales.yAxes[0].scaleLabel.labelString =
            "Effective Duration (hrs)";
          this.options.scales.yAxes[1].scaleLabel.labelString = "Count";
        }
        if (res[0].name == "floc7") {
          // this.removeTicksHalf();
          if (this.subChartTitle != null)
            this.chartdata.datasets[0].label =
              "Top 10 FLOC7 of " + this.subChartTitle[0];
          this.options.scales.yAxes[0].scaleLabel.labelString =
            "Effective Duration (hrs)";
          this.options.scales.yAxes[1].scaleLabel.labelString = "Count";
          res.forEach((r) =>
            this.chartdata.datasets[0].backgroundColor.push(
              this.barColors[r.colorIndex]
            )
          );
        }

        // this is for fixing the floc8 coloring bug
        if (res[0].name == "floc8") {
          this.options.scales.yAxes[0].scaleLabel.labelString =
            "Effective Duration (hrs)";
          this.options.scales.yAxes[1].scaleLabel.labelString = "Count";
          this.chartdata.datasets[0].backgroundColor = [];
          res.forEach((r) =>
            this.chartdata.datasets[0].backgroundColor.push(
              this.barColors[res.colorIndex]
            )
          );
        }
      }
    },
  },
};
</script>
