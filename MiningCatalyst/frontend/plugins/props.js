const generic = {
  outlined: true,
  dense: true,
  'hide-details': 'auto',
  solo: true,
  flat: true,
  'menu-props': { top: false, offsetY: true },
}

const btn = {
  elevation: 0,
  outlined: false,
  color: 'primary',
}

const readonly_input = {
  dense: true,
  // 'hide-details': 'none',
  solo: true,
  flat: true,
  readonly: true,
  style: 'margin-left: -12px',
}

const number = {
  ...generic,
  type: 'number',
  step: 'any',
}
const currency = {
  ...number,
  min: 0,
  'prepend-inner-icon': 'mdi-currency-usd',
}

const table = {
  ...generic,
  outlined: false,
  'background-color': 'transparent',
  class: 'simple-input',
}

const table_number = {
  ...number,
  ...table,
}

const table_currency = {
  ...currency,
  ...table,
}

export default ({ app, store }, inject) => {
  inject('bind', {
    generic,
    btn,
    readonly_input,
    number,
    currency,

    table,
    table_number,
    table_currency,
  })
}
