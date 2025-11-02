export default ({ app, store }, inject) => {
  inject("socket", {
    init() {
      store.dispatch("socket/init");
    },
    destroy() {
      store.dispatch("socket/destroy");
    },
    removeNotification(notification) {
      store.dispatch("socket/removeNotification", notification);
    },
    removeAllNotifications() {
      store.dispatch("socket/removeAllNotifications");
    },
  });
};
