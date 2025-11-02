export const state = () => ({
  settings: {},
})

export const mutations = {
  settings(state, val) {
    state.settings = val
  },
}

export const actions = {
  load({ commit }) {
    return this.$axios.$get('/settings/frontend').then((res) => {
      commit('settings', res)
    })
  },
}

export const getters = {
  settings: (state) => state.settings,
}
