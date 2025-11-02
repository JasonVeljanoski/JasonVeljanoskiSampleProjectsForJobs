<template>
  <v-app>
    <navbar />
    <side-bar />

    <v-main :class="{ 'has-background': loading || show_background }">
      <v-container v-if="!is_ready" fill-height fluid>
        <v-row justify="center">
          <v-col align="center">
            <v-progress-circular indeterminate :size="120" :width="10" color="white" />
          </v-col>
        </v-row>
      </v-container>
      <v-container v-else class="center-piece" fluid :style="center_style">
        <nuxt />
      </v-container>
    </v-main>

    <e-snackbar />
  </v-app>
</template>

<script>
import { mapGetters } from 'vuex'
import Navbar from '@/components/navigation/Navbar.vue'
import SideBar from '~/components/navigation/SideBar.vue'

export default {
  components: { Navbar, SideBar },
  data() {
    return {
      loading: true,
      tab: null,
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
    show_background() {
      return ['index', 'initiatives', 'initiative'].includes(this.$route.name)
    },
    is_ready() {
      return !this.loading // add more in future...
    },
  },
  created() {
    this.loading = true
    this.$theme.init()

    if (this.$auth.loggedIn) {
      this.$perms.init()

      // ------------------

      Promise.all([this.$settings.load(), this.$lists.importAllLists(), this.$enums.importAllEnums()])
        .then(() => (this.loading = false))
        .catch((error) => console.error(error))
    } else {
      this.$perms.destroy()
      this.loading = false
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
.center-piece {
  overflow-y: auto;
}

.theme--light.v-application {
  background: #f8f8f8;
}
.v-main.has-background {
  background-image: url('~/static/Home.jpg');
  background-position: center top;
  background-size: cover;

  .theme--dark &::before {
    @extend %pseudo;
    background: rgba(black, 0.3);
  }
}
</style>
