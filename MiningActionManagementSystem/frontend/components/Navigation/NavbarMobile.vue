<template>
  <div>
    <!-- NAV BAR -->
    <v-app-bar
      fixed
      app
      clipped-left
      clipped-right
      :class="{ 'non-prod': !is_prod && !is_impersonating, impersonating: is_impersonating }"
    >
      <div>
        <v-img :src="$theme.getAceLogo()" height="50" width="50" contain />
      </div>
      <nuxt-link to="/actions">
        <v-img :src="$theme.getLogo()" height="50" width="80" contain />
      </nuxt-link>

      <v-spacer />

      <e-icon-btn @click="drawer = true"> mdi-menu </e-icon-btn>
    </v-app-bar>

    <!-- SIDE BAR -->
    <v-navigation-drawer v-if="drawer" v-model="drawer" right absolute temporary>
      <v-list>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title class="text-h6">
              {{ $auth.user.name }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ $auth.user.email }}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <v-divider />
        <v-subheader>NAVIGATION</v-subheader>
        <v-divider />
        <template v-for="item in navbar_buttons">
          <v-list-item v-if="!item.menu" :key="item.to" text @click="navigate(item.to)">
            <v-list-item-icon>
              <v-icon left>{{ item.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item>
          <v-list-group v-else>
            <template #activator>
              <v-list-item-icon>
                <v-icon left>{{ item.icon }}</v-icon>
              </v-list-item-icon>
              <v-list-item-title>{{ item.title }}</v-list-item-title>
            </template>

            <template v-for="x in item.menu">
              <v-list-item v-if="x.show" :key="x.to" link @click="navigate(x.to)">
                <v-icon left>{{ x.icon }}</v-icon>
                <v-list-item-title>{{ x.title }}</v-list-item-title>
              </v-list-item>
            </template>
          </v-list-group>
          <v-divider />
        </template>
        <v-subheader>TOOLS</v-subheader>
        <v-divider />
        <v-list-item text @click="createFeedback">
          <v-list-item-icon>
            <v-icon left> mdi-bug</v-icon>
          </v-list-item-icon>
          <v-list-item-title>New Feedback</v-list-item-title>
        </v-list-item>
        <v-divider />
        <v-list-group>
          <template #activator>
            <v-list-item-icon>
              <v-icon left>mdi-card-account-details</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Access</v-list-item-title>
          </template>

          <v-list-item @click="handleAccessChange(1)">
            <v-icon left>mdi-account</v-icon>
            <v-list-item-title>Basic</v-list-item-title>
          </v-list-item>
          <v-list-item @click="handleAccessChange(2)">
            <v-icon left>mdi-crown</v-icon>
            <v-list-item-title>Admin</v-list-item-title>
          </v-list-item>
          <v-list-item @click="handleAccessChange(3)">
            <v-icon left>mdi-shield-crown</v-icon>
            <v-list-item-title>Super Admin</v-list-item-title>
          </v-list-item>
        </v-list-group>
        <v-divider />
        <v-list-item text @click="$theme.toggle()">
          <v-list-item-icon>
            <v-icon left> {{ $theme.isDark() ? 'mdi-white-balance-sunny' : 'mdi-moon-waning-crescent' }}</v-icon>
          </v-list-item-icon>
          <v-list-item-title>{{ $theme.isDark() ? 'Light Mode' : 'Dark Mode' }}</v-list-item-title>
        </v-list-item>
        <v-divider />
        <v-subheader>USER</v-subheader>
        <v-divider />
        <user-menu-list-items />
        <v-divider />
      </v-list>
    </v-navigation-drawer>

    <!-- DIALOGS -->
    <feedback-form ref="feedback_form" @add_feedback="submitFeedback($event)" />
  </div>
</template>

<script scoped>
import FeedbackForm from '@/components/Feedback/FeedbackForm.vue'
import UserMenuListItems from '@/components/Navigation/UserMenuListItems.vue'

export default {
  components: {
    FeedbackForm,
    UserMenuListItems,
  },
  data() {
    return {
      access: null,
      drawer: false,
    }
  },
  computed: {
    navbar_buttons() {
      return [
        {
          to: '/actions',
          icon: ' mdi-format-list-checkbox',
          title: 'Actions',
          show: true,
        },
        {
          to: '/groups',
          icon: ' mdi-account-supervisor-circle',
          title: 'Groups',
          show: true,
        },
        {
          to: null,
          icon: ' mdi-account-cog',
          title: 'Manage',
          show: true,
          menu: [
            {
              to: '/feedback',
              icon: ' mdi-bug',
              title: 'Feedback',
              show: true,
            },
            {
              to: '/admin',
              icon: ' mdi-cogs',
              title: 'Admin',
              show: this.$perms.is_admin,
            },
          ],
        },
      ].filter((x) => x.show)
    },
    is_impersonating() {
      return this.$utils.getJWT()?.is_impersonating
    },
    is_prod() {
      return process.env.ENV == 'prod'
    },
  },
  mounted() {
    this.access = this.$auth.user.access - 1
  },
  methods: {
    navigate(to) {
      this.$router.push(to)
    },
    // -----------------------------
    // FEEDBACK MODULE
    // -----------------------------
    createFeedback() {
      this.$refs.feedback_form.open(null)
    },
    submitFeedback(payload) {
      this.loading = true

      // ---------------------------
      // handle attachments + its metadata (sending attachments through pydantic sucks...)

      const form_data = new FormData()

      const attachments = payload.attachments
      const files_metadatas = []
      for (const attachment of attachments) {
        files_metadatas.push({
          title: attachment.title,
          description: attachment.description,
          network_drive_link: attachment.network_drive_link,
        })

        form_data.append('attachments', attachment.file)
      }

      const feedback = payload.feedback
      feedback.general_attachments_metas = files_metadatas
      form_data.append('edits', JSON.stringify(feedback))

      // ----------------------------

      this.$axios
        .$put('feedback', form_data)
        .then((res) => {
          this.$nuxt.$emit('force_load_data_update')
          this.$snackbar.add('New Feedback Item Created')

          // --------------------------------

          if (payload.to_email) {
            this.$axios
              .$post('/feedback/send_email', null, {
                params: { feedback_id: res.id },
              })
              .catch((err) => console.error(err))
          }
        })
        .catch((err) => console.error(err))
    },
    // -----------------------------
    // CHANGE PERMS - uat feature only
    // -----------------------------
    handleAccessChange(access) {
      if (this.is_prod) return
      this.$axios
        .$patch('/user/access', null, {
          params: { access },
        })
        .then(() => window.location.reload())
        .catch((err) => console.error(err))
    },
    hasActiveChild(children) {
      return children.some((x) => this.$route.path.includes(x.to))
    },
  },
}
</script>

<style lang="scss" scoped>
.non-prod {
  $color: rgb(19, 166, 68);
  outline: solid $color 4px;
  outline-offset: -4px;
  &:before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: $color;
    opacity: 0.2;
  }
}

.impersonating {
  &:before,
  &:after {
    content: '';
    position: absolute;
    left: 0;
    width: 100%;
    height: 5px;
    background: repeating-linear-gradient(-45deg, #cb5a5e, #cb5a5e 12px, transparent 10px, transparent 23px);
  }

  &:before {
    top: 0;
  }

  &:after {
    bottom: 0;
  }
}
</style>
