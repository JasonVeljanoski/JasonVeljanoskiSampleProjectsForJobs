export const state = () => ({
  functional_locs_permutations: [],
  workcenters: [],
})

export const actions = {
  fetchFunctionalLocsPermutations({ commit }) {
    this.$axios
      .$get('/static/functional_location_permutations')
      .then((res) => {
        return commit('SET_FUNCTIONAL_LOCS_PERMUTATIONS', res)
      })
      .catch((err) => console.error(err))
  },
  fetchWorkcenters({ commit }) {
    this.$axios
      .$get('/static/workcenters')
      .then((res) => {
        return commit('SET_WORKCENTERS', res)
      })
      .catch((err) => console.error(err))
  },
}

export const mutations = {
  SET_FUNCTIONAL_LOCS_PERMUTATIONS(state, payload) {
    state.functional_locs_permutations = payload
  },
  SET_WORKCENTERS(state, payload) {
    state.workcenters = payload
  },
}

export const getters = {
  getFunctionalLocsPermutations(state) {
    return state.functional_locs_permutations
  },
  getWorkcenters(state) {
    return state.workcenters
  },
}
