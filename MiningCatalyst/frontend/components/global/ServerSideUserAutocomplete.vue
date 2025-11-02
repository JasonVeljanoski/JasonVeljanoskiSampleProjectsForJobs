<template>
  <v-autocomplete
    v-bind="{ ...$attrs, ...$props }"
    :search-input.sync="search"
    :loading="loading"
    :items="items"
    item-text="name"
    item-value="id"
    prepend-inner-icon="mdi-account-search"
    @blur="search = null"
    @keydown.enter.prevent
    @keydown.enter.stop
    @change="updateMemory($event, items)"
    v-on="$listeners"
  >
    <template #selection="data">
      <v-chip
        v-if="data.index < 2"
        v-bind="data.attrs"
        :input-value="data.selected"
        close-icon="mdi-close"
        :close="'multiple' in $attrs"
        outlined
        @click="data.select"
        @click:close="remove(data.item.id)"
      >
        {{ data.item.name }}
      </v-chip>

      <span v-else-if="data.index === 2" class="text-overline mx-2">
        <v-tooltip right>
          <template #activator="{ on, attrs }">
            <span v-on="on">+{{ value.length - 2 }} User(s)</span>
          </template>
          <div v-for="(item, i) in value.slice(2)" :key="i">
            <span v-if="isNaN(item)">{{ item }}</span>
            <span v-else>{{ findItem(item).name }}</span>
          </div>
        </v-tooltip>
      </span>
    </template>

    <template #item="data">
      <v-list-item-content>
        <v-list-item-title class="item-title" v-text="findItem(data.item).name" />
        <v-list-item-subtitle class="item-subtitle" v-text="findItem(data.item).email" />
      </v-list-item-content>
    </template>
  </v-autocomplete>
</template>

<script>
export default {
  props: {
    value: {
      type: Array | String,
    },
    url: {
      type: String,
      default: '/user/search/user',
    },
  },
  data() {
    return {
      data: [],
      memory: {},
      loading: false,
      search: null,
      token: null,
      timer: null,
    }
  },
  // init memory on both these hooks: otherwise weird stuff happens
  mounted() {
    this.initMemory()
  },
  beforeUpdate() {
    this.initMemory()
  },
  computed: {
    is_multiple() {
      return Array.isArray(this.value)
    },
    has_selected() {
      // multiple (or, multiple in $props)
      if (this.is_multiple) return this.value.length > 0
      // single
      else return this.value !== null
    },
    items() {
      if (this.data.length === 0 && !this.has_selected) return [{ header: 'Type To Search' }]

      let value = this.value
      if (!this.is_multiple) value = [this.value]

      value = value.map((item) => {
        return this.findItem(item)
      })

      return [{ header: 'Selected' }, ...value, { header: 'Search' }, ...this.data]
    },
  },
  methods: {
    getData() {
      if (this.token) this.token.cancel()

      if (!this.search) return (this.data = [])

      this.token = this.$axios.CancelToken.source()

      this.$emit('loading:start')
      this.loading = true

      this.$axios
        .$get(this.url, { params: { search: this.search } })
        .then((resp) => {
          this.data = [...resp]

          this.$emit('loading:end')
          this.loading = false
        })
        .catch((err) => {
          console.error(err)
          this.$emit('loading:end')
          this.loading = false
        })
        .finally(() => {
          this.$emit('loading:end')
          this.loading = false
        })
    },
    initMemory() {
      const key_len = Object.keys(this.memory).length
      // if value has data but memory is empty, populate memory
      if ((this.has_selected && key_len === 0) || key_len < this.value?.length) {
        let ids = this.value

        if (!this.is_multiple) {
          ids = [ids]
        }

        this.$axios
          .$post('/user/users', ids)
          .then((resp) => {
            resp.forEach((item) => {
              this.memory[item.id] = item
            })

            this.data = resp
          })
          .catch((err) => {
            console.error(err)
          })
      }
    },
    updateMemory(ids, items) {
      if (!this.is_multiple) ids = [ids]

      for (let i = 0; i < ids.length; i++) {
        const id = ids[i]
        const item = items.find((item) => item?.id === id)
        if (item) this.memory[id] = item
      }
    },
    findItem(id) {
      return this.memory.hasOwnProperty(id) ? this.memory[id] : id
    },
    remove(id) {
      const index = this.value.findIndex((x) => x === id)
      if (index >= 0) this.value.splice(index, 1)
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
  font-weight: 600;
}
</style>
