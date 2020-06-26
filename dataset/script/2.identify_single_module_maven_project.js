const fs = require("fs");
const path = require("path");
const async = require("async");
const ProgressBar = require("progress");

const config = require("./config");

const available_tokens = [...config.github_tokens];

const fileContent = fs.readFileSync(__dirname + "/../data/java_repos.txt") + "";
const repos = fileContent.split("\n");

let truncated = 0;

const OUTPUT_dir = config.output + "maven_projects/";
if (!fs.existsSync(OUTPUT_dir)) {
  fs.mkdirSync(OUTPUT_dir);
}

var bar = new ProgressBar("[:bar] :current :rate/bps :percent :etas :repo", {
  complete: "=",
  incomplete: " ",
  width: 80,
  total: repos.length,
});

const ingoredFolders = ["siteMods", "userguide", "resources", "sample", "example"]
async.eachLimit(repos, 15, (repo, callback) => {
  bar.tick({
    repo: repo,
  });
  if (!fs.existsSync(config.output + "repo_files/" + repo + ".json")) {
    return callback();
  }
  // const repo = owner + '/' + file.replace('.json', '')
  const repositoryContent = JSON.parse(
    fs.readFileSync(config.output + "repo_files/" + repo + ".json")
  );
  if (repositoryContent.truncated) {
    truncated++;
  }
  const poms = [];
  for (let i of repositoryContent.tree) {
    if (i.size < 5) {
      continue;
    }
    const filename = i.path.substring(
      i.path.lastIndexOf("/") + 1,
      i.path.length
    );
    if (filename.toLowerCase() == "pom.xml") {
      let found = false;
      for (let ign of ingoredFolders) {
        if (i.path.indexOf(ign) != -1) {
          found = true
          break;
        }
      }
      if (found == false) {
        poms.push(i.path);
      }
    }
  }
  if (poms.length != 1) {
      return callback();
  }
  if (!fs.existsSync(OUTPUT_dir + path.dirname(repo))) {
    fs.mkdirSync(OUTPUT_dir + path.dirname(repo));
  }
  fs.writeFileSync(OUTPUT_dir + repo + ".json", JSON.stringify(poms));

  callback();
});

console.log("Truncated", truncated);
