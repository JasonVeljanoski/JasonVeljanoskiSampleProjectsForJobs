export default ({ app, store }, inject) => {
  inject('workgroup_perms', {
    canEdit(owner_id, admin_ids) {
      // A workgroup can be edited if:
      //  [1]. User is an Admin of the workgroup OR
      //  [2]. User is the owner of the workgroup (assigned to)
      const user = app.$auth.user
      return admin_ids.includes(user.id) || owner_id == user.id
    },
  })
}
