module.exports = app => {
  app.use('/category', require('./actions/category/getCategory'));
}
