<template>
  <div id="app">
    <div id="login" v-if="!loggedIn || !loggedIn.uuid || !loggedIn.token">
      <Login/>
    </div>
    <div id="loggedIn" v-if="loggedIn && loggedIn.uuid && loggedIn.token">
      <div id="nav">
        <router-link to="/">Home</router-link>|
        <router-link to="/about">About</router-link>
      </div>
      <router-view/>
    </div>
  </div>
</template>

<script>
import Login from "@/components/Login.vue";

export default {
  components: {
    Login
  },

  loggedIn: null,
  created: function() {
    let data = {};
    this.loggedIn = null;
    console.log(document.cookie);
    if (document.cookie["auth"]) {
      data["uuid"] = document.cookie["auth"]["uuid"];
      data["token"] = document.cookie["auth"]["token"];
    } else {
      data["new_login"] = true;
    }

    fetch("/api/authenticate", {
      method: "POST",
      body: JSON.stringify(data), // data can be `string` or {object}!
      headers: {
        "Content-Type": "application/json"
      }
    })
      .then(res => res.json())
      .then(response => {
        this.loggedIn = {};
        console.log("Success:", JSON.stringify(response));
      })
      .catch(error => console.error("Error:", error));
  }
};
</script>

<style lang="scss">
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
#nav {
  padding: 30px;
  a {
    font-weight: bold;
    color: #2c3e50;
    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
</style>
