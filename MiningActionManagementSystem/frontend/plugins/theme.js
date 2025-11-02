import Vue from 'vue'

export default ({ $vuetify, app }, inject) => {
  inject('theme', {
    init() {
      const theme = localStorage.getItem('dark_theme')

      if (theme) {
        if (theme == 'true') {
          $vuetify.theme.dark = true
        } else {
          $vuetify.theme.dark = false
        }
      }
    },
    isDark() {
      return $vuetify.theme.dark
    },
    getAceLogo() {
      return `/ace_logo_${$vuetify.theme.dark ? 'dark' : 'light'}.svg`
    },
    getLogo() {
      return `/fmg_aus_logo_${$vuetify.theme.dark ? 'dark' : 'light'}.svg`
    },
    getClass() {
      return `theme--${$vuetify.theme.dark ? 'dark' : 'light'}`
    },
    toggle() {
      $vuetify.theme.dark = !$vuetify.theme.dark

      localStorage.setItem('dark_theme', $vuetify.theme.dark.toString())
    },
  })
}
