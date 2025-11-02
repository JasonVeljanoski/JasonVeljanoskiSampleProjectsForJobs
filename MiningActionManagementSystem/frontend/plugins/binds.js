const generic = {
  outlined: true,
  'hide-details': 'true',
  solo: true,
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
    number,
    currency,
    table,
    table_number,
    table_currency,
  })
}
