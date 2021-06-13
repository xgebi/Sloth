<template>
  <div id="app">
    <span v-if="test">This is test</span>
  </div>
</template>

<script>
export default {
  name: 'App',
  components: {

  },
  props: {
    sections: String
  },
  data: () => {
    return { test: false }
  },
  mounted() {
    console.log(JSON.parse(this.sections.substr("data:json,".length)));
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
