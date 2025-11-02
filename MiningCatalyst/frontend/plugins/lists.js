export default ({ app, store }, inject) => {
  inject('lists', {
    async importAllLists() {
      await Promise.all([
        store.dispatch('lists/fetchUsers'),
        // store.dispatch('lists/fetchEquipments'),
        store.dispatch('lists/fetchOrganisationalUnits'),
      ])
    },
  })
}
