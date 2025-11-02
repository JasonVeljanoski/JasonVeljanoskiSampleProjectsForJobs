<template>
  <div class="d-flex flex-column" style="width: 100%">
    <h4>{{ title }}</h4>
    <v-autocomplete
      v-bind="{ ...$bind.generic, ...$attrs }"
      v-model="selected"
      :search-input.sync="search"
      :items="items"
      :filter-duplicate="false"
      multiple
      no-filter
      return-object
      item-value="id"
      @blur="search = null"
      @keydown.enter.prevent
      @keydown.enter.stop
      @change="
        $emit('input', selected)
        $emit('get:children')
      "
    >
      <template #selection="{ item }">
        <v-chip class="ma-1" close small @click:close="filterSelected(item)">
          <slot name="chip-text" :item="item" />
        </v-chip>
      </template>

      <template #item="{ item }">
        <slot name="item" :item="item" />
      </template>
    </v-autocomplete>
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
    },
    url: {
      type: String,
      required: true,
    },
    parent_ref: Object,
  },
  data() {
    return {
      data: [],
      selected: [],
      search: null,
      token: null,
      timer: null,
    }
  },
  computed: {
    items() {
      if (this.data.length === 0 && this.selected.length === 0) return [{ header: 'Type To Search' }]

      return [{ header: 'Selected' }, ...this.selected, { header: 'Other' }, ...this.data]
    },
    readonly() {
      if (this.parent_ref) return this.parent_ref.selected.length > 0
      return false
    },
  },
  methods: {
    filterSelected(item) {
      this.selected = this.selected.filter((s) => s.id !== item.id)
      this.$emit('input', this.selected)
    },
    setData(setTo) {
      this.data = [...setTo]

      if (this.data.length === 1) {
        this.selected = [...this.data]
        this.$emit('input', this.selected)
      }
    },
    getData() {
      if (this.token) this.token.cancel()

      if (this.readonly) return

      if (!this.search) return (this.data = [])

      this.token = this.$axios.CancelToken.source()

      this.$emit('loading:start')

      this.$axios
        .$get(this.url, { params: { search: this.search } })
        .then((resp) => {
          this.data = [...resp]

          this.$emit('loading:end')
        })
        .catch((err) => {
          this.$emit('loading:end')
        })
        .finally(() => {
          this.$emit('loading:end')
        })
    },
  },
  watch: {
    search() {
      clearTimeout(this.timer)
      this.timer = setTimeout(() => {
        this.getData()
      }, 500)
    },
  },
}
</script>

<style lang="scss" scoped>
::v-deep .v-subheader {
  color: rgba(0, 0, 0, 0.6);
  font-weight: 600;
}
</style>
