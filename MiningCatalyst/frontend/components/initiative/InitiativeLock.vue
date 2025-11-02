<template>
  <div class="lock-container">
    <div class="lock">
      <v-icon color="#bababa" v-if="locked"> mdi-circle-small </v-icon>
      <v-icon color="#bababa" v-else> mdi-chevron-up </v-icon>
      <hr color="#e0e0e0" />

      <v-progress-circular v-if="loading" indeterminate :width="5" :size="50" class="mt-2 mb-2" />
      <v-icon color="success" v-else-if="locked" class="pt-2 pb-2"> mdi-lock </v-icon>
      <v-icon v-else class="pb-2 pt-2"> mdi-lock-open </v-icon>

      <hr color="#e0e0e0" />
      <v-icon color="#bababa"> mdi-chevron-down </v-icon>
    </div>
    <div class="inputs">
      <slot name="inputs" />
    </div>
  </div>
</template>

<script>
export default {
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
    locked: {
      type: Boolean,
      default: false,
    },
  },
}
</script>

<style lang="scss" scoped>
.lock-container .lock {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-right: 16px;
  width: 100%;
}

.lock-container .inputs {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.lock-container {
  display: flex;

  .lock {
    width: 20px;

    hr {
      height: 100%;
    }

    hr:first-child {
      margin-bottom: 12px;
    }

    hr:last-child {
      margin-top: 12px;
    }
  }
}
</style>
