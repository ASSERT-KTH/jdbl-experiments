const fs = require("fs");
const ProgressBar = require("progress");
const async = require("async");
var exec = require("child_process").exec;

const config = require("./config");
const utils = require("./utils");

let mavenGraph = JSON.parse(
  fs.readFileSync(config.output + "maven_graph_with_test_results.json")
);
if (
  fs.existsSync(config.output + "maven_graph_with_client_test_results.json")
) {
  mavenGraph = JSON.parse(
    fs.readFileSync(config.output + "maven_graph_with_client_test_results.json")
  );
}

function execTest(repo, commit) {
  return new Promise((resolve) => {
    exec(
      `docker run --rm jdbl compile --url https://github.com/${repo} --commit ${commit}`,
      (error, stdout, stderr) => {
        if (!error && stdout) {
          try {
            const results = JSON.parse(stdout);
            return resolve(results);
          } catch (error) {}
        }
        console.log(error, stdout, stderr);
        resolve(null);
      }
    );
  });
}

(async () => {
  const tasks = [];
  for (let libId in mavenGraph) {
    const lib = mavenGraph[libId];
    version: for (let version in lib.clients) {
      const commit = lib.releases[version];
      if (
        !lib.test_results ||
        !lib.test_results[commit] ||
        lib.test_results[commit].length != 3
      ) {
        continue;
      }
      for (let r of lib.test_results[commit]) {
        if (r == null) {
          continue version;
        }
        if (r.error != 0 || r.failing != 0 || r.passing == 0) {
          continue version;
        }
      }
      const clients = lib.clients[version];
      for (let client of clients) {
        if (client.test_results) {
          continue;
        }
        tasks.push({
          lib,
          client,
          repo: client.repo_name,
        });
      }
    }
  }
  var bar = new ProgressBar(
    "[:bar] :current/:total :rate/bps :percent :etas :step",
    {
      complete: "=",
      incomplete: " ",
      width: 30,
      total: tasks.length,
    }
  );
  async.eachOfLimit(utils.shuffle(tasks), 5, async (task, index) => {
    const results = await execTest(task.repo, "HEAD");

    bar.tick({
      step: `${task.repo} for ${task.lib.repo_name}`,
    });

    console.log(results);
    task.client.commit = results.commit;
    task.client.test_results = results.test_results;

    fs.writeFileSync(
      config.output + "maven_graph_with_client_test_results.json",
      JSON.stringify(mavenGraph)
    );
  });
})();
