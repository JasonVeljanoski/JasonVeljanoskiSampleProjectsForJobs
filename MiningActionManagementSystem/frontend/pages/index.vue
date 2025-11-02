<script>
export default {
  head() {
    return {
      title: 'Home',
    }
  },
  created() {
    this.$router.push({ name: 'actions' })
  },
}
</script>
