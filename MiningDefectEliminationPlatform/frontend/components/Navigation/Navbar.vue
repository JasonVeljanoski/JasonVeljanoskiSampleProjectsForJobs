<template>
  <v-app-bar fixed app clipped-left clipped-right class="navbar" :class="{ 'non-prod': !is_prod }">
    <nuxt-link to="/">
      <v-img :src="$theme.getLogo()" height="70" width="165" contain />
    </nuxt-link>
    <span :key="index">
      <v-btn
        v-for="(item, ii) in menu"
        :key="ii"
        text
        tile
        @click="switchPage(item)"
        :color="item.clicked ? 'primary' : ''"
      >
        <v-icon left>{{ item.icon }}</v-icon>
        {{ item.title }}
      </v-btn>
    </span>

    <manage-menu />

    <v-spacer />

    <!-- UAT FEATURE ONLY -->
    <v-btn-toggle v-if="!is_prod" v-model="is_admin" class="mx-4 non-prod">
      <v-btn :value="false" text @click="handleAccessChange(2)">
        Basic
        <v-icon right>mdi-account</v-icon>
      </v-btn>
      <v-btn :value="true" text @click="handleAccessChange(3)">
        Admin
        <v-icon right>mdi-crown</v-icon>
      </v-btn>
    </v-btn-toggle>

    <v-btn v-bind="$bind.btn" color="primary" @click="createFeedback">
      <v-icon left>mdi-bug</v-icon>
      New Feedback
    </v-btn>

    <nuxt-link to="/">
      <v-img :src="$theme.getDepLogo()" width="145" contain class="ml-4" />
    </nuxt-link>

    <!-- <notifications-menu /> -->
    <actions-menu />
    <e-icon-btn tooltip="Toggle Colour Theme" @click="$theme.toggle()">
      {{ $theme.isDark() ? "mdi-white-balance-sunny" : "mdi-moon-waning-crescent" }}
    </e-icon-btn>

    <user-menu />

    <!-- DIALOG -->
    <feedback-form ref="feedback_form" @add_feedback="submitFeedback($event)" />
  </v-app-bar>
</template>

<script scoped>
import UserMenu from "@/components/Navigation/UserMenu";
import NotificationsMenu from "@/components/Navigation/NotificationsMenu";
import ActionsMenu from "@/components/Navigation/ActionsMenu";
import ManageMenu from "@/components/Navigation/ManageMenu";
import TheLogoV2 from "@/components/Utils/TheLogoV2";
import FeedbackForm from "@/components/Feedback/FeedbackForm";

export default {
  components: {
    NotificationsMenu,
    ActionsMenu,
    UserMenu,
    ManageMenu,
    TheLogoV2,
    FeedbackForm,
  },
  mounted() {
    this.is_admin = this.$perms.is_admin;

    let indexPage = this.menuList.indexOf(window.location.pathname);
    if (indexPage !== -1) this.menu[indexPage].clicked = true;
  },
  data() {
    return {
      is_admin: false,
      is_prod: process.env.ENV == "prod",
      index: 0,
      menuList: ["/investigations", "/actions", "/charts", "/rems", "/dashboards"],
      menu: [
        {
          index: 0,
          title: "Investigations",
          slug: "investigations",
          icon: "mdi-application-edit-outline",
          clicked: false,
        },
        {
          index: 1,
          title: "Actions",
          slug: "actions",
          icon: "mdi-format-list-checkbox",
          clicked: false,
        },
        {
          index: 2,
          title: "APLUS",
          slug: "charts",
          icon: "mdi-chart-bar",
          clicked: false,
        },
        {
          index: 3,
          title: "REMS",
          slug: "rems",
          icon: "mdi-chart-bell-curve",
          clicked: false,
        },
        {
          index: 4,
          title: "Dashboards",
          slug: "dashboards",
          icon: "mdi-view-dashboard",
          clicked: false,
        },
      ],
    };
  },
  watch: {
    "$route.path"() {
      this.menu.forEach((m) => {
        m.clicked = false;
      });
      let indexPage = this.menuList.indexOf(window.location.pathname);
      if (indexPage !== -1) this.menu[indexPage].clicked = true;
    },
  },
  methods: {
    switchPage(item) {
      this.menu.forEach((m) => {
        m.clicked = false;
      });
      this.menu[item.index].clicked = true;
      this.$router.push(item.slug);

      this.index++;
    },
    // -----------------------------
    // FEEDBACK
    // -----------------------------
    createFeedback() {
      this.$refs.feedback_form.open(null);
    },
    submitFeedback(payload) {
      this.loading = true;

      // ---------------------------
      // handle attachments + its metadata (sending attachments through pydantic sucks...)

      const form_data = new FormData();

      const attachments = payload.attachments;
      let files_metadatas = [];
      for (let attachment of attachments) {
        files_metadatas.push({
          title: attachment.title,
          description: attachment.description,
          network_drive_link: attachment.network_drive_link,
        });

        form_data.append("attachments", attachment.file);
      }

      let feedback = payload.feedback;
      feedback.general_attachments_metas = files_metadatas;
      form_data.append("edits", JSON.stringify(feedback));

      // ----------------------------

      this.$axios
        .$put("feedback", form_data)
        .then(() => {
          this.$nuxt.$emit("force_load_data_update");
          this.$snackbar.add("New Feedback Item Created");
        })
        .catch((err) => console.error(err));
    },
    // -----------------------------
    // CHANGE PERMS - uat feature only
    // -----------------------------
    handleAccessChange(access) {
      this.$axios
        .$patch("/user/access", null, {
          params: { access },
        })
        .then(() => window.location.reload())
        .catch((err) => console.error(err));
    },
  },
};
</script>

<style lang="scss" scoped>
.non-prod {
  $color: rgb(19, 166, 68);
  outline: solid $color 4px;
  outline-offset: -4px;
  &:before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: $color;
    opacity: 0.2;
  }
}
</style>
