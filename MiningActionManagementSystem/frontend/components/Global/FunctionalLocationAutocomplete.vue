<template>
  <div>
    <v-autocomplete
      v-bind="{ ...$attrs, ...$props }"
      class="main-selector"
      prepend-inner-icon="mdi-filter-outline"
      @click:prepend-inner="openDialog"
      v-on="$listeners"
    />
    <v-dialog v-model="dialog" width="unset" min-width="900">
      <v-card>
        <div class="selector-wrapper pa-4">
          <div v-for="(items, index) in available_floc_indexes" :key="index">
            <v-autocomplete
              ref="input"
              v-model="selected_options[index]"
              :items="items"
              hide-details
              outlined
              autofocus
              dense
              :disabled="index > 0 && !selected_options[index - 1]"
              @change="inputChange(index)"
            />
          </div>
          <e-icon-btn tooltip="save" :disabled="is_not_leaf" @click="submitValue()"> mdi-content-save </e-icon-btn>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
const LEAF_KEY = '__is_leaf'

export default {
  data() {
    return {
      dialog: false,
      selected_options: [],
      floc_tree: {},
    }
  },
  computed: {
    value() {
      return this.$attrs.value
    },
    items() {
      return this.$attrs.items
    },
    max_count() {
      const get_length = (item, count) => {
        if (Object.keys(item).length > 0) {
          return 1 + Math.max(...Object.values(item).map((x) => get_length(x, count)))
        }

        count &&= count - 1 // -1 to not include leaf (null)

        return count
      }

      const temp_root = this.selected_options.reduce((a, b) => a[b], this.floc_tree)
      return get_length(temp_root, this.selected_options.length)
    },
    available_floc_indexes() {
      this.selected_options = this.selected_options.filter((x) => x)
      const selected = this.selected_options
      const max_count = this.max_count

      const available = [...Array(max_count)].map(() => [])

      let root = this.floc_tree

      for (let ii = 0; ii <= Math.min(selected.length, max_count - 1); ii++) {
        const keys = Object.keys(root)
          .map((x) => {
            if (x != LEAF_KEY) return x
          })
          .sort()

        if (keys.length != 0) available[ii] = keys

        root = root[selected[ii]]
      }

      return available
    },
    is_not_leaf() {
      let tree = this.floc_tree
      for (const key of this.selected_options) tree = tree[key]
      return !tree[LEAF_KEY]
    },
  },
  watch: {
    dialog() {
      if (this.dialog) this.constructFlocTree()
    },
  },
  methods: {
    constructFlocTree() {
      const tree = {}

      for (const item of this.items) {
        let temp = tree

        const keys = item.split('-')
        keys.push(null)

        for (const key of keys) {
          if (key) {
            temp[key] ||= {}
            temp = temp[key]

            temp[LEAF_KEY] ||= 0
          } else {
            temp[LEAF_KEY] = 1
          }
        }
      }
      this.floc_tree = tree
    },
    openDialog() {
      if (this.items.length == 0) return // can't open dialog before items are loaded

      this.dialog = true
      if (this.value) {
        this.selected_options = this.value.split('-')
      } else {
        this.selected_options = []
      }
    },
    inputChange(index) {
      this.selected_options = this.selected_options.slice(0, index + 1)

      this.$nextTick(() => {
        if (index + 1 < this.max_count) {
          this.$refs.input[index + 1].focus()
          this.$refs.input[index + 1].activateMenu()
        } else {
          this.submitValue()
        }
      })
    },
    submitValue() {
      const new_value = this.selected_options.join('-')
      this.$emit('input', new_value)
      this.$emit('change', new_value)

      this.dialog = false
    },
  },
}
</script>

<style lang="scss" scoped>
.selector-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;

  > *:not(:first-child) > .v-autocomplete::before {
    font-size: 1em;
    margin-right: 0px;
    padding: 10px;
    color: var(--v-primary-base);
    content: '—';
  }
}

::v-deep {
  .v-dialog .v-autocomplete > .v-input__control {
    width: 130px;
  }
}
</style>
