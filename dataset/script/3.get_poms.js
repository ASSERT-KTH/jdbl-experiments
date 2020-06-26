const fs = require("fs");
const path = require("path");
const async = require("async");
const ProgressBar = require("progress");
const request = require("request");

const config = require("./config");
const utils = require("./utils");

const OUTPUT_dir = config.output + "poms/";
if (!fs.existsSync(OUTPUT_dir)) {
  fs.mkdirSync(OUTPUT_dir);
}

const repos = utils.walkSync(config.output + "maven_projects/");

var bar = new ProgressBar("[:bar] :current :rate/bps :percent :etas :repo", {
  complete: "=",
  incomplete: " ",
  width: 80,
  total: repos.length,
});

function downloadGitHubFile(repo, file, callback) {
  utils.downloadGithubFile(repo, "HEAD", file, config.github_tokens[0]).then(
    (res) => callback(null, res),
    (res) => callback(res, null)
  );
}

let nbMaven = 0;
async.eachLimit(
  repos.reverse(),
  10,
  (file, callback) => {
    let repo =
      path.basename(path.dirname(file)) +
      "/" +
      path.basename(file).replace(".json", "");
    bar.tick({
      repo: repo,
    });
    if (fs.existsSync(OUTPUT_dir + repo + "/pom.xml")) {
      nbMaven++;
      return callback();
    }
    fs.readFile(file, (err, data) => {
      if (err) {
        console.error(err);
        return callback();
      }
      const poms = JSON.parse(data);
      if (poms.length > 0) {
        nbMaven++;
      }
      if (poms.length == 1) {
        if (!fs.existsSync(OUTPUT_dir + repo)) {
          fs.mkdirSync(OUTPUT_dir + repo, { recursive: true });
        }
        downloadGitHubFile(repo, poms[0], (err, body) => {
          if (err == null) {
            fs.writeFileSync(OUTPUT_dir + repo + "/pom.xml", body);
          }
          callback();
        });
      } else {
        callback();
      }
    });
  },
  () => {
    console.log("# pom downloaded", nbMaven);
  }
);
