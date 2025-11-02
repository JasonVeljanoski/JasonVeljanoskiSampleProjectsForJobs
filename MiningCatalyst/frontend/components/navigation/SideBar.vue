<template>
  <v-navigation-drawer app permanent rail :mini-variant="mini" :class="{ 'green-mode': $settings.showGreenBar() }">
    <v-list class="pt-0">
      <v-list-item-group color="primary" mandatory @change="$emit('input', $event)">
        <!-- fortescue -->
        <v-list-item class="pl-1" :style="{ height: nav_height }" inactive @click="$router.push('/')">
          <v-img :src="$theme.getFMGLogo()" max-width="45" />
          <v-list-item-content>
            <v-list-item-title>
              <v-img :src="fortescue_text_img" class="svg_wrapper" />
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-divider />

        <!-- menu -->
        <v-list-item v-for="(tab, key) in tabs" :key="key" :to="tab.to">
          <v-list-item-icon>
            <v-icon>{{ tab.icon }}</v-icon>
          </v-list-item-icon>
          <v-list-item-title>{{ tab.title }}</v-list-item-title>
        </v-list-item>

        <!-- customise -->
        <slot />
      </v-list-item-group>
    </v-list>

    <!-- open/close -->
    <template #append>
      <div class="d-flex pa-2">
        <v-spacer />
        <e-icon-btn @click="mini = !mini">
          {{ mini ? 'mdi-arrow-right' : 'mdi-arrow-left' }}
        </e-icon-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script>
export default {
  data() {
    return {
      mini: true,
      close_on_click: false,
    }
  },
  computed: {
    tabs() {
      const tabs = {
        home: {
          icon: 'mdi-home',
          title: 'Home',
          to: '/',
          show: true,
        },
        initiatives: {
          icon: 'mdi-finance',
          title: 'Initiatives',
          to: '/initiatives',
          show: true,
        },
        test: {
          icon: 'mdi-test-tube',
          title: 'Test',
          to: 'test',
          show: true,
        },
        admin: {
          to: '/admin',
          icon: ' mdi-cogs',
          title: 'Admin',
          show: this.$perms.is_admin,
        },
      }

      return this.$utils.filterObj(tabs, (k, v) => v.show)
    },
    nav_height() {
      const shaddow_height = 4
      const navbar_height = this.$vuetify.application.top
      return navbar_height - shaddow_height + 'px'
    },
    fortescue_text_img() {
      return `/icons/fortescue_text_${!this.$theme.isDark() ? 'light' : 'dark'}.svg`
    },
  },
}
</script>

<style lang="scss" scoped>
.svg_wrapper {
  width: 120px;
  margin-left: -7px;
}
</style>
