const { serverlessHandler } = require('../dist/serverless');

module.exports = (req, res) => serverlessHandler(req, res);
