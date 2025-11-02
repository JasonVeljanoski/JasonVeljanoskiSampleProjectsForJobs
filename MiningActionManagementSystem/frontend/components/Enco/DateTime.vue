<template>
  <v-text-field
    ref="global"
    v-model="trash"
    :class="[inline ? 'mt-0 pt-0' : null, focused ? 'v-input--is-focused' : null]"
    :style="{
      minWidth: (time ? 9.5 : 6.25) + (editable && gui ? 1.5 : 0) + 'em',
      paddingRight: '0em',
    }"
    class="date-time-root"
    style="pointer-events: none"
    tabindex="-1"
    v-bind="{ ...parentBind }"
    :append-icon="editable && gui ? 'mdi-calendar' : parentBind['append-icon']"
    :error-messages="errors"
    readonly
    v-on="$listeners"
    @click:clear="cleared"
    @click:append="gui ? showGUI() : null"
  >
    <template #prepend>
      <div class="custom-date">
        <input
          ref="day"
          v-model="day"
          class="date_input input_day"
          type="number"
          :style="{ width: '1.2em' }"
          hide-details
          placeholder="dd"
          min="1"
          max="31"
          :disabled="disabled"
          :readonly="readonly"
          @keydown="checkVal2('day', ...arguments)"
          @input="checkVal('day')"
          @focus="focused = true"
          @blur="makeDate('day', ...arguments)"
        />
        <span class="divider">/</span>
        <input
          ref="month"
          v-model="month"
          class="date_input input_month"
          type="number"
          :style="{ width: month ? '1.2em' : '1.8em' }"
          hide-details
          placeholder="mm"
          min="1"
          max="12"
          :disabled="disabled"
          :readonly="readonly"
          @keydown="checkVal2('month', ...arguments)"
          @input="checkVal('month')"
          @focus="focused = true"
          @blur="makeDate('month', ...arguments)"
        />
        <span class="divider">/</span>
        <input
          ref="year"
          v-model="year"
          class="date_input input_year"
          type="number"
          :style="{ width: year ? '2.2em' : '2em' }"
          placeholder="yyyy"
          hide-details
          min="1900"
          max="2999"
          :disabled="disabled"
          :readonly="readonly"
          @keydown="checkVal2('year', ...arguments)"
          @input="checkVal('year')"
          @focus="focused = true"
          @blur="makeDate('year', ...arguments)"
        />
        <template v-if="time">
          <span class="divider mr-1"> &nbsp; </span>
          <input
            ref="hour"
            v-model="hour"
            class="date_input input_hour"
            type="number"
            :style="{ width: '1.2em' }"
            placeholder="hh"
            hide-details
            min="0"
            max="23"
            :disabled="disabled"
            :readonly="readonly"
            @keydown="checkVal2('hour', ...arguments)"
            @input="checkVal('hour')"
            @focus="focused = true"
            @blur="makeDate('hour', ...arguments)"
          />
          <span class="divider">:</span>
          <input
            ref="min"
            v-model="min"
            class="date_input input_min"
            type="number"
            :style="{ width: min ? '1.2em' : '1.8em' }"
            placeholder="mm"
            hide-details
            min="0"
            max="59"
            :disabled="disabled"
            :readonly="readonly"
            @keydown="checkVal2('min', ...arguments)"
            @input="checkVal('min')"
            @focus="focused = true"
            @blur="makeDate('min', ...arguments)"
          />
          <template v-if="seconds">
            <span class="divider">:</span>
            <input
              ref="sec"
              v-model="sec"
              class="date_input input_sec"
              type="number"
              :style="{ width: '1.8em' }"
              placeholder="ss"
              hide-details
              min="0"
              max="59"
              :disabled="disabled"
              :readonly="readonly"
              @keydown="checkVal2('sec', ...arguments)"
              @input="checkVal('sec')"
              @focus="focused = true"
              @blur="makeDate('sec', ...arguments)"
            />
          </template>
        </template>
      </div>
    </template>
    <template slot="append">
      <div v-show="quick_select" style="pointer-events: all">
        <e-btn :disabled="disabled" class="e-btn" tooltip="+ 1 week" icon @click="nowPlusDays(7)"> 1W </e-btn>
        <e-btn :disabled="disabled" class="e-btn" tooltip="+ 2 weeks" icon @click="nowPlusDays(7 * 2)"> 2W </e-btn>
        <e-btn :disabled="disabled" class="e-btn" tooltip="+ 4 weeks" icon @click="nowPlusDays(7 * 4)"> 4W </e-btn>
      </div>
    </template>
  </v-text-field>
