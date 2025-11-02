<template>
  <div @mouseenter="hovering = true" @mouseleave="hovering = false">
    <!-- HEADER -->
    <form-input-title
      :title="title"
      :loading="loading"
      :edit_mode="edit_mode || edit_only"
      :info_text="info_text"
      :required="required"
    />

    <!-- LOADER -->
    <v-skeleton-loader v-if="loading" :type="skeleton_loader_type" />

    <div v-else class="d-flex align-center" :class="{ active: is_active }">
      <!-- SLOTS -->
      <div style="width: 100%">
        <slot v-if="!edit_mode && !edit_only" name="input:reader" />
        <slot v-else name="input:writer" />
      </div>
      <v-spacer />
      <!-- ACTIONS -->
      <div v-if="show_actions && !edit_only" class="ml-2">
        <e-icon-btn v-if="!edit_mode" tooltip="Edit Value" style="min-width: 40px" @click="editMode">
          mdi-pencil
        </e-icon-btn>
        <div v-else style="min-width: 80px">
          <e-icon-btn tooltip="Cancel" @click="cancel">mdi-close-circle</e-icon-btn>
          <e-icon-btn tooltip="Submit Change" @click="updateField">mdi-content-save</e-icon-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    // Editable Input Props
    loading: { type: Boolean, default: null },
    edit_only: { type: Boolean, default: false },

    // Form Input Props
    title: { type: String },
    info_text: { type: String, default: null },
    skeleton_loader_type: { type: String, default: 'heading' },
    required: { type: Boolean, default: false },
  },
  data() {
    return {
      edit_mode: false,
      hovering: false,
    }
  },
  computed: {
    show_actions() {
      return this.hovering || this.edit_mode
    },
    is_active() {
      return this.hovering && !this.edit_mode && !this.edit_only
    },
  },
  methods: {
    editMode() {
      this.$emit('edit:setup')
      this.edit_mode = true
    },
    updateField() {
      this.$emit('edit:update')
    },
    cancel() {
      this.$emit('edit:cancel')
      this.edit_mode = false
    },
  },
}
</script>

<style lang="scss" scoped>
.active {
  border-radius: 5px;
  padding-left: 10px;
  padding-right: 5px;
  background-color: var(--v-tableBackground-base);
}
</style>
