<template>
  <div>
    <div v-if="editor" class="d-flex">
      <div v-for="(group, key) in handles" :key="key" v-bind="{ ...group.props }" class="mr-2 mb-2 toggle-wrapper">
        <template v-for="(item, ii) in group.values">
          <v-btn
            v-if="item.callback"
            :key="ii"
            :class="{ 'is-active': editor.isActive(item.command, item?.args) }"
            :disabled="!item.callback"
            tile
            text
            dense
            small
            class="button-toggle"
            @click="item.callback"
          >
            <v-icon small>{{ item.icon }}</v-icon>
          </v-btn>
        </template>
      </div>

      <!-- <v-btn tile text dense small outlined rounded class="button-toggle" @click="insertTable">
        <v-icon small>mdi-table</v-icon>
      </v-btn> -->

      <color-picker
        :value="editor.getAttributes('textStyle').color"
        icon="mdi-format-color-text"
        :swatches="swatches"
        show-swatches
        @input="editor.chain().focus().setColor($event).run()"
      />

      <div class="ml-2 mb-2 toggle-wrapper">
        <v-btn
          v-if="toggleUndo"
          :class="{ 'is-active': editor.isActive('undo') }"
          :disabled="!toggleUndo"
          tile
          text
          dense
          small
          class="button-toggle"
          @click="toggleUndo"
        >
          <v-icon small>mdi-undo</v-icon>
        </v-btn>
        <v-btn
          v-if="toggleRedo"
          :class="{ 'is-active': editor.isActive('redo') }"
          :disabled="!toggleRedo"
          tile
          text
          dense
          small
          @click="toggleRedo"
        >
          <v-icon small>mdi-redo</v-icon>
        </v-btn>
      </div>
    </div>
    <editor-content
      :editor="editor"
      :class="{ markdown_light: !$vuetify.theme.dark, markdown_dark: $vuetify.theme.dark }"
      class="editor"
      :rules="$attrs.rules"
    />

    <!-- HIDDEN ELEMENTS -->
    <input ref="fileInput" type="file" accept="image/*" style="display: none" @change="addImage" />
  </div>
</template>

<script>
import { Editor, EditorContent } from '@tiptap/vue-2'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Typography from '@tiptap/extension-typography'
import TextAlign from '@tiptap/extension-text-align'
import Heading from '@tiptap/extension-heading'
import { Color } from '@tiptap/extension-color'
import TextStyle from '@tiptap/extension-text-style'
import Link from '@tiptap/extension-link'
import Table from '@tiptap/extension-table'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import TableRow from '@tiptap/extension-table-row'
import Image from '@tiptap/extension-image'

