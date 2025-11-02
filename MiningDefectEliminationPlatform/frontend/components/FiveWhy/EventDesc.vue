<template>
  <div class="root">
    <v-card class="mx-auto" v-bind="$bind.card" tile>
      <p class="card-title">Event Description</p>
      <v-textarea
        v-bind="{ ...$bind.textarea, ...$attrs, ...$props }"
        hint="Briefly describe the event"
        v-on="$listeners"
      />
    </v-card>
  </div>
</template>

<script>
export default {};
</script>

<style scoped>
.root {
  display: flex;
  align-items: center;
  flex-direction: column;
}

.v-card {
  width: 100%;
  padding: 15px;
  padding-bottom: 0;
}

.card-title {
  font-size: 14pt;
  padding-top: 5px;
  color: var(--v-primary-base);
}
</style>
