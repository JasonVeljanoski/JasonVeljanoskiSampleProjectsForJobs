export default ({ app, store }, inject) => {
  inject("perms", {
    is_admin: false,
    is_writer: false,

    init() {
      let user = app.$auth.user;

      this.is_admin = user.access === 3;
      this.is_writer = user.access >= 2;
    },
    destroy() {
      this.is_admin = false;
      this.is_writer = false;
    },
  });
};
