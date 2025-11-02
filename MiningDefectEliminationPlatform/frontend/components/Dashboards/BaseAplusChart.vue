<script>
import { Bar } from "vue-chartjs";
import chart_mixin from "@/assets/chart_mixin.js";

export default {
  extends: Bar,
  mixins: [chart_mixin],
  mounted() {
    this.addPlugin({
      id: "LabelDraw",
      afterDraw: (chart) => {
        // ------------------------------------------------------
        //  This is for the tooltip at the center of the bar
        // ------------------------------------------------------
        let chartInstance = chart;
        let ctx = chartInstance.ctx;
        ctx.textAlign = "center";
        ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
        if (this.$vuetify.theme.isDark) ctx.fillStyle = "rgba(255, 255, 255, 0.7)";
        ctx.textBaseline = "top";
        ctx.strokeStyle = "white";
        ctx.font = "bold 15px Roboto";

        chart.data.datasets.forEach((dataset, i) => {
          let meta = chartInstance.controller.getDatasetMeta(i);
          meta.data.forEach((bar, index) => {
            let data = dataset.data[index];
            if (data != 0) {
              if (data !== undefined && data % 1 !== 0) data = data.toFixed(1);

              ctx.fillText(data, bar._model.x, bar._model.base + (bar._model.y - bar._model.base) / 2);
            }
          });
        });
      },
    });

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
      default: "Trend",
    },
  },
  data() {
    return {
      COLOR_PRIMARY: "#FF9800",
      COLOR_SECONDARY: "#0876bd",
      count: [],
      labels: [],
      lineAt: { rca: 5, why5: 2, rca_count: 400, why5_count: 200 },
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
            borderColor: [],
            // borderColor: "#bae755",
          },
          {
            type: "line",
            // label: "Count   ⚑ Investigation Created",
            label: "",
            lineTension: 0,
            yAxisID: "B",
            showLine: false,
            pointBackgroundColor: [],
            // pointRadius: 40,
            pointRadius: 10,
            pointBorderColor: [],
            // pointHoverRadius: 50,
            pointHoverRadius: 15,
            pointStyle: [],
            order: 1,
            data: [],
            backgroundColor: "rgba(241,123,121,0)",
            borderWidth: 0,
            // borderColor: this.$vuetify.theme.themes.light.accent,
            // borderColor: "#bae755",
          },
        ],
      },
      options: {
        legend: {
          display: false,
          // position: "bottom",
          // labels: {
          //   fontColor: "#000080",
          // },
          labels: {
            usePointStyle: false,
            // fontColor: "#202020",
            // generateLabels: (chart) => {
            //   if (chart.data.labels.length == 0) return [];
            //   else {
            //     return [
            //       {
            //         text: "Effective duration (hrs)",
            //         fillStyle: this.COLOR_PRIMARY,
            //         storekeStyle: chart.data.datasets[0].borderColor,
            //         lineWidth: 0,
            //         pointStyle: "rect",
            //         hidden: false,
            //       },
            //       {
            //         text: "Count",
            //         fillStyle: "#DDDDDD",
            //         storekeStyle: chart.data.datasets[0].borderColor,
            //         lineWidth: 0,
            //         pointStyle: "dot",
            //         hidden: false,
            //       },
            //     ];
            //   }
            // },
          },
        },
        scales: {
          yAxes: [
            {
              id: "A",
              gridLines: {
                display: true,
                drawOnChartArea: false,
                // color: "#FFFFFF", // this is for the dark mode
              },
              display: true,
              ticks: {
                beginAtZero: true,
                precision: 0,
                // fontColor: null, // this is for the dark mode
              },
              scaleLabel: {
                display: true,
                labelString: "",
              },
            },
            {
              id: "B",
              type: "linear",
              position: "right",
              gridLines: { drawOnChartArea: false },
              borderWidth: 0,
              ticks: {
                display: true,
                beginAtZero: true,
                precision: 0,
              },
              scaleLabel: {
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
                // color: "#FFFFFF", // this is for the dark mode
              },
              ticks: {
                autoSkip: false,
                maxRotation: 0,
                minRotation: 0,
                // fontColor: "#FFFFFF", // this is for the dark mode
              },
            },
          ],
        },
        onClick: this.handleClicked,
        maintainAspectRatio: false,
        tooltips: {
          displayColors: false,
          enabled: true,
          callbacks: {
            title: () => null, // or function () { return null; }
            label: this.handleTooltip,
          },
        },
        title: {
          display: true,
          text: this.chartTitle,
          fontSize: 24,
        },
        hover: {
          onHover: function (event, chart) {
            if (chart.length > 0) event.target.style.cursor = "pointer";
          },
        },
        animation: false,
        // animation: {
        //   duration: 0,
        //   // TODO move to after draw event
        //   onProgress: function (e) {
        //     let chartInstance = this.chart,
        //       ctx = chartInstance.ctx;
        //     ctx.textAlign = "center";
        //     ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
        //     ctx.textBaseline = "top";

        //     this.data.datasets.forEach(function (dataset, i) {
        //       let meta = chartInstance.controller.getDatasetMeta(i);
        //       meta.data.forEach(function (bar, index) {
        //         let data = dataset.data[index];
        //         if (data != 0) {
        //           if (data !== undefined && data % 1 !== 0)
        //             data = data.toFixed(1);
        //           ctx.fillText(
        //             data,
        //             bar._model.x,
        //             bar._model.base + (bar._model.y - bar._model.base) / 2
        //           );
        //         }
        //       });
        //     });
        //   },
        // },
        // plugins: {
        //   datalabels: {
        //     anchor: "center",
        //     align: "center",
        //     // color: "black",
        //     font: {
        //       weight: "normal",
        //     },
        //     labels: ["1", "2", "3", "4"],
        //   },
        // },
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
    // drawThreshold(chart, key, text, lineColor, leftAxes = true) {
    //   let axisIndex = 0;
    //   if (!leftAxes) axisIndex = 1;

    //   var lineAt = this.lineAt[key];
    //   var ctxPlugin = chart.chart.ctx;
    //   var xAxe = chart.scales[chart.config.options.scales.xAxes[0].id];
    //   var yAxe = chart.scales[chart.config.options.scales.yAxes[axisIndex].id];

    //   if (yAxe.min != 0) return;

    //   ctxPlugin.strokeStyle = lineColor;
    //   ctxPlugin.beginPath();
    //   lineAt = (lineAt - yAxe.min) * (100 / yAxe.max);
    //   lineAt = ((100 - lineAt) / 100) * yAxe.height + yAxe.top;
    //   ctxPlugin.lineWidth = 2;
    //   ctxPlugin.moveTo(xAxe.left, lineAt);
    //   ctxPlugin.lineTo(xAxe.right, lineAt);
    //   ctxPlugin.stroke();
    //   // the text align with the line
    //   let chartInstance = chart;
    //   let ctx = chartInstance.ctx;
    //   ctx.textAlign = "right";
    //   ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
    //   if (this.$vuetify.theme.isDark)
    //     ctx.fillStyle = "rgba(255, 255, 255, 0.77)";
    //   ctx.textBaseline = "top";
    //   ctx.font = "bold 15px Roboto";
    //   // ctxPlugin.fillText(text, xAxe.right - 5, lineAt - 15);
    // },
    setTheme(isDark) {
      this.options.scales.yAxes[0].gridLines.color = "black";
      this.options.scales.yAxes[1].gridLines.color = "black";
      this.options.scales.xAxes[0].gridLines.color = "black";
      this.options.scales.xAxes[0].ticks.fontColor = "black";
      this.options.scales.yAxes[0].ticks.fontColor = "black";
      // this.options.scales.yAxes[1].ticks.fontColor = "black";
      this.options.legend.labels.fontColor = "black";
      this.options.scales.yAxes[0].scaleLabel.fontColor = "black";
      // this.options.scales.yAxes[1].scaleLabel.fontColor = "black";
      if (this.theme) {
        this.options.scales.yAxes[0].gridLines.color = "#FFFFFF";
        this.options.scales.yAxes[1].gridLines.color = "#FFFFFF";
        this.options.scales.xAxes[0].gridLines.color = "#FFFFFF";
        this.options.scales.xAxes[0].ticks.fontColor = "#FFFFFF";
        this.options.scales.yAxes[0].ticks.fontColor = "#FFFFFF";
        // this.options.scales.yAxes[1].ticks.fontColor = "#FFFFFF";
        this.options.legend.labels.fontColor = "#FFFFFF";
        this.options.scales.yAxes[0].scaleLabel.fontColor = "#FFFFFF";
        // this.options.scales.yAxes[1].scaleLabel.fontColor = "#FFFFFF";
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
      if (i.length > 0) {
        const equipName = this.labels[i[0]._index];
        this.$emit("clicked", {
          data: equipName,
          index: i[0]._index,
          period: "",
        });
      } else {
        this.$emit("clicked", null);
      }
    },
    handleTooltip(tooltipItems, data) {
      if (tooltipItems.datasetIndex == 1) {
        return [`Number Count: ${tooltipItems.value} `];
      } else {
        return [`Sum hrs of day: ${parseFloat(this.count[tooltipItems.index]).toFixed(1).toString()} `];
      }
    },

    handleData(res) {
      this.setTheme(this.theme);

      if (res.length > 0 && res[0].date != undefined) {
        // for the sub chart
        if (res.length !== 7) this.options.scales.xAxes[0].ticks.minRotation = 90;

        res.forEach((r) => {
          let bar_color = this.COLOR_SECONDARY;
          if (r.within_a_week) bar_color = this.COLOR_PRIMARY;
          const label = r.date.slice(8, 10) + "/" + r.date.slice(5, 7);
          this.labels.push(r.date);
          // this.options.scales.yAxes[1].ticks.display = false;

          this.chartdata.labels.push(label);
          this.chartdata.datasets[0].data.push(r.sum);
          if (r.count != 0) this.chartdata.datasets[1].data.push(r.count);
          else this.chartdata.datasets[1].data.push(undefined);
          this.chartdata.datasets[0].backgroundColor.push(
            // "rgba(255, 99, 132,0.6)"
            bar_color
          );
          this.chartdata.datasets[1].pointBackgroundColor.push("#DDDDDD");
          this.chartdata.datasets[0].label = r.yLabel;
          this.options.scales.xAxes[0].ticks.maxRotation = 0;
          this.options.scales.yAxes[0].scaleLabel.labelString = "Effective Duration (hrs)";
          this.options.scales.yAxes[1].scaleLabel.labelString = "Count";
          this.count.push(r.sum);
        });
      }
    },
  },
};
</script>
