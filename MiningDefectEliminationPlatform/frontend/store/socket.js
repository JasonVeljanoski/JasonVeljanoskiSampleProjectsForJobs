export const state = () => ({
  socket: null,
  actions: [],
  investigations: [],
  notifications: [],
});

let timeout = 250;

// -----------------------------------------------
// GETTERS
export const getters = {
  actions(state) {
    return state.actions;
  },
  investigations(state) {
    return state.investigations;
  },
  notifications(state) {
    return state.notifications;
  },
};

// -----------------------------------------------
// MUTATIONS
export const mutations = {
  // GENERAL
  socket(state, socket) {
    state.socket = socket;
  },
  destroy(state) {
    state.actions = [];
    state.notifications = [];

    if (state.socket) {
      // Remove the onclose event to stop auto reconnect
      state.socket.onclose = null;
      state.socket.close();
      state.socket = null;
    }
  },

  // -----------------------------------------------

  // NOTIFICATIONS
  appendToNotifications(state, toAppend) {
    if (!Array.isArray(toAppend)) {
      toAppend = [toAppend];
    }

    for (let item of toAppend) {
      if (!state.notifications.find((x) => x.id == item.id)) {
        state.notifications.push(item);
      }
    }
  },
  removeNotification(state, notification) {
    state.notifications = state.notifications.filter((n) => n.id !== notification.id);
  },
  removeAllNotifications(state) {
    state.notifications = [];
  },

  // -----------------------------------------------

  // INVESTIGATIONS AND ACTIONS
  appendToActions(state, toAppend) {
    if (!Array.isArray(toAppend)) toAppend = [toAppend];
    state.actions = state.actions.filter((x) => x); // ! remove nulls/undefined to lazily fix bug

    for (let item of toAppend) {
      // CONSTRUCT DATA
      let id = null;
      let data = null;

      // if, data comes from socket
      if ("data" in item && "id" in item) {
        id = item.id;
        data = item.data;
      }
      // else, data comes from route /investigation/user_open
      else {
        id = item.id;
        data = item;
      }

      // ADD, REMOVE, REPLACE
      const idx = state.actions.findIndex((x) => x.id == id);

      // add
      if (idx == -1) {
        if (data && !data.is_archived && !data.is_deleted && data.status != 3) state.actions.push(data);
      } else {
        // remove
        state.actions.splice(idx, 1);

        // update
        if (data && !data.is_archived && !data.is_deleted && data.status != 3) state.actions.push(data);
      }
    }
  },
  appendToInvestigations(state, toAppend) {
    if (!Array.isArray(toAppend)) toAppend = [toAppend];
    state.investigations = state.investigations.filter((x) => x); // ! remove nulls/undefined to lazily fix bug

    for (let item of toAppend) {
      // CONSTRUCT DATA
      let id = null;
      let data = null;

      // if, data comes from socket
      if ("data" in item && "id" in item) {
        id = item.id;
        data = item.data;
      }
      // else, data comes from route /investigation/user_open
      else {
        id = item.id;
        data = item;
      }

      // ADD, REMOVE, REPLACE
      const idx = state.investigations.findIndex((x) => x.id == id);

      // add
      if (idx == -1) {
        if (data && !data.is_archived && data.status != 3) state.investigations.push(data);
      } else {
        // remove
        state.investigations.splice(idx, 1);

        // update
        if (data && !data.is_archived && data.status != 3) state.investigations.push(data);
      }
    }
  },

  // -----------------------------------------------

  // RESET
  resetAll(state) {
    state.notifications = [];
    state.actions = [];
    state.investigations = [];

    this.$axios.$get("/notification/all").then((res) => {
      this.commit("socket/appendToNotifications", res);
    });

    this.$axios.$get("/action/user_open").then((res) => {
      this.commit("socket/appendToActions", res);
    });

    this.$axios.$get("/investigation/user_open").then((res) => {
      this.commit("socket/appendToInvestigations", res);
    });
  },
};

