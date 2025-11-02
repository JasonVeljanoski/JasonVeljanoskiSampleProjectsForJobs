export const state = () => ({
  loading: false,
});

export const actions = {
  loadingOn({ commit }) {
    commit("LOADING_ON");
  },
  loadingOff({ commit }) {
    commit("LOADING_OFF");
  },
};

export const mutations = {
  LOADING_ON(state) {
    state.loading = true;
  },
  LOADING_OFF(state) {
    state.loading = false;
  },
};

export const getters = {
  getLoading(state) {
    return state.loading;
  },
};
