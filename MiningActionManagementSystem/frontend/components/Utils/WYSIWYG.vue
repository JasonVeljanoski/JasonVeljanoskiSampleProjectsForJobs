<template>
  <tiptap-vuetify
    v-model="content"
    v-bind="{ ...$attrs, ...$props }"
    :extensions="extensions"
    :card-props="card_props"
    :toolbar-attributes="toolbar_attributes"
    class="html_render"
    @input="$emit('input', $event.content)"
  >
    <template #toolbar-after>
      <v-divider />
    </template>

    <template #footer>
      <v-divider v-if="has_footer_slot" />
      <v-card-actions>
        <slot name="card:footer" />
      </v-card-actions>
    </template>
  </tiptap-vuetify>
</template>

<script>
import {
  TiptapVuetify,
  Heading,
  Bold,
  Italic,
  Strike,
  Underline,
  BulletList,
  OrderedList,
  ListItem,
  // Link,
  Blockquote,
  HardBreak,
  HorizontalRule,
  History,
} from 'tiptap-vuetify'

export default {
  components: { TiptapVuetify },
  data() {
    return {
      extensions: [
        Bold,
        Italic,
        Underline,
        Strike,
        [
          Heading,
          {
            options: {
              levels: [1, 2, 3],
            },
          },
        ],
        ListItem,
        BulletList,
        OrderedList,
        Blockquote,
        // Link,
        HorizontalRule,
        HardBreak,
        History,
      ],
      content:
        '<h1>Sample title</h1><h2>Sample Subtitle</h2><p>Sample text</p><ul><li><p>item one</p></li><li><p>item two</p></li><li><p>item three</p></li></ul>',
      card_props: {
        outlined: true,
        dense: true,
        elevation: 0,
      },
      toolbar_attributes: {
        color: '',
        rounded: true,
      },
    }
  },
  computed: {
    content_json() {
      return JSON.stringify(this.content)
    },
    has_footer_slot() {
      return this.$slots['card:footer']
    },
  },
}
</script>
