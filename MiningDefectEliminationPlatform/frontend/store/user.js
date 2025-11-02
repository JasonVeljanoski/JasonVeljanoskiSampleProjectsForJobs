export const state = () => ({
  users: [],
  is_my_investigation: false,
});

export const actions = {
  fetchUsers({ commit }) {
    return this.$axios
      .$get("/user/all")
      .then((res) => {
        commit("SET_USERS", res);
      })
      .catch((err) => {
        console.error(err);
      });
  },
  changeIsMyInvestigation({ commit }, flag) {
    commit("SET_IS_MY_INVESTIGATION", flag);
  },
};

export const mutations = {
  SET_USERS(state, payload) {
    // add filter_name (for expressive search)
    for (let item of payload)
      item["filter_name"] = item.name + " " + item.email;
    state.users = payload;
  },
  SET_IS_MY_INVESTIGATION(state, payload) {
    state.is_my_investigation = payload;
  },
};

export const getters = {
  getUsers(state) {
    return state.users;
  },
  getIsMyInvestigation(state) {
    return state.is_my_investigation;
  },
};
