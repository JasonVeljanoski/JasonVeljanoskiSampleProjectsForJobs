export default ({ app }, inject) => {
  inject('document', {
    download(path) {
      return `${app.$axios.defaults.baseURL}/document/${path}`
    },
  })
}
