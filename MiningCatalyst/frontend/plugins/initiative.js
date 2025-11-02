export default ({ app, store }, inject) => {
  inject('initiative', {
    formatDates(initiative) {
      initiative.created = app.$format.initDate(initiative.created)
      initiative.updated = app.$format.initDate(initiative.updated)
      initiative.date_opened = app.$format.initDate(initiative.date_opened)
      initiative.target_completion_date = app.$format.initDate(initiative.target_completion_date)

      return initiative
    },
  })
}
