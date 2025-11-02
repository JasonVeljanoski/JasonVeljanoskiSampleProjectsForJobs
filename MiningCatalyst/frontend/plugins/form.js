export default ({ app, store }, inject) => {
  inject('form', {
    length(v, len) {
      return (v || '').length <= len || `Invalid character length, required ${len}`
    },
    required(v) {
      return !!v || 'This field is required'
    },
    conditional_required(v, condition_result) {
      if (condition_result) return !!v || 'This field is required'
    },
    arr_len_lim(v, lim) {
      return v.length <= lim || `Invalid quantity, required at most ${lim}`
    },
    arr_non_empty(v) {
      return (v && v.length > 0) || 'At least one is required'
    },
    arr_fixed_len(v, lim) {
      return v.length == lim || `Invalid quantity, required ${lim}`
    },
    date_cannot_be_in_future(v) {
      return v <= new Date() || 'Date cannot be in the future'
    },
    date_cannot_be_in_past(v) {
      return v > new Date() || 'Date cannot be in the past'
    },

    // specific to this project
    values_must_be_different(v, v2, message = 'Values must be different') {
      // v and v2 must be different and not null
      return (!!v && v != v2) || message
    },
  })
}
