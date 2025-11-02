const base = {};

const textarea = {
  ...base,
  rows: 3,
  color: "primary",
  outlined: true,
  dense: true,
  hideDetails: "auto",
};

const textfield = {
  ...base,
  color: "primary",
  outlined: true,
  dense: true,
  hideDetails: "auto",
};

const card = {
  ...base,
  elevation: 0,
  outlined: true,
};

const btn = {
  ...base,
  elevation: 0,
  outlined: false,
  color: "primary",
};

const simple_btn = {
  ...base,
  elevation: 0,
  outlined: true,
  color: "primary",
  text: true,
};

const dialog = {
  ...base,
};

const select = {
  ...base,
  outlined: true,
  dense: true,
  hideDetails: "auto",
};

const date_picker = {
  ...base,
  headerColor: "primary",
  scrollable: true,
  light: true,
};

const range_slider = {
  ...base,
  color: "primary",
  trackColor: "accent",
};

const auto_complete = {
  ...base,
  hideDetails: true,
  hideDetails: "auto",
};

const stepper = {
  ...base,
  outlined: true,
  elevation: 0,
};

const snackbar = {
  ...base,
  elevation: 0,
  dark: true,
  vertical: true,
};

export default ({ app, store }, inject) => {
  inject("bind", {
    textarea,
    textfield,
    card,
    btn,
    simple_btn,
    dialog,
    select,
    date_picker,
    range_slider,
    auto_complete,
    stepper,
    snackbar,
  });
};
