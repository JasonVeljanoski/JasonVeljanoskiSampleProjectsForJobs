<template>
  <div class="grid">
    <v-card width="700px">
      <v-card-title>
        <h3>Impact Dropdown (Multiple)</h3>
      </v-card-title>

      <v-card-text>
        <initiative-lock :locked="false" :loading="loading.floc || loading.equipment">
          <template #inputs>
            <initiative-input
              title="Functional Locations"
              v-model="selected_flocs"
              ref="floc"
              class="mb-4"
              url="/floc"
              item-text="node"
              :parent_ref="$refs.equipment"
              @get:children="fromFlocsSetEquipments"
              @loading:start="$set(loading, 'floc', true)"
              @loading:end="$set(loading, 'floc', false)"
            >
              <template #chip-text="{ item }">
                {{ item.node }}
              </template>

              <template #item="{ item }">
                <v-list-item-content>
                  <v-list-item-title> {{ item.node }} </v-list-item-title>
                  <v-list-item-subtitle> {{ item.equipment_description }}</v-list-item-subtitle>
                </v-list-item-content>
              </template>
            </initiative-input>

            <initiative-input
              v-model="selected_equipment"
              title="Equipments"
              ref="equipment"
              url="/equipment"
              item-text="description"
              :parent_ref="$refs.floc"
              @get:children="fromEquipmentsSetFlocs"
              @loading:start="$set(loading, 'equipment', true)"
              @loading:end="$set(loading, 'equipment', false)"
            >
              <template #chip-text="{ item }">
                {{ item.description }}
              </template>

              <template #item="{ item }">
                <v-list-item-content>
                  <v-list-item-title> {{ item.description }} </v-list-item-title>
                  <v-list-item-subtitle> {{ item.functional_location }}</v-list-item-subtitle>
                </v-list-item-content>
              </template>
            </initiative-input>
          </template>
        </initiative-lock>

        <v-divider class="mt-4 mb-4" />

        <h4>Flocs :</h4>
        {{ selected_flocs }}

        <h4>Equipment:</h4>
        {{ selected_equipment }}
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import InitiativeLock from '@/components/initiative/InitiativeLock.vue'
import InitiativeInput from '@/components/initiative/InitiativeInput.vue'

export default {
  components: {
    InitiativeLock,
    InitiativeInput,
  },
  data() {
    return {
      loading: {},

      selected_flocs: [],
      selected_equipment: [],

      flocToken: null,
      flocTimer: null,

      equipmentToken: null,
      equipmentTimer: null,
    }
  },

  methods: {
    fromFlocsSetEquipments() {
      clearTimeout(this.flocTimer)

      this.flocTimer = setTimeout(() => {
        if (this.flocToken) this.flocToken.cancel()

        const floc_ids = this.selected_flocs.map((floc) => floc.id)

        this.$axios.$post('/floc/equipment', floc_ids).then((resp) => {
          this.$refs.equipment.setData(resp)
        })
      }, 500)
    },
    fromEquipmentsSetFlocs() {
      clearTimeout(this.equipmentTimer)

      this.equipmentTimer = setTimeout(() => {
        if (this.equipmentToken) this.equipmentToken.cancel()

        const equipment_ids = this.selected_equipment.map((equipment) => equipment.id)

        this.$axios.$post('/equipment/floc', equipment_ids).then((resp) => {
          this.$refs.floc.setData(resp)
        })
      }, 500)
    },
  },
}
</script>

<style lang="scss" scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  height: 100%;
}

.grid-col-span-2 {
  grid-column: span 2;
}

.grid-row-span-2 {
  grid-row: span 2;
}

.grid-columns-mobile {
  grid-template-columns: repeat(1, 1fr);
}
</style>
