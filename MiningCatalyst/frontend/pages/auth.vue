<template>
  <div></div>
</template>

<script>
import { useApiRouter } from '~/client'

const { UserRouter } = useApiRouter()

export default {
  layout: 'simple',
  head() {
    return {
      title: 'Authentication',
    }
  },
  mounted() {
    // checks if logged in
    if (this.$auth?.loggedIn) {
      this.$perms.init()
      this.$router.push({ path: '/', param: {} })
      return
    }
    // checks if ur in localhost and if
    if (window.location.host == 'localhost') {
      UserRouter.localBackdoor().then((res) => {
        const token = `Bearer ${res.access_token}`
        this.$auth.strategy.token.set(token)

        this.$auth.fetchUser().then(() => {
          this.$perms.init()
          this.$router.push({ path: '/', param: {} })
        })
      })
    } else if (this.$route.query && this.$route.query.code) {
      // if you have a code in ur path it will attempt to log you in
      UserRouter.getAuthToken({ code: this.$route.query.code }).then((res) => {
        const token = `Bearer ${res.access_token}`
        this.$auth.strategy.token.set(token)

        this.$router.replace({ query: null })
        this.$auth.fetchUser().then(() => {
          this.$perms.init()
          this.$router.push({ path: '/', param: {} })
        })
      })
    } else {
      // otherwise it logins and opens the microsoft login
      this.$auth.loginWith('social')
    }
  },
}
</script>

<style></style>
