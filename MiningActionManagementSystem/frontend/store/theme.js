export const state = () => ({
  is_mobile: false,
})

export const actions = {}

export const mutations = {
  SET_IS_MOBILE(state, payload) {
    state.is_mobile = payload
  },
}

export const getters = {
  getIsMobile(state) {
    return state.is_mobile
  },
}
