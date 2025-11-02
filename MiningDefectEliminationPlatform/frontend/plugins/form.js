export default ({ app, store }, inject) => {
  inject("form", {
    length(v, len) {
      return (v || "").length <= len || `Invalid character length, required ${len}`;
    },
    required(v) {
      return !!v || "This field is required";
    },
    conditional_required(v, condition_result) {
      if (condition_result) return !!v || "This field is required";
    },
    arr_len_lim(v, lim) {
      return v.length <= lim || `Invalid quantity, required at most ${lim}`;
    },
    arr_non_empty(v) {
      return v.length > 0 || "At least one is required";
    },
    arr_fixed_len(v, lim) {
      return v.length == lim || `Invalid quantity, required ${lim}`;
    },
    file_size_lim_MB(v, lim) {
      const lim_bytes = lim * 1024 * 1024;
      let total_size = 0;
      for (const file of v) total_size += +file.size;
      return total_size < lim_bytes || `Invalid size, required at most ${lim}MB`;
    },
    date_cannot_be_in_future(v) {
      return v <= new Date() || "Date cannot be in the future";
    },
    date_cannot_be_in_future(v) {
      return v <= new Date() || "Date cannot be in the future";
    },
  });
};
