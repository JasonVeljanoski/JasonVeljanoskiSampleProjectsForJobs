<template>
  <v-menu>
    <template #activator="{ on, attrs }">
      <e-icon-btn v-bind="attrs" class="mx-auto" tooltip="Metadata" v-on="on"> mdi-dots-vertical </e-icon-btn>
    </template>

    <v-card outlined>
      <small v-if="Object.keys(value).length === 0" class="mx-4">No metadata.</small>
      <v-simple-table v-else dense>
        <thead>
          <tr>
            <th>Key</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(v, k) in value">
            <td class="text-capitalize">{{ k.replaceAll('_', ' ') }}</td>
            <td>{{ v }}</td>
          </tr>
        </tbody>
      </v-simple-table>
    </v-card>
  </v-menu>
</template>

<script>
export default {
  props: {
    value: { type: Object, default: null },
  },
}
</script>

<style lang="scss" scoped></style>
