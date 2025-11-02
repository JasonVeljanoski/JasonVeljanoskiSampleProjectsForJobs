<template>
  <div class="root" ref="scrollToMe" :class="{ 'last-node': depth > 1 }">
    <base-section title="Cause">
      <!-- REMOVE NODE BUTTON -->
      <div class="d-flex">
        <v-spacer />
        <e-icon-btn
          v-if="can_remove"
          tooltip="Remove"
          class="mt-n12"
          @click="$emit('remove', response)"
        >
          mdi-close
        </e-icon-btn>
      </div>

      <!-- TEXTAREAS -->
      <v-form ref="cause-form">
        <h4>Description</h4>
        <v-textarea
          :height="
            been_split && response.cause != null && response.cause.length >= 215
              ? 130
              : 120
          "
          v-model="response.cause"
          v-bind="$bind.textarea"
          :rules="[
            $form.required(response.cause),
            $form.length(response.cause, max_word_count),
          ]"
          :counter="max_word_count"
          hideDetails="auto"
          @input="$emit('cause_change')"
        />

        <h4>Evidence</h4>
        <v-textarea
          :height="
            been_split &&
            response.reason != null &&
            response.reason.length >= 290
              ? 230
              : 140
          "
          v-model="response.reason"
          v-bind="$bind.textarea"
          :rules="[
            $form.required(response.reason),
            $form.length(response.reason, max_word_count_evidence),
          ]"
          :counter="max_word_count_evidence"
          hideDetails="auto"
          @input="$emit('cause_change')"
        />
      </v-form>

      <h4>Images</h4>
      <image-input
        :images="response.files"
        :img-disabled="response.files.length >= max_file_count"
        :img-rules="[
          $form.arr_non_empty(response.files),
          $form.arr_len_lim(response.files, max_file_count),
        ]"
        :image-style="{ maxWidth: max_file_count == 1 ? '200px' : '300px' }"
      />

      <!-- ADD MORE CAUSES -->
      <div class="d-flex mt-4">
        <v-spacer />
        <v-btn
          class="add-btn"
          v-if="can_add"
          @click="
            addChild();
            scrollToChild('scrollToMe');
          "
          v-bind="$bind.btn"
        >
          <v-icon left>mdi-plus</v-icon>
          <span>Why?</span>
        </v-btn>
      </div>
    </base-section>

    <!-- CHILD RECURSIVE COMPONENT -->
    <div class="children" :class="children_class">
      <cause-card
        v-for="child in response.children_responses"
        @remove="removeNodeAndChildren"
        @cause_change="$emit('cause_change')"
        ref="children"
        :key="child.id"
        :response="child"
        :depth="depth + 1"
        :been_split="been_split"
        :max_word_count="250"
        :max_word_count_evidence="500"
        :max_file_count="been_split ? 1 : 2"
      />
    </div>
  </div>
</template>

<script>
import ImageInput from "@/components/Utils/ImageInput";
import VImageInput from "vuetify-image-input";

export default {
  name: "cause-card",
  components: {
    ImageInput,
    VImageInput,
  },
  props: {
    response: { Object },
    depth: { type: Number, default: 1 },
    been_split: { type: Boolean, default: false },
    max_word_count: { type: Number, default: 250 },
    max_word_count_evidence: { type: Number, default: 500 },
    max_file_count: { type: Number, default: 2 },
  },
  data() {
    return {
      tmp_img: null,
      dialog: false,
    };
  },
  computed: {
    children_class() {
      if (this.response.children_responses.length > 1) {
        return "multi-children";
      } else if (this.response.children_responses.length == 1) {
        return "single-children";
      }
      return "no-children";
    },
    can_add() {
      // cannot have more than 5 whys
      // tree height must be less than 5
      if (this.depth >= 5) {
        return false;
      }
      // cannot split responses more than once
      // width of tree must be max of 2
      if (this.been_split && this.response.children_responses.length > 0) {
        return false;
      }
      return true;
    },
    can_remove() {
      return this.depth > 1;
    },
    can_add_img() {
      return this.response.files.length < this.max_file_count;
    },
  },
  methods: {
    addImage() {
      if (this.tmp_img) {
        this.response.files.push(this.tmp_img);
        this.dialog = false;
      }
      this.tmp_img = null;
    },
    removeImage(img) {
      this.response.files.splice(this.response.files.indexOf(img), 1);
    },
    addChild() {
      this.response.children_responses.push({
        id: null,
        cause: null,
        reason: null,
        files: [],
        children_responses: [],
      });

      this.$emit("cause_change");
    },
    removeNodeAndChildren(sub_response_tree) {
      if (!confirm("Are you sure you want to delete this node?")) {
        return;
      }

      let index = this.response.children_responses.indexOf(sub_response_tree);

      if (index > -1) {
        // garbage collection will take care of hanging refs
        this.response.children_responses.splice(index, 1);
      }
      return;
    },
    scrollToChild() {
      this.$nextTick(() => {
        let child = this.$refs.children[0];
        child.$refs.scrollToMe.scrollIntoView({
          behavior: "smooth",
        });
      });
    },
  },
};
</script>

<style lang="scss" scoped>
$line: solid thin var(--v-accent-base);
$children-margin: 50px;

.root {
  display: flex;
  align-items: center;

  flex-direction: column;
  margin-top: -1px;
}

.last-node {
  position: relative;
  &::before {
    content: "";
    position: absolute;
    top: 0;
    bottom: $children-margin/2;
    left: 50%;
    border-left: $line;
  }
}

.children {
  $children-gap: 32px;
  display: flex;
  flex-direction: row;
  margin-top: $children-margin;
  width: 100%;
  gap: $children-gap;
  position: relative;

  > * {
    flex-grow: 1;
  }

  &.single-children::before {
    content: "";
    position: absolute;
    height: $children-margin/2;
    top: -$children-margin/2;
    left: 50%;
    border-left: $line;
  }

  &.multi-children::before {
    content: "";
    position: absolute;
    height: $children-margin/2;
    top: -$children-margin/2;
    left: calc(25% - #{$children-gap/4});
    right: calc(25% - #{$children-gap/4});
    border: $line;
    border-width: 1px 1px 0 1px;
  }

  &::after {
    content: "";
    position: absolute;
    height: $children-margin/2;
    top: -50px;
    left: 50%;
    border-left: $line;
  }
}

.add-img {
  cursor: pointer;
  text-align: right;

  &:hover {
    text-decoration: underline;
    color: var(--v-primary-base);
  }
}

.dialog-container {
  background-color: var(--v-background-base);
  overflow: hidden;
  padding: 10px;
}

.img-wrapper {
  display: flex;
  justify-content: space-evenly;
}

.img-item {
  display: flex;
  border-radius: 10px;
  overflow: hidden;
}

.remove-img {
  position: relative;
  margin-left: -27px;
  margin-top: 7px;
  background-color: var(--v-accent-base);

  &:hover {
    opacity: 0.4;
  }
}
</style>