</template>
<script>
export default {
  name: 'FormDate',

  inject: {
    form: {
      default: null,
    },
  },
  inheritAttrs: false,
  props: {
    // JASON ADDED
    quick_select: {
      type: Boolean,
      default: false,
      required: false,
    },
    show_validate: {
      type: Boolean,
      default: true,
      required: false,
    },
    // ORIGINAL
    date: {
      type: Boolean,
      default: true,
    },
    time: {
      type: Boolean,
      default: true,
    },
    value: {
      type: Date,
      default: null,
    },
    minStep: {
      type: Number,
      default: 1,
    },
    rules: {
      type: Array,
      default: () => [],
    },
    gui: {
      type: Boolean,
      default: false,
    },
    inline: {
      type: Boolean,
      default: false,
    },
    seconds: {
      type: Boolean,
      default: false,
    },
    noOffset: {
      type: Boolean,
      default: false,
    },
    minDate: {},
    maxDate: {},
  },
  data() {
    return {
      day: null,
      month: null,
      year: null,
      hour: null,
      min: null,
      sec: null,
      focus: null,
      arrow: false,
      trash: ' ',
      innerValue: null,
      isoValue: null,
      loading: true,
      errors: null,
      focused: false,
    }
  },
  computed: {
    parentBind() {
      const temp = { ...this.$attrs, ...this.$props }

      if (this.disabled || this.readonly) {
        temp.clearable = false
      }

      temp.rules = []
      return temp
    },
    disabled() {
      return this.$attrs.disabled !== undefined && this.$attrs.disabled !== false
    },
    readonly() {
      return this.$attrs.readonly !== undefined && this.$attrs.readonly !== false
    },
    editable() {
      return !this.disabled && !this.readonly
    },
    hasError() {
      return this.errors && this.errors.length > 0
    },
  },
  watch: {
    value(val) {
      this.setValue()
      this.trash = ' '
    },
  },
  created() {
    this.form && this.form.register(this)

    this.loading = true
    this.setValue()
    this.$nextTick(() => {
      this.loading = false
    })
  },

  beforeDestroy() {
    this.form && this.form.unregister(this)
  },
  methods: {
    // JASONS
    nowPlusDays(days) {
      let date = new Date()
      date = new Date(date.setDate(date.getDate() + days))

      date.setHours(0, 0, 0, 0)

      this.$emit('input', date)
      this.$emit('change', date)
    },
    // ORIGINAL
    validate() {
      const val = this.value
      const errors = []

      let empty = 0
      const fields = []

      if (this.date) {
        fields.push('day', 'month', 'year')
      }
      if (this.time) {
        fields.push('hour', 'min')

        if (this.seconds) {
          fields.push('sec')
        }
      }

      fields.forEach((field) => {
        if (!this[field]) {
          empty++
        }
      })

      if ((this.minDate && val < this.minDate) || (this.maxDate && this.maxDate < val)) {
        errors.push('Date out of Range')
      }

      // let needed = fields.length

      // if (0 < empty && empty <= needed) {
      // 	errors.push('Date is not complete')
      // }

      this.rules.forEach((rule) => {
        const temp = rule(val)

        if (temp !== true) {
          errors.push(temp)
        }
      })

      if (errors.length == 0) {
        this.errors = null
      } else {
        this.errors = errors
      }

      this.$emit('errors', this.errors)

      return !this.hasError
    },
    reset() {},
    resetValidation() {
      this.errors = null
    },
    setValue() {
      const val = this.value
      if (val) {
        const offset = val.getTimezoneOffset()
        const temp = new Date(val.getTime() - offset * 60 * 1000)
        const iso = temp.toISOString()

        this.year = iso.slice(0, 4)
        this.month = iso.slice(5, 7)
        this.day = iso.slice(8, 10)
        this.hour = this.time ? iso.slice(11, 13) : 0
        this.min = this.time ? iso.slice(14, 16) : 0
        this.sec = this.time ? iso.slice(17, 19) : 0

        this.isoValue = this.value.toISOString()
      } else {
        this.day = null
        this.month = null
        this.year = null
        this.hour = null
        this.min = null
        this.sec = null
      }
    },
    cleared() {
      this.$emit('input', null)
      this.$emit('change')

      this.$nextTick(() => {
        this.trash = ' '
        this.$refs.day.focus()
      })
    },
    checkVal2(field_name, event) {
      switch (event.key) {
        // If they used the arrow keys then handle them specially
        case 'ArrowUp':
        case 'ArrowDown':
          this.arrow = true
          break
        case 'ArrowLeft':
          this.arrow = true
          break
        case 'ArrowRight':
          this.arrow = true
          break
        default:
          this.arrow = false
      }
    },
    checkVal(field_name) {
      const next_dict = {
        day: 'month',
        month: 'year',
        year: 'hour',
        hour: 'min',
        min: null,
      }

      if (this.seconds) {
        next_dict.min = 'sec'
        next_dict.sec = null
      }

      const val = this[field_name]
      const ref = this.$refs[field_name]

      const max = ref.max

      if (!this.arrow) {
        if (val.length >= max.length) {
          if (parseInt(val) > parseInt(max)) {
            this[field_name] = max
          }

          const next = next_dict[field_name]
          if (next && this.$refs[next]) {
            this.$refs[next].focus()
            this.$refs[next].select()
          } else {
            // this.focus = null
            ref.blur()
          }
        }
      }
      this.arrow = false
    },
    makeDate(field_name, event, b) {
      this.focused = false

      let val = this[field_name]
      // TODO show validation errors
      if (val == null || val == '') {
        if (!this.day && !this.month && !this.year && !this.hour && !this.min && (!this.seconds || !this.sec)) {
          this.submitNew(null)
        }
        return
      }
      const ref = this.$refs[field_name]

      if (field_name == 'year') {
        if (val.toString().length == 2) {
          this.year = +this.year + 2000
          val = this.year
        }
      }

      const max = parseInt(ref.max)
      for (let ii = val.toString().length; ii < max.toString().length; ii++) {
        this[field_name] = '0' + this[field_name]
      }

      const old_focus = ref
      const new_focus = event.relatedTarget

      let still_focused = true

      try {
        const old_parent = old_focus.parentElement
        const new_parent = new_focus.parentElement.parentElement.parentElement.parentElement.parentElement

        still_focused = old_parent == new_parent
      } catch {
        still_focused = false
      }

      if (still_focused) return
      // this.focus = null

      const day = parseInt(this.day)
      const month = parseInt(this.month)
      const year = parseInt(this.year)
      const hour = parseInt(this.hour)
      const min = parseInt(this.min)
      const sec = this.seconds ? parseInt(this.sec) : 0

      if (this.time) {
        if (day && month && year && !isNaN(hour) && !isNaN(min) && !isNaN(sec)) {
          const b = new Date(year, month - 1, day, hour, min, sec)
          if (b) {
            this.submitNew(new Date(b))
          }
        }
      } else if (day && month && year) {
        const b = new Date(year, month - 1, day)
        if (b) {
          this.submitNew(new Date(b))
        }
      }
    },
    showGUI() {
      if (!this.disabled && !this.readonly) {
        this.$refs.hiddenDate.$el.children[0].click()
      }
    },
    convertISO(a) {
      if (a && !this.loading) {
        this.submitNew(new Date(a))
      }
    },
    submitNew(val) {
      if (!this.editable) {
        return
      }
      if (!val && !this.value) {
        return
      }

      if (val && !this.time) {
        val.setHours(0, 0, 0, 0)
        if (!this.noOffset) {
          val = new Date(val - val.getTimezoneOffset() * 60000)
        }
      }

      if (val && this.value) {
        if (val.getTime() == this.value.getTime()) {
          return
        }
      }

      this.$emit('input', val)
      this.$emit('change', val)

      if (this.show_validate)
        this.$nextTick(() => {
          this.validate(val)
        })
    },
  },
}
</script>

