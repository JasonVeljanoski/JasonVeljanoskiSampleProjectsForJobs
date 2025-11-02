<template>
  <v-app>
    <template v-if="$auth.loggedIn">
      <navbar v-if="!is_mobile" />
      <navbar-mobile v-else />
    </template>

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

    <e-snackbar />
    <news-update-dialog />
  </v-app>
</template>

<script>
import { mapGetters } from 'vuex'
import Navbar from '@/components/Navigation/Navbar.vue'
import NavbarMobile from '@/components/Navigation/NavbarMobile.vue'
import NewsUpdateDialog from '@/components/Dialogs/NewsUpdateDialog.vue'

export default {
  components: { Navbar, NavbarMobile, NewsUpdateDialog },
  data() {
    return {
      loading: false,
      drawer: true,
    }
  },
  computed: {
    ...mapGetters({
      is_mobile: 'theme/getIsMobile',
    }),

    center_style() {
      return {
        height: `calc(100vh - ${this.$vuetify.application.top}px)`,
      }
    },
  },
  created() {
    this.loading = true
    this.$theme.init()

    if (this.$auth.loggedIn) {
      this.$perms.init()

      // ------------------

      // to run with loading
      this.$store
        .dispatch('user/fetchUsers')
        .then(() => {
          // must wait for users to load before app can run. Other tasks can run in background
          this.$nextTick(() => {
            this.loading = false
          })
        })
        .catch((err) => console.error(err))

      // to run in background
      this.$store.dispatch('lists/fetchFunctionalLocsPermutations').catch((err) => console.error(err))
      this.$store.dispatch('lists/fetchWorkcenters').catch((err) => console.error(err))
    }
  },
  mounted() {
    this.onResize()
    window.addEventListener('resize', this.onResize, { passive: true })
  },
  beforeDestroy() {
    this.$perms.destroy()

    // ------------------

    if (typeof window === 'undefined') return
    window.removeEventListener('resize', this.onResize, { passive: true })
  },
  methods: {
    onResize() {
      this.$store.commit('theme/SET_IS_MOBILE', window.innerWidth < 1180)
    },
  },
}
</script>

<style lang="scss" scoped>
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
