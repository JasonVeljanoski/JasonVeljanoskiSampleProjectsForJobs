<template>
  <v-dialog v-model="dialog" width="875">
    <v-carousel v-model="model" :show-arrows="images.length > 1">
      <v-carousel-item v-for="(image, ii) in images" :key="ii">
        <v-sheet height="100%" tile>
          <img class="fill-height" :src="image" />
        </v-sheet>
      </v-carousel-item>
    </v-carousel>
  </v-dialog>
</template>

<script>
export default {
  data() {
    return {
      model: 0,
      dialog: false,
      images: [],
    };
  },
  methods: {
    open(items) {
      this.images = items;
      this.dialog = true;

      return new Promise((resolve, reject) => {
        this.resolve = resolve;
        this.reject = reject;
      });
    },
    cancel() {
      this.resolve(false);
    },
  },
};
</script>

<style lang="scss" scoped></style>
