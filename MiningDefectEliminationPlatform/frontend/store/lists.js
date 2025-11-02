export const state = () => ({
  function_locations: [],
  damage_codes: [],
  cause_codes: [],
  sites: [],
  departments: [],
  equipments: [],
  object_types: [],
  object_parts: [],
  email_lists: [],
});

export const actions = {
  fetchFunctionLocations({ commit }) {
    this.$axios
      .$get("/incident/function_locations")
      .then((res) => {
        commit("SET_FUNCTION_LOCATIONS", res);
      })
      .catch((err) => {
        console.error(err);
      });
  },
  fetchDamageCodes({ commit }) {
    this.$axios
      .$get("/incident/damage_codes")
      .then((res) => {
        commit("SET_DAMAGE_CODES", res);
      })
      .catch((err) => {
        console.error(err);
      });
  },
  fetchCauseCodes({ commit }) {
    this.$axios
      .$get("/incident/cause_codes")
      .then((res) => {
        commit("SET_CAUSE_CODES", res);
      })
      .catch((err) => {
        console.error(err);
      });
  },
  fetchSites({ commit }) {
    this.$axios
      .$get("/incident/sites")
      .then((res) => {
        commit("SET_SITES", res);
      })
      .catch((err) => {
        console.error(err);
      });
  },
  fetchDepartments({ commit }) {
    this.$axios
      .$get("/incident/departments")
      .then((res) => {
        commit("SET_DEPARTMENTS", res);
      })
      .catch((err) => {
        console.error(err);
      });
  },
  fetchEquipments({ commit }) {
    this.$axios
      .$get("/incident/equipments")
      .then((res) => {
        commit("SET_EQUIPMENTS", res);
      })
      .catch((err) => {
        console.error(err);
      });
  },
  fetchObjectTypes({ commit }) {
    this.$axios
      .$get("/incident/object_types")
      .then((res) => {
        commit("SET_OBJECT_TYPES", res);
      })
      .catch((err) => {
        console.error(err);
      });
  },
  fetchObjectParts({ commit }) {
    this.$axios
      .$get("/incident/object_parts")
      .then((res) => {
        commit("SET_OBJECT_PARTS", res);
      })
      .catch((err) => {
        console.error(err);
      });
  },
  fetchEmailLists({ commit }) {
    this.$axios
      .$get("/static/email_distribution_list")
      .then((res) => {
        commit("SET_EMAIL_LISTS", res);
      })
      .catch((err) => {
        console.error(err);
      });
  },
};

export const mutations = {
  SET_FUNCTION_LOCATIONS(state, payload) {
    state.function_locations = payload;
  },
  SET_DAMAGE_CODES(state, payload) {
    state.damage_codes = payload;
  },
  SET_CAUSE_CODES(state, payload) {
    state.cause_codes = payload;
  },
  SET_SITES(state, payload) {
    state.sites = payload;
  },
  SET_DEPARTMENTS(state, payload) {
    state.departments = payload;
  },
  SET_EQUIPMENTS(state, payload) {
    state.equipments = payload;
  },
  SET_OBJECT_TYPES(state, payload) {
    state.object_types = payload;
  },
  SET_OBJECT_PARTS(state, payload) {
    state.object_parts = payload;
  },
  SET_EMAIL_LISTS(state, payload) {
    state.email_lists = payload;
  },
};

export const getters = {
  getFunctionLocations: (state) => state.function_locations,
  getDamageCodes: (state) => state.damage_codes,
  getCauseCodes: (state) => state.cause_codes,
  getSites: (state) => state.sites,
  getDepartments: (state) => state.departments,
  getEquipments: (state) => state.equipments,
  getObjectTypes: (state) => state.object_types,
  getObjectParts: (state) => state.object_parts,
  getEmailLists: (state) => state.email_lists,
};
