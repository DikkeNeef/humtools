var zerorpc    = require("zerorpc");
var express    = require('express');
var app        = express();
var bodyParser = require('body-parser');

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

var port = process.env.PORT || 8000;
var router = express.Router();
var rpc = new zerorpc.Client();
rpc.connect("tcp://127.0.0.1:4242");

router.get('/', function(req, res) {
    res.json({ message: 'hooray! welcome to our api!' });
});

router.get('/hello/:name', function(req, res) {
    rpc.invoke("hello", req.params.name, function(error, res, more) {
        console.log(res);
    });
    res.json({ message: 'Ahoi, Node.js server is responding' });
})
// http://localhost:8080/api
app.use('/api', router);
app.listen(port);
