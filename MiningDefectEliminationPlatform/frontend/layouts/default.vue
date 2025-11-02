<template>
  <v-app>
    <navbar />

    <v-main>
      <v-container v-if="loading" fill-height fluid>
        <v-row justify="center">
          <v-col align="center">
            <v-progress-circular :size="120" :width="10" indeterminate color="primary" />
          </v-col>
        </v-row>
      </v-container>
      <v-container v-else class="center-piece" fluid :style="center_style">
        <nuxt />
      </v-container>
    </v-main>

    <!-- GLOBAL COMPONENTS -->
    <e-snackbar />
  </v-app>
</template>

<script>
import Navbar from "@/components/Navigation/Navbar";

export default {
  components: {
    Navbar,
  },
  data() {
    return {
      loading: false,
    };
  },
  computed: {
    center_style() {
      return {
        height: `calc(100vh - ${this.$vuetify.application.top}px)`,
      };
    },
  },
  created() {
    this.loading = true;
    this.$theme.init();

    if (this.$auth.loggedIn) {
      this.$perms.init();
      this.$socket.init();

      this.$store
        .dispatch("user/fetchUsers")
        .then(() => {
          this.$nextTick(() => {
            this.loading = false;
          });
        })
        .catch((err) => console.error(err));

      // ------------------

      this.$store.dispatch("lists/fetchFunctionLocations").catch((err) => console.error(err));
      this.$store.dispatch("lists/fetchDamageCodes").catch((err) => console.error(err));
      this.$store.dispatch("lists/fetchCauseCodes").catch((err) => console.error(err));
      this.$store.dispatch("lists/fetchSites").catch((err) => console.error(err));
      this.$store.dispatch("lists/fetchDepartments").catch((err) => console.error(err));
      this.$store.dispatch("lists/fetchEquipments").catch((err) => console.error(err));
      this.$store.dispatch("lists/fetchObjectTypes").catch((err) => console.error(err));
      this.$store.dispatch("lists/fetchObjectParts").catch((err) => console.error(err));
      this.$store.dispatch("lists/fetchEmailLists").catch((err) => console.error(err));
    } else {
      this.$perms.destroy();
      this.loading = false;
    }
  },
  mounted() {
    // Why use setTimeout? $vutify bug workaround
    // https://github.com/vuetifyjs/vuetify/issues/13378
    setTimeout(() => this.$theme.init(), 1);
  },
};
</script>

<style scoped lang="scss">
.main-wrapper {
  height: calc(100vh - 64px);
  > * {
    // outline: solid red 2px !important;
    overflow: hidden;
  }

  // margin-top: calc(46px + 82px);
  overflow-y: auto;

  .theme--light & {
    background: #f8f8f8;
  }
}

.center-piece {
  overflow-y: auto;
}
</style>