// -----------------------------------------------
// ACTIONS
export const actions = {
  // INIT
  init({ commit, state, dispatch }) {
    try {
      commit("destroy");

      let token = this.$utils.getAuthToken();

      const url = window.location.origin.replace("http", "ws");
      const path = `${url}/api/ws/global?token=${token}`;

      const socket = new WebSocket(path);

      // --------------------------------------------------------

      // ON OPEN
      socket.onopen = (event) => {
        timeout = 250;

        // NOTIFICATIONS
        this.$axios.$get("/notification/all").then((res) => {
          commit("appendToNotifications", res);
        });

        // ACTIONS AND INVESTIGATIONS
        this.$axios.$get("/action/user_open").then((res) => {
          commit("appendToActions", res);
        });
        this.$axios.$get("/investigation/user_open").then((res) => {
          commit("appendToInvestigations", res);
        });
      };

      // --------------------------------------------------------

      // ON CLOSE
      socket.onclose = (event) => {
        console.error("Websocket lost");
        setTimeout(() => {
          if (timeout < 50000) {
            dispatch("init");
          } else {
            commit("destroy");
            alert("The server seems to be down");
          }
        }, Math.min(10000, (timeout += timeout)));
      };

      // --------------------------------------------------------

      // ON MESSAGE
      socket.onmessage = (event) => {
        if (event.data == "NO") {
          commit("destroy");
          alert("Authentication error occurred. Page is needing to be reloaded to continue.");
          location.reload();
        } else {
          let MAPPING = {
            // NOTIFICATION
            NOTIFICATION: (x) => {
              // fix tags
              if (typeof x.tags === "string") {
                let tags = x.tags.slice(1, -1).split(",");

                let tag_arr = [];
                for (let tag of tags) tag_arr.push(tag.slice(1, -1).replace("'", "").replace('"', ""));
                x.tags = tag_arr;
              }
              // fix type
              if (typeof x.type === "string") {
                let type = x.type;
                if (type == this.$enums.notification_types[1]) x.type = 1;
                else if (type == this.$enums.notification_types[2]) x.type = 2;
                else if (type == this.$enums.notification_types[3]) x.type = 3;
              }
              commit("appendToNotifications", x);
            },

            // ----------------------------------------------

            // INVESTIGATION AND ACTION
            INVESTIGATION: (x) => {
              let data = x.data;
              if (data) {
                data.created = this.$format.initDate(data.created);
                data.updated = this.$format.initDate(data.updated);
                data.event_date = this.$format.initDate(data.event_date);
                data.date_due = this.$format.initDate(data.date_due);
                data.date_closed = this.$format.initDate(data.date_closed);
                data.priority = this.$format.capitaliseWords(data.priority);
              }
              commit("appendToInvestigations", x);
            },
            ACTION: (x) => {
              let data = x.data;
              if (data) {
                data.created = this.$format.initDate(data.created);
                data.updated = this.$format.initDate(data.updated);
                data.date_due = this.$format.initDate(data.date_due);
                data.date_closed = this.$format.initDate(data.date_closed);
                data.priority = this.$format.capitaliseWords(data.priority);
              }
              commit("appendToActions", x);
            },
          };

          // ----------------------------------------------

          // SNACKBAR
          const info = JSON.parse(event.data);

          if (info.group in MAPPING) {
            MAPPING[info.group](info.data);

            if (info.group === "NOTIFICATION") {
              // -------------------------------------------
              let build_notification_html = (info) => {
                let X = (a) =>
                  a
                    .toString()
                    .replace(/</g, "&lt;")
                    .replace(/>/g, "&gt;")
                    .replace(/'/g, "&#39;")
                    .replace(/"/g, "&#34;");

                let title = `<h4>${X(info.data.title)}</h4>`;
                let message = X(info.data.message) + "\n";
                let tag_str = "";

                let tags = info.data.tags;
                for (let i = 0; i < tags.length; i++) {
                  let sanatised = "<b>" + tags[i] + "</b>";
                  if (i < tags.length - 1) tag_str += `${sanatised} - `;
                  else tag_str += sanatised;
                }
                tag_str = `<small>${tag_str}</small>`;

                return title + message + tag_str;
              };
              // -------------------------------------------
              let body = build_notification_html(info);
              let type = this.$enums.notification_types[info.data.type] || "success";

              this.$snackbar.add(body, type);
            }
          } else {
            console.warn("Unknown group", info.group, info.data);
          }
        }
      };

      // ----------------------------------------------

      // ON ERROR
      socket.onerror = (error) => {
        console.error("Socket error", error);
      };

      commit("socket", socket);
    } catch (err) {
      console.error(err);
    }
  },

  // -----------------------------------------------

  // REMOVE
  removeNotification({ commit }, notification) {
    commit("removeNotification", notification);
  },
  removeAllNotifications({ commit }) {
    commit("removeAllNotifications");
  },
  destroy({ commit, state }) {
    commit("destroy");
  },
};
