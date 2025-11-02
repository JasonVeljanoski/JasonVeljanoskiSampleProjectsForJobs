<template>
  <v-card outlined min-width="300">
    <v-card-title>
      {{ title }}
      <v-spacer />

      <hidden-text-field placeholder="Add Label" @submit="addLabel">
        <template #activator="{ on }">
          <e-icon-btn tooltip="New Label" v-on="on">mdi-plus</e-icon-btn>
        </template>
      </hidden-text-field>
    </v-card-title>

    <v-divider />

    <draggable :list="values" dense tag="v-list" v-bind="drag_options" class="scroll-area" @end="onEnd">
      <v-card v-for="(v, ii) in values" :key="ii" flat>
        <v-card-text class="d-flex align-center">
          <v-icon class="handle" left small color="primary">mdi-format-line-spacing</v-icon>

          <v-text-field
            :ref="'textField' + ii + v.label"
            v-model="values_copy[ii].label"
            dense
            flat
            solo
            hide-details
            @keyup.enter="handleEdit(ii, v)"
            @blur="resetVal(ii, v)"
          />
          <v-spacer />

          <color-picker
            :value="values_copy[ii].color"
            :swatches="swatches"
            show-swatches
            @input="updateColor($event, ii)"
          >
            <e-icon-btn :color="values_copy[ii].color">mdi-brush</e-icon-btn>
          </color-picker>

          <e-icon-btn color="error" @click="removeLabel(v.id)"> mdi-delete </e-icon-btn>
        </v-card-text>
        <v-divider />
      </v-card>
    </draggable>
  </v-card>
</template>

<script>
import Draggable from 'vuedraggable'

export default {
  components: {
    Draggable,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    base_url: {
      type: String,
      required: true,
    },
    values: {
      type: Array,
      required: true,
    },
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
      values_copy: null,
      swatches: [
        ['#355bb7', '#4CAF50', '#E53935'],
        ['#26C6DA', '#FFC107', '#B71C1C'],
      ],
      color_mapper: {
        '#4CAF50': 'success',
        '#FFC107': 'warning',
        '#E53935': 'error',
        '#B71C1C': 'error2',
        '#355bb7': 'primary',
        '#26C6DA': 'secondary',
      },
    }
  },
  created() {
    this.initOrder()
  },
  methods: {
    // ------------------------------------
    // CREATE
    // ------------------------------------
    create(model) {
      //  map hex to vuetify color in nuxt.config.js
      const copy_model = JSON.parse(JSON.stringify(model))
      if (Object.keys(this.color_mapper).includes(copy_model.color)) {
        copy_model.color = this.color_mapper[copy_model.color]
      }

      this.$axios.$post(this.base_url, copy_model).then((res) => {
        res.color = this.colorNameToHex(res.color)

        this.$set(this.values_copy, this.values_copy.length, JSON.parse(JSON.stringify(res)))
        this.$set(this.values, this.values.length, JSON.parse(JSON.stringify(res)))

        // update the enum store
        this.$enums.importAllEnums()
      })
    },
    addLabel(label) {
      if (!label) return

      const exists = this.values.some((v) => v.label == label)
      if (exists) return

      const model = {
        label,
      }

      this.create(model)
    },
    // ------------------------------------
    // UPDATE
    // ------------------------------------
    resetVal(ii, v) {
      this.values_copy[ii].label = v.label
    },
    colorNameToHex(name) {
      const key = Object.keys(this.color_mapper).find((k) => this.color_mapper[k] == name)
      if (key) return key
      return name
    },
    update(model, ii) {
      // check if the model label matches any other
      const exists = this.values.some((v) => v.label == model.label && v.id != model.id)
      if (exists) {
        this.resetVal(ii)
        return
      }

      // ------------------------------------

      // map hex to vuetify color in nuxt.config.js
      const copy_model = JSON.parse(JSON.stringify(model))
      if (Object.keys(this.color_mapper).includes(copy_model.color)) {
        copy_model.color = this.color_mapper[copy_model.color]
      }

      // ------------------------------------

      this.$axios.$put(this.base_url, copy_model).then((res) => {
        res.color = this.colorNameToHex(res.color)

        this.values.splice(ii, 1, JSON.parse(JSON.stringify(res)))
        this.values_copy.splice(ii, 1, JSON.parse(JSON.stringify(res)))

        // update the enum store
        this.$enums.importAllEnums()
      })
    },
    updateAll() {
      // map hex to vuetify color in nuxt.config.js
      const copy_values = JSON.parse(JSON.stringify(this.values_copy))
      copy_values.forEach((v) => {
        if (Object.keys(this.color_mapper).includes(v.color)) {
          v.color = this.color_mapper[v.color]
        }
      })

      // ------------------------------------

      this.$axios
        .$put(`${this.base_url}/all`, copy_values)
        .then(() => this.$enums.importAllEnums())
        .catch((err) => {
          console.error(err)
        })
    },
    handleEdit(ii, v) {
      const is_null = this.values_copy[ii].label == null || this.values_copy[ii].label == ''

      if (is_null || !confirm('Are you sure you want to edit this label?')) {
        this.resetVal(ii, v)
        return
      }

      this.update(this.values_copy[ii], ii)
    },
    updateColor(color, ii) {
      this.values_copy[ii].color = color
      this.update(this.values_copy[ii], ii)
    },
    // ------------------------------------
    // DELETE
    // ------------------------------------
    removeLabel(id) {
      if (!confirm('Are you sure you want to remove this label?')) {
        return
      }

      this.$axios
        .$delete(this.base_url, {
          params: {
            id,
          },
        })
        .then(() => {
          const index = this.values.findIndex((v) => v.id === id)
          if (index !== -1) {
            // Remove the item from both arrays, inplace
            this.values.splice(index, 1)
            this.values_copy.splice(index, 1)
          }
        })
    },
    // ------------------------------------
    // DRAGGABLE HELPERS
    // ------------------------------------
    initOrder() {
      // sort values by order_key
      this.values = this.values.sort((a, b) => a.order - b.order)
      this.values_copy = JSON.parse(JSON.stringify(this.values))
    },
    onEnd() {
      // sort the values_copy array to match the order of the values array
      this.values_copy = this.values_copy.sort((a, b) => {
        const a_index = this.values.findIndex((v) => v.id === a.id)
        const b_index = this.values.findIndex((v) => v.id === b.id)
        return a_index - b_index
      })

      // update the order of the values
      this.values.forEach((v, ii) => {
        v.order = ii
      })
      this.values_copy.forEach((v, ii) => {
        v.order = ii
      })

      // update the database
      this.updateAll()
    },
  },
}
</script>

<style lang="scss" scoped>
.handle {
  cursor: ns-resize;
}

.dragging {
  opacity: 0.6;
  background: #888;
}

.scroll-area {
  overflow: auto;
  max-height: 400px;
}
</style>
