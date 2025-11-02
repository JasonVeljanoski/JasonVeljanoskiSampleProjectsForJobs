<template>
  <v-app-bar fixed app class="navbar" :class="{ 'green-mode': $settings.showGreenBar() }" style="height: 60px">
    <!-- NAV ITEMS -->
    <portal-target name="navbar" multiple class="d-flex align-center" style="gap: 8px" />

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

    <e-icon-btn class="ml-2" tooltip="Toggle Colour Theme" @click="$theme.toggle()">
      {{ $theme.isDark() ? 'mdi-white-balance-sunny' : 'mdi-moon-waning-crescent' }}
    </e-icon-btn>
    <e-title>Catalyst</e-title>

    <user-menu class="ml-2" />
  </v-app-bar>
</template>

<script scoped>
import UserMenu from './UserMenu.vue'
import ETitle from './Title.vue'

export default {
  components: {
    UserMenu,
    ETitle,
  },
  data() {
    return {
      access: null,
    }
  },
  computed: {
    navbar_buttons() {
      return [].filter((x) => x.show)
    },
    is_prod() {
      return process.env.ENV == 'prod'
    },
  },
  methods: {
    hasActiveChild(children) {
      return children.some((x) => this.$route.path.includes(x.to))
    },
  },
}
</script>

<style lang="scss" scoped></style>
