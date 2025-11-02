export default ({ app, store }, inject) => {
  inject('utils', {
    initArray(size, value = 0) {
      const array = []
      for (let ii = 0; ii < size; ii++) {
        array[ii] = value
      }

      return array
    },
    arrayToDict(array, key) {
      return array.reduce((obj, cur) => {
        return { ...obj, [cur[key]]: cur }
      }, {})
    },
    sortDict(obj) {
      return Object.keys(obj)
        .sort()
        .reduce((v, k) => {
          v[k] = obj[k]
          return v
        }, {})
    },
    filterObj(obj, callback) {
      return Object.fromEntries(Object.entries(obj).filter(([k, v]) => callback(k, v)))
    },
    fuzzySearch(haystack, needle) {
      let ii = 0
      let n = -1
      let jj

      haystack = haystack.toLowerCase()
      needle = needle.toLowerCase()

      for (; (jj = needle[ii++]); ) {
        if (!~(n = haystack.indexOf(jj, n + 1))) {
          return false
        }
      }
      return true
    },
    betterSelectFilter(item, search_text, item_text) {
      if (item.header || item.divider) {
        return true
      }
      return item_text.toLocaleLowerCase().includes(search_text.toLocaleLowerCase())
    },
    hexToRgb(hex) {
      const m = hex.match(/^#?([\da-f]{2})([\da-f]{2})([\da-f]{2})$/i)
      return [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)]
    },

    // -----------------------------------------
    // USER
    // -----------------------------------------
    getUserName(id) {
      if (!id) {
        return ''
      }
      const users = store.getters['lists/getUsers']
      return users.find((x) => x.id == id)?.name || ''
    },
  })
}
