export const state = () => ({
  priority: [],
  status: [],
  triggers: [],
  primary_drivers: [],
  secondary_drivers: [],
  cost_benefit_categories: [],
  benefit_frequencies: [],
})

export const actions = {
  fetchPriorities({ commit }) {
    return this.$axios
      .$get('/enums/priority/all')
      .then((res) => {
        return commit('SET_PRIORITIES', res)
      })
      .catch((err) => {
        console.error(err)
      })
  },
  fetchStatuses({ commit }) {
    return this.$axios
      .$get('/enums/status/all')
      .then((res) => {
        return commit('SET_STATUS', res)
      })
      .catch((err) => {
        console.error(err)
      })
  },
  fetchTriggers({ commit }) {
    return this.$axios
      .$get('/enums/trigger/all')
      .then((res) => {
        return commit('SET_TRIGGERS', res)
      })
      .catch((err) => {
        console.error(err)
      })
  },
  fetchPrimaryDrivers({ commit }) {
    return this.$axios
      .$get('/enums/primary_driver/all')
      .then((res) => {
        return commit('SET_PRIMARY_DRIVERS', res)
      })
      .catch((err) => {
        console.error(err)
      })
  },
  fetchSecondaryDrivers({ commit }) {
    return this.$axios
      .$get('/enums/secondary_driver/all')
      .then((res) => {
        return commit('SET_SECONDARY_DRIVERS', res)
      })
      .catch((err) => {
        console.error(err)
      })
  },
  fetchCostBenefitCategories({ commit }) {
    return this.$axios
      .$get('/enums/cost_benefit_category/all')
      .then((res) => {
        return commit('SET_COST_BENEFIT_CATEGORIES', res)
      })
      .catch((err) => {
        console.error(err)
      })
  },
  fetchBenefitFrequencies({ commit }) {
    return this.$axios
      .$get('/enums/benefit_frequency/all')
      .then((res) => {
        return commit('SET_BENEFIT_FREQUENCIES', res)
      })
      .catch((err) => {
        console.error(err)
      })
  },
}

export const mutations = {
  SET_PRIORITIES: (state, payload) => (state.priority = payload),
  SET_STATUS: (state, payload) => (state.status = payload),
  SET_TRIGGERS: (state, payload) => (state.triggers = payload),
  SET_PRIMARY_DRIVERS: (state, payload) => (state.primary_drivers = payload),
  SET_SECONDARY_DRIVERS: (state, payload) => (state.secondary_drivers = payload),
  SET_COST_BENEFIT_CATEGORIES: (state, payload) => (state.cost_benefit_categories = payload),
  SET_BENEFIT_FREQUENCIES: (state, payload) => (state.benefit_frequencies = payload),
}

export const getters = {
  getPriorities: (state) => state.priority,
  getStatuses: (state) => state.status,
  getTriggers: (state) => state.triggers,
  getPrimaryDrivers: (state) => state.primary_drivers,
  getSecondaryDrivers: (state) => state.secondary_drivers,
  getCostBenefitCategories: (state) => state.cost_benefit_categories,
  getBenefitFrequencies: (state) => state.benefit_frequencies,
}