<style lang="scss" scoped>
.e-btn {
  margin-top: -5px;
}

.custom-date input::-webkit-inner-spin-button {
  display: none;
  -webkit-appearance: none;
}
.custom-date {
  z-index: 1;

  input[type='number'] {
    -moz-appearance: textfield;
  }
  .v-input {
    display: inline-flex !important;
    margin-top: 0;
    padding-top: 0;
  }

  input:focus {
    outline-width: 0;
    // caret-color: #418fde;
  }

  .v-data-table &:focus-within::after {
    content: '';
    width: calc(100% + 16px);
    height: calc(100% + 4px);
    top: -2px;
    left: -8px;

    position: absolute;
    pointer-events: none;

    border: solid var(--v-primary-base) 1px;
    border-radius: 4px;
  }
}

.v-text-field--outlined .custom-date {
  margin-left: 10px;
  margin-top: 13px;
}

.v-text-field--outlined.v-input--dense .custom-date {
  margin-top: -2px;
}

.date_input {
  pointer-events: all;
}

.root ::v-deep {
  white-space: initial;
}

.root ::v-deep .date-time-root {
  .v-label {
    overflow: unset;
    /* max-width: 133%; */
    transform: translateY(-18px) scale(0.75);
  }
}

.custom-date .divider {
  margin-left: -0.2em !important;
  margin-right: -0.2em !important;
}

.date-time-root ::v-deep .v-input__prepend-outer {
  position: absolute;
  margin: 0;
  /* background: red; */
}
.date-time-root {
  position: relative;
}

.v-input.error--text ::v-deep input {
  color: var(--v-error-base) !important;
  caret-color: var(--v-error-base) !important;
}

.date-time-root:focus-within ::v-deep fieldset {
  color: var(--v-primary-base);
}

.root ::v-deep .v-input__append-inner,
.root ::v-deep .v-input__append-inner .v-input__icon--clear {
  pointer-events: all;
}

/* ::v-deep .v-text-field > .v-input__prepend-outer * { */
.root ::v-deep .v-input__prepend-outer .v-input__slot::before {
  /* border: solid red 2px; */
  border: none !important;
}
</style>
