export default ({ app, store }, inject) => {
  inject('utils', {
    // -----------------------------------------
    // DATE
    // -----------------------------------------
    daysDiff(date, start) {
      start = new Date(start).setHours(0, 0, 0, 0)
      const plan = new Date(date).setHours(0, 0, 0, 0)

      const offset = (plan - start) / (1000 * 60 * 60 * 24)

      return offset
    },
    // -----------------------------------------
    // USER
    // -----------------------------------------
    getUserName(id) {
      if (!id) {
        return ''
      }
      const users = store.getters['user/getUsers']
      return users.find((x) => x.id == id)?.name || ''
    },
    getUserInitials(email) {
      if (!email) {
        return 'N/A'
      }
      const users = store.getters['user/getUsers']
      const user = users.find((x) => x.email == email)
      return user.first_name.charAt(0) + '.' + user.last_name.charAt(0)
    },
    getAuthToken() {
      let token = app.$auth.strategy.token.get()
      token = token ? token.substr(7) : null
      return token
    },
    getJWT() {
      const token = this.getAuthToken()
      if (!token) return null

      return JSON.parse(window.atob(token.split('.')[1]))
    },
    // -----------------------------------------
    // TASK AND ARRAYS
    // -----------------------------------------
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
        .reduce((v, k) => ((v[k] = obj[k]), v), {})
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
  })
}
