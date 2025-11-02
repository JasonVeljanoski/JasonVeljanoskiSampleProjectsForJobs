<template>
  <v-menu ref="menu" offset-y :close-on-content-click="false">
    <template #activator="{ on }">
      <div v-on="on">
        <slot>
          <v-btn v-bind="buttonProps" style="border-radius: 5px; height: 30px" class="py-2">
            <v-icon small dense :color="value">{{ icon }}</v-icon>
          </v-btn>
        </slot>
      </div>
    </template>
    <v-color-picker
      :value="value"
      mode="hexa"
      :swatches="swatches"
      show-swatches
      hide-canvas
      hide-sliders
      hide-inputs
      hide-mode-switch
      @update:color="handleInput"
    />
  </v-menu>
</template>

<script>
export default {
  name: 'ColorPicker',
  props: {
    value: {
      type: String,
    },
    swatches: {
      type: Array,
      default: () => ['#000000', '#FFFFFF', '#212e4d', '#355bb7', '#FFC107', 'E53935'],
    },
    icon: {
      type: String,
      default: 'mdi-format-color-fill',
    },
    buttonProps: {
      type: Object,
      default: () => ({
        tile: true,
        text: true,
        dense: true,
        small: true,
        outlined: true,
        rounded: true,
      }),
    },
  },
  methods: {
    handleInput(value) {
      this.$emit('input', value.hex)
    },
  },
}
</script>
