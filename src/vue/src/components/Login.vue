<template>
  <div>
    <form method="POST" action="/process-registration">
      <label for="username">Username:</label>
      <input type="text" id="username" name="username">
      <label for="password">Password:</label>
      <input type="text" id="password" name="password">
      <a href="/forgot">Forgotten password</a>
      <input type="submit" value="Log in">
    </form>
  </div>
</template>

<script>
export default {
  name: "Login"
};
</script>

<style lang="scss" scoped>
div {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  grid-template-rows: 1fr auto 1fr;
  min-height: 100vh;
}
form {
  grid-column: 2 / 3;
  grid-row: 2 / 3;

  display: grid;
  grid-template-columns: 1fr 1fr;
}
</style>
