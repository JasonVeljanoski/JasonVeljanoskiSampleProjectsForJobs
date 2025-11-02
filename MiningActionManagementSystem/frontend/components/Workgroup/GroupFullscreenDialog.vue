<template>
  <v-dialog v-if="workgroup" v-model="dialog" fullscreen hide-overlay transition="dialog-top-transition">
    <v-card tile>
      <!-- TITLE -->
      <v-card-title>
        {{ workgroup.title }}
        <v-spacer />
        <e-icon-btn @click="cancel()"> mdi-close </e-icon-btn>
      </v-card-title>
      <v-card-subtitle>{{ workgroup.description }}</v-card-subtitle>

      <v-divider />

      <!-- BODY -->
      <span class="body-wrapper">
        <v-card-text>
          <simple-action-table :workgroup="workgroup" @trigger_reload="triggerReload" />
        </v-card-text>
      </span>
    </v-card>
  </v-dialog>
</template>

<script>
import SimpleActionTable from '@/components/Action/SimpleActionTable.vue'

export default {
  components: {
    SimpleActionTable,
  },
  data() {
    return {
      dialog: false,
      workgroup: null,
    }
  },
  methods: {
    // ------------------------------
    // DIALOG HANDLERS
    // ------------------------------
    open(workgroup) {
      this.workgroup = workgroup
      this.dialog = true

      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },
    cancel(status = false) {
      this.resolve(status)
      this.dialog = false
    },
    triggerReload() {
      this.$emit('trigger_reload')
    },
  },
}
</script>

<style lang="scss" scoped>
.body-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: auto;

  max-height: calc(100vh - 100px);
}
</style>
