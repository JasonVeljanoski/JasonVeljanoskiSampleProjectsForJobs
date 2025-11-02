export default ({ app, store }, inject) => {
  inject('format', {
    round(value, dec = 2, pad = false) {
      if (!value) return value

      value = +(Math.round(value + `e+${dec}`) + `e-${dec}`)

      if (pad && dec > 0) {
        value = value.toString()

        if (!value.includes('.')) {
          value += '.'
          pad = dec
        } else {
          pad = dec - value.split('.')[1].length
        }

        for (let ii = 0; ii < pad; ii++) {
          value += '0'
        }
      }

      return value
    },
    commarize(number, dec = null, pad = false) {
      if (!number) {
        return number
      }

      if (dec !== null) {
        number = this.round(number, dec, pad)
      }

      const str = number.toString().split('.')
      str[0] = str[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',')
      return str.join('.')
    },
    percent(val, dec = 0) {
      if (val == null) return val

      return `${this.round(val * 100, dec)}%`
    },
    date(date) {
      if (!date) {
        return null
      }
      if (typeof date == 'string') {
        date = new Date(date)
      }

      let day = date.getDate()
      if (day < 10) day = '0' + day

      let month = date.getMonth() + 1
      if (month < 10) month = '0' + month

      const year = date.getFullYear()

      return `${day}/${month}/${year}`
    },
    time(date) {
      if (!date) {
        return null
      }

      if (typeof date == 'string') {
        date = new Date(date)
      }

      let hours = date.getHours()
      if (hours < 10) hours = '0' + hours

      let mins = date.getMinutes()
      if (mins < 10) mins = '0' + mins

      // let secs = date.getSeconds()
      // if (secs < 10) secs = '0' + secs

      return `${hours}:${mins}`
    },
    dateTime(date) {
      if (!date) {
        return null
      }

      return `${this.date(date)} ${this.time(date)}`
    },
    initDate(date_string) {
      return date_string ? new Date(date_string) : null
    },
    toISO(x) {
      if (typeof x == 'string') {
        x = new Date(x)
      }

      const temp = x.toLocaleDateString('en-GB').split('/')
      return `${temp[2]}-${temp[1]}-${temp[0]}`
    },
  })
}
