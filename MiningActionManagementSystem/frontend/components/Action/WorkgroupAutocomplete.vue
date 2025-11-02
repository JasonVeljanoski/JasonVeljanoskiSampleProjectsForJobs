<template>
  <v-menu v-model="show" :close-on-content-click="false">
    <template #activator="slot_props">
      <slot name="activator" v-bind="{ ...slot_props }" />
    </template>
    <v-card>
      <v-autocomplete
        ref="input"
        v-model="selected_workgroup"
        :items="workgroup_titles"
        v-bind="$bind.select"
        autofocus
        :append-icon="selected_workgroup ? 'mdi-content-save' : 'mdi-menu-down'"
        item-text="title"
        placeholder="Start typing the group title..."
        return-object
        @click:append="handleAddWorkgroup"
        @blur="show = false"
      >
        <template #item="{ item }">
          <privacy-enum-icon :value="item.privacy" />
          <span class="ml-2">{{ item.title }}</span>
        </template>
      </v-autocomplete>
    </v-card>
  </v-menu>
</template>

<script>
import PrivacyEnumIcon from '@/components/Icon/PrivacyEnumIcon.vue'

export default {
  components: {
    PrivacyEnumIcon,
  },
  props: {
    action_id: { type: Number },
    action_privacy: { type: Number },
    existing_workgroups: { type: Array },
  },
  data() {
    return {
      show: false,
      workgroup_titles: [],
      selected_workgroup: null,
    }
  },
  mounted() {
    this.getWorkgroupTitles()
  },
  methods: {
    getWorkgroupTitles() {
      this.$axios
        .$get('/privacy/workgroup_titles')
        .then((res) => {
          this.workgroup_titles = res
        })
        .catch((err) => console.error(err))
    },
    // -----------------------------
    // APPEND ACTION HANDLERS
    // -----------------------------
    appendActionToWorkgroup() {
      // ! change route names and remove unused routes
      this.$axios
        .$patch('/action/append_action_to_workgroup', null, {
          params: {
            workgroup_id: this.selected_workgroup.id,
            action_id: this.action_id,
            action_privacy: this.action_privacy,
            workgroup_privacy: this.selected_workgroup.privacy,
            return_workgroup_response: true,
          },
        })
        .then(() => {
          this.$snackbar.add(`Action was successfully added to the group`)

          // ---
          this.triggerReload()
          this.show = false
          // ---

          // reset
          this.selected_workgroup = null
        })
        .catch((err) => console.error(err))
    },
    handleAddWorkgroup() {
      let message = ''
      if (this.selected_workgroup.privacy == 1 && this.action_privacy == 1) {
        message = 'Any public action can be appended to any public group.'
      } else {
        message = `Confirming will remove this action from all other groups as well as changing the privacy accordingly if needed.`
      }

      if (
        this.selected_workgroup &&
        confirm('Are you sure you want the selected group to hold this action? ' + message)
      ) {
        // you cannot add the same action twice to a single workgroup
        const res = this.existing_workgroups.filter((x) => x.id == this.selected_workgroup.id)
        if (res.length > 0) {
          this.$snackbar.add(`Action already exists in Group`, 'warning')
          return
        }

        // add action to workgroup
        this.appendActionToWorkgroup()
      } else {
        // reset
        this.selected_workgroup = null
        this.show = false
      }
    },
    triggerReload() {
      this.$emit('trigger_reload')
    },
  },
}
</script>

<style lang="scss" scoped></style>
