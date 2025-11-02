<script>
import { Bar } from "vue-chartjs";
import chart_mixin from "@/assets/chart_mixin.js";

export default {
  extends: Bar,
  mixins: [chart_mixin],
  mounted() {
    this.addPlugin({
      id: "LabelDraw",
      beforeTooltipDraw: (chart) => {
        // ------------------------------------------------------
        //  This is for the threshold
        // ------------------------------------------------------

        if (this.lineAt.length != 0 && this.chartTitle != "Trend") {
          // the upper threshold
          let themeColor = this.$vuetify.theme.themes.light;
          if (this.$vuetify.theme) themeColor = this.$vuetify.theme.themes.dark;
          this.drawThreshold(chart, "rca", "RCA", "rgba(229,57,53,0.5)");
          // the lower threshold
          this.drawThreshold(chart, "why5", "5-Why", "rgba(255,193,5,0.8)");
        }
      },
      afterDraw: (chart) => {
        // xxx.fillText("datatata", x - 12, yAxis.bottom + 10);
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
        ctx.font = "bold 14px Roboto";
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
      default: "",
    },
    currentStack: {
      type: Object,
      default: () => {
        return { datasetIndex: null, index: null };
      },
    },
    threshold_5_why: { type: Number, require: false, default: 2 },
  },
  data() {
    return {
      count: [],
      labels: [],
      lineAt: { rca: 5, why5: 2, rca_count: 400, why5_count: 200 },
      // theme: localStorage.getItem("dark_theme"),
      chartdata: {
        labels: [],
        datasets: [
          {
            type: "bar",
            yAxisID: "A",
            xAxisID: "xAxis1",
            label: "Within One Week",
            order: 2,
            data: [],
            backgroundColor: [],
            borderColor: [],
            pointStyle: [],
            // borderColor: "#bae755",
          },
          {
            type: "bar",
            yAxisID: "A",
            label: "Over A Week",
            order: 2,
            data: [],
            backgroundColor: [],
            borderColor: [],
            pointStyle: [],
          },
          {
            type: "line",
            label: "Count   ⚑ Investigation Created",
            lineTension: 0,
            yAxisID: "B",
            xAxisID: "xAxis1",
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
            borderWidth: 3,
            // borderColor: this.$vuetify.theme.themes.light.accent,
            // borderColor: "#bae755",
          },
        ],
      },
      options: {
        legend: {
          // onClick: (click, legendItem,legend) => {},
          display: true,
          labels: {
            usePointStyle: true,
            fontSize: 15,
            radius: 4,
            generateLabels: (chart) => {
              const COLOR_PRIMARY = "#FF9800"; // "Within A Week"
              const COLOR_SECONDARY = "#0876bd"; // "Over A Week"
              const legendColor = [COLOR_SECONDARY, COLOR_PRIMARY, "#DDDDDD"];
              let result = chart.data.datasets.map((dataset, index) => ({
                text: dataset.label,
                fillStyle: legendColor[index],
                storekeStyle: dataset.borderColor,
                lineWidth: 0,
                pointStyle: dataset.pointStyle[0],
                radius: 4,
                hidden: false,
              }));

              return result;
            },
          },
          // position: "bottom",
          // labels: {
          //   fontColor: "#000080",
          // },
          // labels: {
          //   usePointStyle: true,
          //   pointStyle: ["line", "rect", "rect"],
          //   // fontColor: "#202020",
          // },
        },
        scales: {
          yAxes: [
            {
              id: "A",
              stacked: true,
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
              color: null,
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
              id: "xAxis1",
              stacked: true,
              gridLines: {
                display: true,
                drawOnChartArea: false,
                // color: "#FFFFFF", // this is for the dark mode
              },
              ticks: {
                display: true,
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
      },
    };
  },
  watch: {
    theme(val) {
      this.setTheme(val);
      this.renderChart(this.chartdata, this.options);
    },
  },
  methods: {
    drawThreshold(chart, key, text, lineColor, leftAxes = true) {
      let axisIndex = 0;
      if (!leftAxes) axisIndex = 1;

      var lineAt = this.lineAt[key];
      var ctxPlugin = chart.chart.ctx;
      var xAxe = chart.scales[chart.config.options.scales.xAxes[0].id];
      var yAxe = chart.scales[chart.config.options.scales.yAxes[axisIndex].id];

      if (this.threshold_5_why != 2 && key == "why5") lineAt = this.threshold_5_why;
      if (yAxe.min != 0) return;

      ctxPlugin.strokeStyle = lineColor;
      ctxPlugin.beginPath();
      lineAt = (lineAt - yAxe.min) * (100 / yAxe.max);
      lineAt = ((100 - lineAt) / 100) * yAxe.height + yAxe.top;
      ctxPlugin.lineWidth = 2;
      ctxPlugin.moveTo(xAxe.left, lineAt);
      ctxPlugin.lineTo(xAxe.right, lineAt);
      ctxPlugin.stroke();
      // the text align with the line
      let chartInstance = chart;
      let ctx = chartInstance.ctx;
      ctx.textAlign = "right";
      ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
      ctx.font = "bold 14px Roboto";
      if (this.$vuetify.theme.isDark) ctx.fillStyle = "rgba(255, 255, 255, 0.77)";
      ctx.textBaseline = "top";
      ctxPlugin.fillText(text, xAxe.right - 5, lineAt - 15);
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
        this.chartdata.datasets[2].borderColor = this.$vuetify.theme.themes.dark.accent;
        this.chartItems.forEach((i, index) => {
          let color = "";
          if (i.clicked) color = "#FFFFFF";
          this.chartdata.datasets[0].borderColor.push(color);
        });
      }
    },
    handleClicked(e, i) {
      if (i.length > 0 && this.currentStack.datasetIndex !== 2) {
        let period = "within 7 days";
        if (this.currentStack.datasetIndex == 1) period = "over 7 days";
        if (this.currentStack.datasetIndex == 2) period = "all data within date range";
        const equipName = this.labels[i[0]._index];
        this.$emit("clicked", {
          data: equipName,
          index: i[0]._index,
          currentStack: this.currentStack,
          period: period,
        });
      } else {
        this.$emit("clicked", null);
      }
    },
    handleTooltip(tooltipItems, data) {
      // get the current stack for the handle click function
      this.currentStack.datasetIndex = tooltipItems.datasetIndex;
      this.currentStack.index = tooltipItems.index;

      let sum = this.chartItems[tooltipItems.index].within_week_sum;
      // let count = this.chartItems[tooltipItems.index].within_week_count;
      let total = this.chartItems[tooltipItems.index].sum_duration;
      if (tooltipItems.datasetIndex == 1) {
        // count = this.chartItems[tooltipItems.index].over_week_count;
        sum = this.chartItems[tooltipItems.index].over_week_sum;
      }

      if (tooltipItems.datasetIndex == 2) {
        let count = this.chartItems[tooltipItems.index].equipment_count;
        sum = this.chartItems[tooltipItems.index].sum_duration;
        return [
          `Count: ${count} `,
          // `Sum Hours: ${parseFloat(sum).toFixed(1).toString()} `,
          // `Total: ${parseFloat(total).toFixed(1).toString()}`,
        ];
      }
      return [
        // `Number Count: ${count} `,
        `Sum Hours: ${parseFloat(sum).toFixed(1).toString()} `,
        `Total Hours: ${parseFloat(total).toFixed(1).toString()}`,
      ];
    },
    handleData(res) {
      this.setTheme(this.theme);
      if (res.length > 0 && res[0].cause != undefined) {
        // for the main chart

        // this is for when all the sum_durations are too much lower than 1 and set the valuable ticks
        if (res[0].sum_duration <= 0.2 && res[0].sum_duration != 0 && res[0].sum_duration != null)
          this.options.scales.yAxes[0].ticks.stepSize = 0.02;
        else if (res[0].sum_duration <= 0.31 && res[0].sum_duration != 0 && res[0].sum_duration != null)
          this.options.scales.yAxes[0].ticks.stepSize = 0.05;

        // make sure clean all the bars are unclicked
        const originChart = res.every((r) => r.clicked == null);

        // makse sure the array of color for dots is emypty
        this.chartdata.datasets[2].pointBackgroundColor = [];
        this.chartdata.datasets[0].backgroundColor = [];
        this.chartdata.datasets[1].backgroundColor = [];
        // --------------------------------------------

        // for loop start
        res.forEach((r, index) => {
          const COLOR_PRIMARY = "rgba(255, 152, 0, 1)"; // "Within A Week"
          const COLOR_SECONDARY = "rgba(8,118,189, 1)"; // "Over A Week"
          const COLOR_PRIMARY_BACKGROUND = "rgba(255, 152, 0, 0.25)"; // "Within A Week"
          const COLOR_SECONDARY_BACKGROUND = "rgba(8,118,189, 0.25)"; // "Over A Week"
          const COLOR_CLICKED = "#70C1A6";
          const BLUE = "#8EA1C9";
          const ORANGE = "#F78F68";
          const GREEN = "#70C1A6";

          this.labels.push([r.equipment_name, r.cause]);
          let line = "⚑ ";
          if (r.has_investigation == 0) line = "  ";
          // those are for the line break as we need to put r.equipment_name and r.cause together
          if (r.equipment_name.length > 17) {
            let name = r.equipment_name.split(" ");

            let i = 0;
            let lineBreak = [];
            while (i < name.length) {
              if (line.length + name[i].length + 1 > 17) {
                if (i == 0) line += name[0];
                if (i == 0) name = name.slice(i, name.length);
                else name = name.slice(i - 1, name.length);
                lineBreak.push(line + " ");
                i = 0;
                line = " ";
              } else {
                line += name[i];
              }
              i++;
            }
            lineBreak.push(line);
            this.chartdata.labels.push([...lineBreak, r.cause]);
          } else if (r.cause.length > 17) {
            // when the cause text length is greater than a certain number
            this.chartdata.labels.push([line + r.equipment_name, ...r.cause.split(" ")]);
          } else {
            this.chartdata.labels.push([line + r.equipment_name, r.cause]);
          }

          this.chartdata.datasets[0].data.push(r.within_week_sum);
          this.chartdata.datasets[1].data.push(r.over_week_sum);
          this.chartdata.datasets[2].data.push(r.equipment_count);
          if (r.clicked != null) {
            if (r.clicked.datasetIndex != 2) {
              // let unclickedIndex = 1;
              // if (r.clicked.datasetIndex == 1) unclickedIndex = 0;
              // this.chartdata.datasets[
              //   r.clicked.datasetIndex
              // ].backgroundColor.push(COLOR_PRIMARY);
              // this.chartdata.datasets[unclickedIndex].backgroundColor.push(
              //   COLOR_CLICKED
              // );
              this.chartdata.datasets[0].backgroundColor.push(COLOR_SECONDARY);
              this.chartdata.datasets[1].backgroundColor.push(COLOR_PRIMARY);
            } else {
              this.chartdata.datasets[0].backgroundColor.push(COLOR_SECONDARY);
              this.chartdata.datasets[1].backgroundColor.push(COLOR_PRIMARY);
            }
          } else if (originChart) {
            this.chartdata.datasets[0].backgroundColor.push(COLOR_SECONDARY);
            this.chartdata.datasets[1].backgroundColor.push(COLOR_PRIMARY);
          } else {
            this.chartdata.datasets[0].backgroundColor.push(
              COLOR_SECONDARY_BACKGROUND
            );
            this.chartdata.datasets[1].backgroundColor.push(
              COLOR_PRIMARY_BACKGROUND
            );
          }

          // --------------------------------------
          //  address the color to the spots
          // --------------------------------------
          let dotColor = "#DDDDDD";
          // if (r.equipment_count > this.lineAt.rca_count) dotColor = "red";
          // if (
          //   r.equipment_count < this.lineAt.rca_count &&
          //   r.equipment_count > this.lineAt.why5_count
          // )
          //   dotColor = "yellow";

          this.chartdata.datasets[2].pointBackgroundColor.push(dotColor);
          this.chartdata.datasets[2].pointBorderColor.push(dotColor);
          this.chartdata.datasets[0].pointStyle.push("rect");
          this.chartdata.datasets[1].pointStyle.push("rect");
          this.chartdata.datasets[2].pointStyle.push("dot");
          // -----------------------------------------

          this.chartdata.datasets[0].label = "Over A Week";
          this.chartdata.datasets[1].label = "Within A Week";
          this.options.scales.yAxes[0].scaleLabel.labelString = "Effective Duration (hrs)";
          this.options.scales.yAxes[1].scaleLabel.labelString = "Count";
          this.count.push(r.equipment_count);
        });
      }
    },
  },
};
</script>
