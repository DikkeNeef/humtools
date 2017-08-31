var bodyParser = require('body-parser');
var zerorpc = require("zerorpc");
var express = require('express');
var cors = require('cors');
var app = express();

app.use(bodyParser.urlencoded({
    extended: true
}));
app.use(bodyParser.json());
app.use(cors({
    origin: '*'
}));

var port = process.env.PORT || 8000;
var router = express.Router();
var rpc = new zerorpc.Client();
rpc.connect("tcp://127.0.0.1:4242");

router.get('/', function (req, res_) {
    res_.json({
        message: 'hooray! welcome to our api!'
    });
});

router.post('/hello', function (req, res_) {
    rpc.invoke("hello", req.body.name, function (error, res, more) {
        res_.json({
            "name": res
        });
    });
})

// http://localhost:8000/api
app.use('/api', router);
app.listen(port);
