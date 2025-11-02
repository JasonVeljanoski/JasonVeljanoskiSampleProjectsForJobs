<template>
  <v-app-bar
    fixed
    app
    clipped-left
    clipped-right
    class="navbar"
    :class="{ 'non-prod': !is_prod && !is_impersonating, impersonating: is_impersonating }"
  >
    <div>
      <v-img :src="$theme.getAceLogo()" width="50" contain />
    </div>
    <nuxt-link to="/actions">
      <v-img :src="$theme.getLogo()" height="50" width="80" contain />
    </nuxt-link>

    <!-- NAV ITEMS -->
    <template v-for="item in navbar_buttons">
      <v-btn v-if="!item.menu" :key="item.to" :to="item.to" text>
        <v-icon left>{{ item.icon }}</v-icon>
        {{ item.title }}
      </v-btn>
      <v-menu v-else :key="item.title" open-on-hover offset-y>
        <template #activator="{ on, attrs }">
          <v-btn text :class="{ 'v-btn--active': hasActiveChild(item.menu) }" v-bind="attrs" v-on="on">
            <v-icon left>{{ item.icon }}</v-icon>
            {{ item.title }}
          </v-btn>
        </template>
        <v-card>
          <v-list>
            <template v-for="x in item.menu">
              <v-list-item v-if="x.show" :key="x.to" :to="x.to" link>
                <v-icon left>{{ x.icon }}</v-icon>
                <v-list-item-title>{{ x.title }}</v-list-item-title>
              </v-list-item>
            </template>
          </v-list>
        </v-card>
      </v-menu>
    </template>

    <v-spacer />

    <!-- UAT FEATURE ONLY -->
    <v-btn-toggle v-if="!is_prod" v-model="access" class="mx-4 non-prod">
      <v-btn text @click="handleAccessChange(1)">
        Basic
        <v-icon right>mdi-account</v-icon>
      </v-btn>
      <v-btn text @click="handleAccessChange(2)">
        Admin
        <v-icon right>mdi-crown</v-icon>
      </v-btn>
      <v-btn text @click="handleAccessChange(3)">
        Super Admin
        <v-icon right>mdi-shield-crown</v-icon>
      </v-btn>
    </v-btn-toggle>

    <!-- FEEDBACK -->
    <v-btn v-bind="$bind.btn" color="primary" @click="createFeedback">
      <v-icon left>mdi-bug</v-icon>
      New Feedback
    </v-btn>

    <e-icon-btn class="ml-2" tooltip="Toggle Colour Theme" @click="$theme.toggle()">
      {{ $theme.isDark() ? 'mdi-white-balance-sunny' : 'mdi-moon-waning-crescent' }}
    </e-icon-btn>

    <user-menu class="ml-2" />

    <!-- DIALOGS -->
    <feedback-form ref="feedback_form" @add_feedback="submitFeedback($event)" />
  </v-app-bar>
</template>

<script scoped>
import UserMenu from '@/components/Navigation/UserMenu.vue'
import FeedbackForm from '@/components/Feedback/FeedbackForm.vue'

export default {
  components: {
    UserMenu,
    FeedbackForm,
  },
  data() {
    return {
      access: null,
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
              to: '/test',
              icon: ' mdi-test-tube',
              title: 'Test',
              show: process.env.ENV != 'prod',
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
