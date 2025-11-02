const base = {}

const freetext = {
  ...base,
  outlined: true,
  dense: true,
  hideDetails: 'auto',
  color: 'primary',
  rows: 3,
}

const select = {
  ...base,
  clearable: true,
  outlined: true,
  dense: true,
  hideDetails: 'auto',
}

const btn = {
  ...base,
  elevation: 0,
  outlined: false,
  color: 'primary',
}

const generic = {
  outlined: true,
  dense: true,
  // 'hide-details': 'true',
  solo: true,
  flat: true,
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
    freetext,
    btn,
    select,
    // ---
    generic,
    number,
    currency,
    table,
    table_number,
    table_currency,
  })
}
