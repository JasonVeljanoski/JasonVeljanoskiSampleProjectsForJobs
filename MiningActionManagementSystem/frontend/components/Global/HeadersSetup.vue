<template>
  <div v-if="headers" class="header-setup">
    <draggable :list="headers" class="header-items" :move="checkMove" v-bind="drag_options">
      <div v-for="header in headers" :key="header.text" class="header-item">
        <v-icon v-if="header.persistent" small>mdi-format-line-spacing</v-icon>
        <v-icon v-else small class="handle">mdi-format-line-spacing</v-icon>
        <v-checkbox
          :input-value="!header.hide"
          hide-details
          class="mt-0 pt-0"
          style="width: 100%"
          :label="header.text"
          :disabled="header.persistent"
          @click="header.hide = !header.hide"
        />
      </div>
    </draggable>
    <v-divider v-if="show_presets" />
    <v-card-text v-if="show_presets" class="header-presets">
      <div class="d-flex">
        <h3 class="ml-2 mt-2">Presets</h3>
        <v-spacer />
        <e-icon-btn tooltip="Create New Blank Preset" @click="createPreset">mdi-plus</e-icon-btn>
      </div>
      <div class="scrollable py-1">
        <div v-for="(preset, ii) in preset_list" :key="preset.id">
          <div class="d-flex align-center">
            <v-radio-group
              :value="selected_preset"
              hide-details
              class="mt-0 pt-0"
              @change="$emit('preset:set', preset)"
            >
              <v-radio :value="preset.id" />
            </v-radio-group>
            <v-text-field
              v-model="preset.label"
              :readonly="!preset.id"
              hide-details
              solo
              dense
              flat
              @change="editPreset(preset, $event)"
            />
            <v-spacer />
            <e-icon-btn
              v-if="preset.id == selected_preset && changes_made"
              tooltip="Save Changes"
              @click="$emit('preset:save', preset)"
            >
              mdi-content-save
            </e-icon-btn>
            <e-icon-btn v-if="preset.id" tooltip="Delete Preset" @click="$emit('preset:delete', preset)">
              mdi-delete
            </e-icon-btn>
            <!-- <icon-btn v-else @click="createPreset">mdi-content-save</icon-btn> -->
          </div>
        </div>
      </div>
    </v-card-text>
  </div>
</template>

<script>
import Draggable from 'vuedraggable'

export default {
  components: { Draggable },
  props: {
    headers: { type: Array, default: () => [] },
    show_presets: { type: Boolean, default: false },
    presets: { type: Array, default: () => [] },
    selected_preset: null,
  },
  data() {
    return {
      drag_options: {
        animation: 200,
        group: 'description',
        disabled: false,
        ghostClass: 'dragging',
        handle: '.handle',
      },
    }
  },
  computed: {
    changes_made() {
      if (!this.selected_preset) return false

      const t1 = this.headers.map((x) => {
        return { id: x.id, hide: x.hide }
      })

      const temp = this.presets.find((x) => x.id == this.selected_preset)

      return JSON.stringify(t1) != temp.settings
    },
    preset_list() {
      const presets = [...this.presets]

      // if (!this.selected_preset) {
      presets.push({ id: 0, label: 'Default' })
      // }
      return presets
    },
  },
  methods: {
    createPreset() {
      this.$emit('preset:create', this.headers)
    },
    editPreset(preset, name) {
      this.$emit('preset:edit', preset, name)
    },
    checkMove(e) {
      const source = this.headers[e.draggedContext.index]
      const target = this.headers[e.relatedContext.index]

      return !(source.persistent || target.persistent)
    },
  },
}
</script>

<style lang="scss" scoped>
.header-setup {
  // outline: solid red;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
}

.header-items {
  display: flex;
  flex-direction: column;
  overflow: auto;
  flex-grow: 1;
  // gap: 8px;
}
.header-item {
  display: flex;
  border: solid #555 1px;
  margin-left: -1px;
  margin-top: -1px;
  // border-radius: 4px;
  padding: 8px;
  gap: 10px;

  background: var(--background-color);

  .handle {
    cursor: ns-resize;
  }

  &.dragging {
    opacity: 0.6;
    background: #888;
  }
}

.header-presets {
  flex-shrink: 0;

  padding: 0;

  max-height: 300px;
  display: flex;
  flex-direction: column;

  overflow: hidden;

  .scrollable {
    overflow-y: auto;
    padding-left: 16px;
  }
}
</style>
