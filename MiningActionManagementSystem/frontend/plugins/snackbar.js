export default ({ app, store }, inject) => {
  inject('snackbar', {
    add(message, type = 'success', duration = 5) {
      store.commit('snackbar/add', { message, type, duration })
    },
    axiosError(error) {
      const message = error?.response?.data?.message || 'Unknown Error Occurred'
      this.add(message, 'error')
    },
  })
}
