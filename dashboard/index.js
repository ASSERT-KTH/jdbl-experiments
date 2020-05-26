const express = require("express");
const compression = require('compression')
const bodyParser = require("body-parser");
const fs = require("fs");

var app = express();
app.use(bodyParser.json());
app.use(compression())

let pathResults = __dirname + "/../script/results";
if (process.argv.length > 2) {
  pathResults = fs.realpathSync(process.argv[2]);
}
app.use(
  "/data/raw_results.json",
  express.static(__dirname + "/../raw_results.json")
);
app.use(
  "/data/client_categories.json",
  express.static(__dirname + "/../client_categories.json")
);
app.use(
  "/data/lib_categories.json",
  express.static(__dirname + "/../lib_categories.json")
);
app.use("/data/", express.static(pathResults));
app.use(express.static(__dirname + "/public"));

app.route("/api/:lib/:version/:category").post(function (req, res) {
  const file = __dirname + "/../lib_categories.json";
  fs.readFile(file, (err, f) => {
    if (err) {
      return res.status(500).send(err);
    }
    const data = JSON.parse(f);
    const key = req.params.lib + "_" + req.params.version;
    if (!data[key]) {
      data[key] = [];
    }
    const index = data[key].indexOf(req.params.category);

    if (index > -1) {
      data[key].splice(index, 1);
    } else {
      data[key].push(req.params.category);
    }
    fs.writeFile(file, JSON.stringify(data), (err) => {
      return res.send("ok");
    });
  });
});
app.route("/api/:lib/:version/:client/:category").post(function (req, res) {
  const file = __dirname + "/../client_categories.json";
  fs.readFile(file, (err, f) => {
    if (err) {
      return res.status(500).send(err);
    }
    const data = JSON.parse(f);
    const key =
      req.params.lib + "_" + req.params.version + "_" + req.params.client;
    if (!data[key]) {
      data[key] = [];
    }
    const index = data[key].indexOf(req.params.category);

    if (index > -1) {
      data[key].splice(index, 1);
    } else {
      data[key].push(req.params.category);
    }
    fs.writeFile(file, JSON.stringify(data), (err) => {
      return res.send("ok");
    });
  });
});

const PORT = process.env.PORT || 8881;

app.listen(PORT, function () {
  console.log("Example app listening on port " + PORT);
});
