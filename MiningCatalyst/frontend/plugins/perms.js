export default ({ app, store }, inject) => {
  inject('perms', {
    is_super: false,
    is_admin: false,
    is_writer: false,

    // --------------

    init() {
      const user = app.$auth.user

      this.is_super = user.access === 3
      this.is_admin = user.access >= 2
      this.is_writer = user.access >= 1
    },
    destroy() {
      this.is_super = false
      this.is_admin = false
      this.is_writer = false
    },
  })
}
