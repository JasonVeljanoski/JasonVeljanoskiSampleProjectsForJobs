let item_id = 1;

export const state = () => ({
  items: [],
});

export const getters = {
  items(state) {
    return state.items;
  },
};

export const mutations = {
  add(state, { message, type, duration }) {
    let item = {
      id: item_id++,
      message: message,
      type: type || "success",
    };

    duration ||= -1;

    if (duration == -1) {
      item.duration = -1;
    } else {
      item.duration = duration * 1000;
    }

    state.items.push(item);
  },
  remove(state, item) {
    let index = state.items.findIndex((x) => x.id === item.id);
    if (index > -1) {
      state.items.splice(index, 1);
    }
  },
};
