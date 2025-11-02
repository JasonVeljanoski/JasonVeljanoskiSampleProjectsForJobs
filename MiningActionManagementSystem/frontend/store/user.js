export const state = () => ({
  users: [],
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
}

export const mutations = {
  SET_USERS(state, payload) {
    state.users = payload
  },
}

export const getters = {
  getUsers(state) {
    return state.users
  },
}
