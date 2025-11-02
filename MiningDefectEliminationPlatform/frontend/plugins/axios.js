export default ({ $axios, redirect, app, $auth }, inject) => {
  $axios.onError((error, a, b) => {
    let show_error = !error.config.headers["hide-error"];

    if (show_error) {
      // Dont show error if its the Nuxt Auth user URL
      let user_url = app.$auth.strategies?.social?.options?.endpoints?.userInfo;
      if (!user_url || user_url != error.config.url) {
        app.$snackbar.axiosError(error);
      }
    }

    throw error;
  });

  let X = (x) => {
    x ||= {};
    x["headers"] ||= {};
    x["headers"]["hide-error"] = true;

    return x;
  };

  $axios.$$get = (a, b, c, d) => $axios.$get(a, X(b), c, d);
  $axios.$$post = (a, b, c, d) => $axios.$post(a, b, X(c), d);
  $axios.$$put = (a, b, c, d) => $axios.$put(a, b, X(c), d);
  $axios.$$patch = (a, b, c, d) => $axios.$patch(a, b, X(c), d);
  $axios.$$delete = (a, b, c, d) => $axios.$delete(a, X(b), c, d);
};
