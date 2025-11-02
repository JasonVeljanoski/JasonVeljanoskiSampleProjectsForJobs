<template>
  <e-dialog v-if="news" :dialog="dialog" title="Latest ACE Updates">
    <template #card:body>
      <div v-if="!loading" class="html_render mt-4" v-html="news?.content ? news.content : 'No Content'" />
    </template>

    <template #card:footer>
      <v-spacer />
      <v-checkbox label="Don't show again" hide-details class="mx-4 my-2" @change="dontShowAgain" />
      <v-btn v-bind="$bind.btn" @click="dialog = !dialog"> OK </v-btn>
    </template>
  </e-dialog>
</template>

<script>
export default {
  components: {},
  data() {
    return {
      dialog: false,
      news: null,
      loading: false,
    }
  },
  computed: {},
  mounted() {
    this.getLatestUpdateNews()
  },
  methods: {
    // ------------------------------
    // DIALOG HANDLERS
    // ------------------------------
    getLatestUpdateNews() {
      this.loading = true
      this.$axios.$get('/log/latest_update').then((res) => {
        this.news = res
        this.loading = false

        // ---

        this.dialog = this.news.active && !this.$auth.user.dont_show_news_again
      })
    },
    dontShowAgain(e) {
      this.$axios
        .$patch('/log/update_history/dont_show_again', null, {
          params: {
            flag: e,
          },
        })
        .catch((err) => {
          console.error(err)
        })
    },
  },
}
</script>

<style lang="scss" scoped></style>
