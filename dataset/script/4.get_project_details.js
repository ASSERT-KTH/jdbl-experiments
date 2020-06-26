const Octokit = require("@octokit/rest")
  .plugin(require("@octokit/plugin-throttling"))
  .plugin(require("@octokit/plugin-retry"));

const async = require("async");
const fs = require("fs");
const ProgressBar = require("progress");

const config = require("./config");
const utils = require("./utils");

const OUTPUT_dir = config.output + "repo_details/";
if (!fs.existsSync(OUTPUT_dir)) {
  fs.mkdirSync(OUTPUT_dir);
}

const tokens = {};
for (let token of config.github_tokens) {
  tokens[token] = {};
}

const repos = utils.walkSync(config.output + "maven_projects/");

var bar = new ProgressBar("[:bar] :current :rate/bps :percent :etas :step", {
  complete: "=",
  incomplete: " ",
  width: 30,
  total: repos.length,
});

const available_tokens = [...config.github_tokens];
async.eachOfLimit(
  utils.shuffle(repos),
  available_tokens.length,
  (item, index, callback) => {
    const tmp = item.split("/");
    item = tmp[tmp.length - 2] + "/" + tmp[tmp.length - 1].replace(".json", "");
    bar.tick({
      step: item,
    });
    const files_path = OUTPUT_dir + item + ".json";
    if (fs.existsSync(files_path)) {
      return callback();
    }
    const token = available_tokens.pop();
    const octokit = new Octokit({
      auth: token,
      throttle: {
        onRateLimit: (retryAfter, options) => {
          octokit.log.warn(
            `Request quota exhausted for request ${options.method} ${options.url} ${options.headers.authorization}`
          );

          if (options.request.retryCount === 0) {
            // only retries once
            console.log(`Retrying after ${retryAfter} seconds!`);
            return true;
          }
        },
        onAbuseLimit: (retryAfter, options) => {
          // does not retry, only logs a warning
          console.log(
            `Abuse detected for request ${options.method} ${options.url}`
          );
          return true;
        },
      },
    });
    octokit.hook.after("request", async (response, options) => {
      tokens[token].remaining = parseInt(
        response.headers["x-ratelimit-remaining"]
      );
      tokens[token].reset = new Date(
        parseInt(response.headers["x-ratelimit-reset"]) * 1000
      );
    });

    const owner = item.split("/")[0];
    const repo = item.split("/")[1];
    const tree_sha = "HEAD";
    const recursive = 1;

    octokit.repos
      .get({
        owner,
        repo,
      })
      .then(
        (response) => {
          if (!fs.existsSync(OUTPUT_dir + owner)) {
            fs.mkdirSync(OUTPUT_dir + owner);
          }
          const files = utils.clean_github_object(response.data);
          fs.writeFile(files_path, JSON.stringify(files), (err) => {
            available_tokens.push(token);
            if (err) {
              console.error(err);
            }
            callback();
          });
        },
        (err) => {
          console.error(err.message, owner, repo);
          available_tokens.push(token);
          callback();
        }
      );
  }
);
