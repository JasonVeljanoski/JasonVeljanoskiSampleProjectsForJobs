export const state = () => ({
  users: [],
  equipments: [],
  organisational_units: [],
})

export const actions = {
  fetchUsers({ commit }) {
    return this.$axios
      .$get('/user/all')
      .then((res) => {
        return commit('SET_USERS', res)
      })
      .catch((err) => {
        console.error(err)
      })
  },

  fetchEquipments({ commit }) {
    this.$axios
      .$get('/lists/equipments')
      .then((res) => {
        return commit('SET_EQUIPMENTS', res)
      })
      .catch((err) => console.error(err))
  },

  fetchOrganisationalUnits({ commit }) {
    this.$axios
      .$get('/lists/organisational_units')
      .then((res) => {
        return commit('SET_ORGANISATIONAL_UNITS', res)
      })
      .catch((err) => console.error(err))
  },
}

export const mutations = {
  SET_USERS: (state, payload) => (state.users = payload),
  SET_EQUIPMENTS: (state, payload) => (state.equipments = payload),
  SET_ORGANISATIONAL_UNITS: (state, payload) => (state.organisational_units = payload),
}

export const getters = {
  getUsers: (state) => state.users,
  getEquipments: (state) => state.equipments,
  getOrganisationalUnits: (state) => state.organisational_units,
}
