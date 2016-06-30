var PythonShell = require('python-shell');

PythonShell.run('Parser.py', function (err) {
  if (err) throw err;
  console.log('finished');
});
