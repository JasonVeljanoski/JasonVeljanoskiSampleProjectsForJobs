<template>
  <div />
</template>

<script>
export default {
  layout: "simple",
  created() {
    this.info = this.$route.query;

    if (this.$auth.loggedIn) {
      this.$router.push({ path: "/", param: {} });
      return;
    }

    if (window.location.host == "localhost") {
      this.$axios.$get("/user/login_dev").then((res) => {
        let token = `${res.token_type} ${res.access_token}`;
        this.$auth.strategy.token.set(token);
        this.$auth.fetchUser();
      });
    } else if (this.$route.query && this.$route.query.code) {
      this.$axios
        .$get("/user/login", { params: { code: this.$route.query.code } })
        .then((res) => {
          let token = `${res.token_type} ${res.access_token}`;
          this.$auth.strategy.token.set(token);
          this.$router.replace({ query: null });
          this.$auth.fetchUser();
        });
    } else {
      this.$auth.loginWith("social");
    }
  },
};
</script>

<style></style>
