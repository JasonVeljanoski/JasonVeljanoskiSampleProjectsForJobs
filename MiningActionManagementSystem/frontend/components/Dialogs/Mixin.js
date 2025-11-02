import BaseDialog from './Base.vue'

export default {
  // extends: BaseDialog,
  components: { BaseDialog },
  props: {},
  data() {
    return {}
  },
  methods: {
    open() {
      return this._open()
    },
    close() {
      return this._close()
    },
    save() {
      return this._close()
    },
    cancel() {
      return this._cancel()
    },
    // Default functions
    _open() {
      return this.$children[0].open()
    },
    _close(res = null) {
      return this.$children[0].close(res)
    },
    _cancel() {
      return this.$children[0].cancel()
    },
  },
}