export default {
  components: {
    EditorContent,
  },
  props: {
    value: {
      type: String,
      default: '',
    },
  },

  data() {
    return {
      editor: null,
      swatches: [
        ['#000000', '#4CAF50'],
        ['#212e4d', '#FFC107'],
        ['#355bb7', '#E53935'],
      ],
      handles: {
        format: {
          props: {
            multiple: true,
          },
          values: [
            { icon: 'mdi-format-bold', command: 'bold', callback: this.toggleBold },
            { icon: 'mdi-format-italic', command: 'italic', callback: this.toggleItalic },
            { icon: 'mdi-format-underline', command: 'underline', callback: this.toggleUnderline },
            { icon: 'mdi-format-strikethrough', command: 'strike', callback: this.toggleStrike },
          ],
        },
        heading: {
          props: {
            multiple: false,
          },
          values: [
            { icon: 'mdi-format-header-1', command: 'heading', args: { level: 1 }, callback: this.toggleHeading(1) },
            { icon: 'mdi-format-header-2', command: 'heading', args: { level: 2 }, callback: this.toggleHeading(2) },
          ],
        },
        lists: {
          props: {
            multiple: false,
          },
          values: [
            { icon: 'mdi-format-list-bulleted', command: 'bulletList', callback: this.toggleBulletList },
            { icon: 'mdi-format-list-numbered', command: 'orderedList', callback: this.toggleOrderedList },
          ],
        },
        links: {
          props: {
            multiple: false,
          },
          values: [
            { icon: 'mdi-link', command: 'link', callback: this.setLink },
            { icon: 'mdi-link-off', command: 'unlink', callback: this.unsetLink },
          ],
        },
        // image: {
        //   values: [{ icon: 'mdi-image-outline', command: 'image', callback: this.openFileInput }],
        // },

        // color: {
        //   props: {
        //     multiple: false,
        //   },
        //   values: [
        //     {
        //       icon: 'mdi-format-color-text',
        //       command: 'textColor',
        //       args: { color: 'red' },
        //       callback: this.toggleTextColor,
        //     },
        //   ],
        // },
        // history: {
        //   props: {
        //     multiple: false,
        //   },
        //   values: [
        //     { icon: 'mdi-undo', command: 'undo', callback: this.toggleUndo },
        //     { icon: 'mdi-redo', command: 'redo', callback: this.toggleRedo },
        //   ],
        // },
      },
    }
  },

  watch: {
    value(value) {
      // HTML
      const isSame = this.editor.getHTML() === value

      // JSON
      // const isSame = JSON.stringify(this.editor.getJSON()) === JSON.stringify(value)

      if (isSame) {
        return
      }

      this.editor.commands.setContent(value, false)
    },
  },

  mounted() {
    this.editor = new Editor({
      content: this.value,
      extensions: [
        StarterKit,
        Underline,
        Typography,
        TextAlign,
        Heading,
        Color,
        TextStyle,
        Link,
        Table.configure({
          resizable: true,
        }),
        TableRow,
        TableHeader,
        TableCell,
        Image,
      ],
      onUpdate: () => {
        // HTML
        this.$emit('input', this.editor.getHTML())

        // JSON
        // this.$emit('input', this.editor.getJSON())
      },
    })
  },

  beforeDestroy() {
    this.editor.destroy()
  },
  methods: {
    // FORMAT
    toggleBold() {
      this.editor.chain().focus().toggleBold().run()
    },
    toggleItalic() {
      this.editor.chain().focus().toggleItalic().run()
    },
    toggleUnderline() {
      this.editor.chain().focus().toggleUnderline().run()
    },
    toggleStrike() {
      this.editor.chain().focus().toggleStrike().run()
    },

    // HEADING
    toggleHeading(level) {
      return () => {
        this.editor.chain().focus().toggleHeading({ level }).run()
      }
    },

    // LISTS
    toggleBulletList() {
      this.editor.chain().focus().toggleBulletList().run()
    },
    toggleOrderedList() {
      this.editor.chain().focus().toggleOrderedList().run()
    },

    // COLOR
    toggleTextColor(e) {
      this.editor.chain().focus().toggleTextColor({ color: e }).run()
    },

    // LINK
    setLink() {
      const previousUrl = this.editor.getAttributes('link').href
      const url = window.prompt('URL', previousUrl)

      // cancelled
      if (url === null) {
        return
      }

      // emptyaddImage
      if (url === '') {
        this.editor.chain().focus().extendMarkRange('link').unsetLink().run()

        return
      }

      // update link
      this.editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
    },
    unsetLink() {
      this.editor.chain().focus().unsetLink().run()
    },

    // HISTORY
    toggleUndo() {
      this.editor.chain().focus().undo().run()
    },
    toggleRedo() {
      this.editor.chain().focus().redo().run()
    },

    // IMAGE
    openFileInput() {
      this.$refs.fileInput.click()
    },
    addImage(event) {
      const file = event.target.files[0]

      // Assuming that "file" is a valid File object
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => {
        const base64String = reader.result
        this.editor.chain().focus().setImage({ src: base64String }).run()
      }
    },

    // TABLE
    insertTable() {
      this.editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
    },
    addColumnBefore() {
      this.editor.chain().focus().addColumnBefore().run()
    },
    addColumnAfter() {
      this.editor.chain().focus().addColumnAfter().run()
    },
    deleteColumn() {
      this.editor.chain().focus().deleteColumn().run()
    },
    addRowBefore() {
      this.editor.chain().focus().addRowBefore().run()
    },
    addRowAfter() {
      this.editor.chain().focus().addRowAfter().run()
    },
    deleteRow() {
      this.editor.chain().focus().deleteRow().run()
    },
    toggleHeaderCell() {
      this.editor.chain().focus().toggleHeaderCell().run()
    },
    mergeOrSplit() {
      this.editor.chain().focus().mergeOrSplit().run()
    },
  },
}
</script>

<style lang="scss" scoped>
.is-active {
  color: var(--v-primary-base) !important;
}

.toggle-wrapper {
  border: 1px solid var(--v-accent-base);
  border-radius: 5px;
}

.button-toggle:not(:last-child) {
  border-right: 1px solid var(--v-accent-base);
}

::v-deep {
  .ProseMirror {
    min-height: 150px;
    border: solid 1px var(--v-accent2-base);
    border-radius: 5px;
    padding: 10px;

    img {
      max-width: 250px;
      display: block;
      margin-left: auto;
      margin-right: auto;
      margin-bottom: 10px;
    }
  }

  // TABLE STYLES
  .ProseMirror {
    table {
      border-collapse: collapse;
      table-layout: fixed;
      width: 100%;
      margin: 0;
      overflow: hidden;

      td,
      th {
        min-width: 1em;
        border: 2px solid #ced4da;
        padding: 3px 5px;
        vertical-align: top;
        box-sizing: border-box;
        position: relative;

        > * {
          margin-bottom: 0;
        }
      }

      th {
        font-weight: bold;
        text-align: left;
        background-color: #f1f3f5;
      }

      .selectedCell:after {
        z-index: 2;
        position: absolute;
        content: '';
        left: 0;
        right: 0;
        top: 0;
        bottom: 0;
        background: rgba(200, 200, 255, 0.4);
        pointer-events: none;
      }

      .column-resize-handle {
        position: absolute;
        right: -2px;
        top: 0;
        bottom: -2px;
        width: 4px;
        background-color: #adf;
        pointer-events: none;
      }

      p {
        margin: 0;
      }
    }
  }

  .tableWrapper {
    padding: 1rem 0;
    overflow-x: auto;
  }

  .resize-cursor {
    cursor: ew-resize;
    cursor: col-resize;
  }
}
</style>
