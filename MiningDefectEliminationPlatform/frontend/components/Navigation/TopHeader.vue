<template>
  <v-row class="header">
    <v-img
      :src="$theme.getLogo()"
      style="cursor: pointer"
      max-height="70"
      max-width="150"
      @click="$router.push('/')"
    />
    <v-btn
      @click="$router.push('/investigation')"
      class="ml-4 large-device"
      text
    >
      Start New Investigation
    </v-btn>
    <v-spacer />

    <div @click="$router.push('/')" class="logo" style="cursor: pointer">
      <the-logo />
    </div>
    <v-menu offset-y open-on-hover>
      <template v-slot:activator="{ attrs, on }">
        <v-btn v-bind="{ ...attrs }" v-on="on" icon>
          <v-icon>mdi-menu</v-icon>
        </v-btn>
      </template>

      <v-list>
        <v-list-item
          v-for="item in menu"
          :key="item.title"
          @click="$router.push(`/${item.slug}`)"
          link
        >
          <v-list-item-title v-text="item.title" />
        </v-list-item>
      </v-list>
    </v-menu>

    <v-btn icon @click="$theme.toggle()">
      <v-icon>{{
        $theme.is_dark ? "mdi-white-balance-sunny" : "mdi-moon-waning-crescent"
      }}</v-icon>
    </v-btn>

    <!-- <user-profile-form ref="user_dialog" /> -->
  </v-row>
</template>

<script>
import TheLogo from "@/components/Utils/TheLogo";
import UserProfileForm from "@/components/Navigation/UserProfileForm";

export default {
  components: {
    TheLogo,
    UserProfileForm,
  },
  data() {
    return {
      toggleUserProfile: false,
      menu: [
        { title: "Investigations", slug: "investigations" },
        { title: "Actions", slug: "actions" },
        { title: "Charts", slug: "charts" },
        { title: "Dashboards", slug: "dashboards" },
        { title: "Logos", slug: "logos" },
        { title: "Users", slug: "users" },
        { title: "REMS", slug: "rems" },
      ],
    };
  },
};
</script>

<style scoped>
.header {
  z-index: 10000;
  display: flex;
  justify-content: center;
  align-items: center;
  /* background-color: var(--v-accent-base); */
}

.logo {
  width: 150px;
}
</style>
