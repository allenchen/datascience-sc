var express = require('express')
  , exec = require('child_process').exec
  ;

var app = module.exports = express.createServer();

app.get('/', function(req, res){
  res.send('sup brah');
});

app.get('/predict', function(req, res){
  p = {
    stuff: [],
  };

  child = exec('./runner', function(error, stdout, stderr){
    if(stderr) p.error = stderr;
    if(error) p.error = error;
    p.stuff = stdout;

    res.send(p);
  });
});

app.listen(9999, function(){
  console.log("Express server listening on port %d in %s mode", app.address().port, app.settings.env);
});
