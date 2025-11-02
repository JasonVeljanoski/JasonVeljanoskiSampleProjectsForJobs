import Vue from 'vue'

export default ({ $vuetify, app }, inject) => {
  inject('theme', {
    init() {
      const theme = localStorage.getItem('dark_theme')

      setTimeout(() => {
        $vuetify.theme.dark = theme && theme == 'true'
      }, 10)
    },
    isDark() {
      return $vuetify.theme.dark
    },
    getLogo() {
      return `/fmg_aus_logo_${$vuetify.theme.dark ? 'dark' : 'light'}.svg`
    },
    getFMGLogoSmall() {
      return `/fmg_logo_${$vuetify.theme.dark ? 'dark' : 'light'}.svg`
    },
    getFMGLogo() {
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
