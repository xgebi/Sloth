module.exports = {
  devServer: {
    proxy: 'http://localhost:5000',
    disableHostCheck: true,
    socket: 'socket'
  }
}
