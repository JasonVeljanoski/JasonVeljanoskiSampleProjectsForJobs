<template>
  <v-menu v-model="show_menu" :close-on-content-click="false" eager absolute min-width="300">
    <template #activator="{ on, attrs }">
      <v-badge
        :color="existing_workgroups.length > 0 ? 'primary' : 'error'"
        overlap
        offset-x="16"
        offset-y="20"
        :content="existing_workgroups.length > 0 ? existing_workgroups.length : '0'"
      >
        <e-icon-btn v-bind="attrs" tooltip="Group" v-on="on"> mdi-account-supervisor-circle </e-icon-btn>
      </v-badge>
    </template>
    <v-card>
      <v-list dense>
        <v-subheader>GROUPS</v-subheader>
        <v-divider />
        <template v-if="existing_workgroups.length > 0">
          <v-list-item v-for="item in existing_workgroups" :key="item.id" :selectable="false">
            <v-list-item-content>
              <v-list-item-subtitle class="d-flex justify-space-between align-center">
                <privacy-enum-icon :value="item.privacy" />
                <span class="ml-2">{{ item.title }}</span>
                <v-spacer />
                <e-icon-btn @click="fullScreenMode(item.id)">mdi-fullscreen</e-icon-btn>
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </template>

        <v-list-item v-else>
          <v-list-item-content>
            <v-list-item-subtitle>No groups.</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <v-divider />
        <v-list-item-group>
          <workgroup-autocomplete
            :action_id="action_id"
            :action_privacy="action_privacy"
            :existing_workgroups="existing_workgroups"
            @trigger_reload="$emit('trigger_reload')"
          >
            <template #activator="{ on }">
              <v-list-item v-on="on">
                <v-list-item-content>
                  <v-list-item-title> Append action to new group </v-list-item-title>
                </v-list-item-content>
                <v-list-item-icon>
                  <v-icon color="primary">mdi-menu-down</v-icon>
                </v-list-item-icon>
              </v-list-item>
            </template>
          </workgroup-autocomplete>
        </v-list-item-group>
      </v-list>
    </v-card>

    <!-- DIALOGS -->
    <group-fullscreen-dialog ref="group_dialog" @trigger_reload="triggerReload" />
  </v-menu>
</template>

<script>
import PrivacyEnumIcon from '@/components/Icon/PrivacyEnumIcon.vue'
import GroupFullscreenDialog from '@/components/Workgroup/GroupFullscreenDialog.vue'
import WorkgroupAutocomplete from '@/components/Action/WorkgroupAutocomplete.vue'

export default {
  components: {
    PrivacyEnumIcon,
    GroupFullscreenDialog,
    WorkgroupAutocomplete,
  },
  props: {
    action_id: { type: Number },
    action_privacy: { type: Number },
    existing_workgroups: { type: Array },
  },
  data() {
    return {
      show_menu: false,
      selected_workgroup: null,
    }
  },
  methods: {
    fullScreenMode(id) {
      this.$axios
        .$get('/workgroup', {
          params: {
            id,
          },
        })
        .then((res) => {
          this.$refs.group_dialog.open(res).catch((err) => console.error(err))
        })
        .catch((err) => console.error(err))
    },

    triggerReload() {
      this.$emit('trigger_reload')
    },
  },
}
</script>

<style lang="scss" scoped></style>
