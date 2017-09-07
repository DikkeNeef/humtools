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

router.get('/load_object_tree', function (req, res_) {
    rpc.invoke("load_object_tree", function (error, res, more) {
        res_.json(res);
    });
});

router.get('/load_scene_tree', function (req, res_) {
    rpc.invoke("load_scene_tree", function (error, res, more) {
        res_.json(res);
    });
});

router.get('/load_conversation_tree', function (req, res_) {
    rpc.invoke("load_conversation_tree", function (error, res, more) {
        res_.json(res);
    });
});

router.post('/load_background', function (req, res_) {
    rpc.invoke("load_background", {
        "scene": req.body.scene
    }, function (error, res, more) {
        console.log(JSON.parse(res));
        res_.json(JSON.parse(res));
    });
});

router.post('/load_music', function (req, res_) {
    rpc.invoke("load_music", {
        "scene": req.body.scene
    }, function (error, res, more) {
        console.log(JSON.parse(res));
        res_.json(JSON.parse(res));
    });
});

// http://localhost:8000/api
app.use('/api', router);
app.listen(port);
