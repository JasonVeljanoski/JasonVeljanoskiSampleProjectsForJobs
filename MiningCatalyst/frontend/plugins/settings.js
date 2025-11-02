export default ({ app, store }, inject) => {
  inject('settings', {
    load() {
      return store.dispatch('settings/load')
    },
    showGreenBar() {
      return getSettings('green_nav_bar', false)
    },
  })
  function getSettings(key, default_value) {
    return store.state.settings.settings?.[key] ?? default_value
  }
}
