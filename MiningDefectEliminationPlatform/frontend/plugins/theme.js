import Vue from "vue";

export default ({ $vuetify, app }, inject) => {
  inject("theme", {
    init() {
      let theme = localStorage.getItem("dark_theme");

      if (theme) {
        if (theme == "true") {
          $vuetify.theme.dark = true;
        } else {
          $vuetify.theme.dark = false;
        }
      }

      this.setChartTheme();
    },
    isDark() {
      return $vuetify.theme.dark;
    },
    getDepLogo() {
      return `/dep_logo_${$vuetify.theme.dark ? "dark" : "light"}.svg`;
    },
    getLogo() {
      return `/fmg_logo_${$vuetify.theme.dark ? "dark" : "light"}.svg`;
    },
    getClass() {
      return `theme--${$vuetify.theme.dark ? "dark" : "light"}`;
    },
    toggle() {
      $vuetify.theme.dark = !$vuetify.theme.dark;

      localStorage.setItem("dark_theme", $vuetify.theme.dark.toString());

      this.setChartTheme();

      // window.dispatchEvent(
      //   new CustomEvent("theme-changed", {
      //     detail: {
      //       storage: localStorage.getItem("foo-key"),
      //     },
      //   })
      // );
    },
    setChartTheme() {
      let color1 = this.isDark() ? "#FFFFFF" : "#111111";
      let color2 = this.isDark() ? "#555555" : "#DDDDDD";

      try {
        Chart.defaults.global.defaultFontColor = color1;
        Chart.defaults.global.defaultColor = color2;
        Chart.defaults.scale.gridLines.color = color2;
        Chart.defaults.scale.gridLines.zeroLineColor = color2;
      } catch {}
    },
  });
};
