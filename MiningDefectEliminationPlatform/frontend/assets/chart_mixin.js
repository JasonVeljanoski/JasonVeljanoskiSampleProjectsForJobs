export default {
  computed: {
    theme() {
      return this.$theme.isDark();
    },
  },
  watch: {
    theme() {
      this.renderChart(this.data, this.options);
    },
    data() {
      this.renderChart(this.data, this.options);
    },
    options() {
      this.renderChart(this.data, this.options);
    },
  },
};
