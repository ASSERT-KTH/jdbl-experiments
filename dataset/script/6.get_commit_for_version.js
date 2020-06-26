const fs = require("fs");
const ProgressBar = require("progress");

const config = require("./config");
const utils = require("./utils");

const available_tokens = [...config.github_tokens];

const OUTPUT_dir = config.output + "project_tags/";
if (!fs.existsSync(OUTPUT_dir)) {
  fs.mkdirSync(OUTPUT_dir);
}

const OUTPUT_POM_COMMIT_dir = config.output + "pom_commits/";
if (!fs.existsSync(OUTPUT_POM_COMMIT_dir)) {
  fs.mkdirSync(OUTPUT_POM_COMMIT_dir);
}

const mavenGraph = JSON.parse(
  fs.readFileSync(config.output + "maven_graph.json")
);

async function downloadTags(lib) {
  const token = available_tokens.pop();
  const octokit = utils.createOctokit(token);

  const owner = lib.repo_name.split("/")[0];
  const repo = lib.repo_name.split("/")[1];

  const response = await octokit.repos.listTags({
    owner,
    repo,
  });
  if (!fs.existsSync(OUTPUT_dir + owner)) {
    fs.mkdirSync(OUTPUT_dir + owner);
  }
  const releases = utils.clean_github_object(response.data);

  fs.writeFileSync(
    OUTPUT_dir + lib.repo_name + ".json",
    JSON.stringify(releases)
  );
  available_tokens.push(token);
}

async function downloadPomCommits(lib) {
  const paths = JSON.parse(
    fs.readFileSync(config.output + "maven_projects/" + lib.repo_name + ".json")
  );
  const path = paths[0];

  const token = available_tokens.pop();
  const octokit = utils.createOctokit(token);

  const owner = lib.repo_name.split("/")[0];
  const repo = lib.repo_name.split("/")[1];

  const response = await octokit.repos.listCommits({
    owner,
    repo,
    path,
  });
  if (!fs.existsSync(OUTPUT_POM_COMMIT_dir + owner)) {
    fs.mkdirSync(OUTPUT_POM_COMMIT_dir + owner);
  }
  const commits = utils
    .clean_github_object(response.data)
    .map((c) => c.sha)
    .reverse();
  fs.writeFileSync(
    OUTPUT_POM_COMMIT_dir + lib.repo_name + ".json",
    JSON.stringify(commits)
  );
  available_tokens.push(token);
}

async function downloadPom(lib, commit) {
  const paths = JSON.parse(
    fs.readFileSync(config.output + "maven_projects/" + lib.repo_name + ".json")
  );
  const path = paths[0];
  const token = available_tokens.pop();

  const pom = await utils.downloadGithubFile(
    lib.repo_name,
    commit,
    path,
    token
  );

  if (!fs.existsSync(OUTPUT_POM_COMMIT_dir + lib.repo_name)) {
    fs.mkdirSync(OUTPUT_POM_COMMIT_dir + lib.repo_name);
  }
  if (!fs.existsSync(OUTPUT_POM_COMMIT_dir + lib.repo_name + "/" + commit)) {
    fs.mkdirSync(OUTPUT_POM_COMMIT_dir + lib.repo_name + "/" + commit);
  }

  fs.writeFileSync(
    OUTPUT_POM_COMMIT_dir + lib.repo_name + "/" + commit + "/pom.xml",
    pom
  );
  available_tokens.push(token);
}

function normalizeVersion(version) {
  return version
    .toLowerCase()
    .replace("portable-", "")
    .replace("v.", "")
    .replace("v", "")
    .replace(/_/g, ".")
    .replace(/-/g, ".");
}
function findCommitForVersion(version, versionCommit) {
  if (versionCommit[version]) {
    return versionCommit[version];
  }
  version = normalizeVersion(version);
  for (let release in versionCommit) {
    const commit = versionCommit[release];
    release = normalizeVersion(release);
    let index = release.indexOf(version);
    if (index > -1) {
      return commit;
    }
  }
}
(async () => {
  var bar = new ProgressBar("[:bar] :current :rate/bps :percent :etas :step", {
    complete: "=",
    incomplete: " ",
    width: 30,
    total: Object.keys(mavenGraph).length,
  });
  let losts = 0;
  let valid = 0;
  for (let libId in mavenGraph) {
    const lib = mavenGraph[libId];

    bar.tick({
      step: libId,
    });

    if (!fs.existsSync(OUTPUT_dir + lib.repo_name + ".json")) {
      await downloadTags(lib);
    }
    const versionCommit = {};
    for (let tag of JSON.parse(
      fs.readFileSync(OUTPUT_dir + lib.repo_name + ".json")
    )) {
      versionCommit[tag.name] = tag.commit.sha;
    }
    if (!fs.existsSync(OUTPUT_POM_COMMIT_dir + lib.repo_name + ".json")) {
      await downloadPomCommits(lib);
    }
    const commits = JSON.parse(
      fs.readFileSync(OUTPUT_POM_COMMIT_dir + lib.repo_name + ".json")
    );

    for (let commit of commits) {
      const pathPom =
        OUTPUT_POM_COMMIT_dir + lib.repo_name + "/" + commit + "/pom.xml";
      if (!fs.existsSync(pathPom)) {
        try {
          await downloadPom(lib, commit);
        } catch (error) {}
      }
      try {
        const pom = await utils.parsePom(pathPom);
        if (!versionCommit[pom.version]) {
          versionCommit[pom.version] = commit;
        }
      } catch (error) {}
    }
    lib.releases = {};
    for (const clientVersion in lib.clients) {
      const commit = findCommitForVersion(clientVersion, versionCommit);
      if (commit == null) {
        delete lib.clients[clientVersion];
        losts += 1; // Object.keys(lib.clients[clientVersion]).length
      } else {
        valid += 1;
        lib.releases[clientVersion] = commit;
      }
    }

    if (Object.keys(lib.clients).length == 0) {
      delete mavenGraph[libId];
    }
  }
  fs.writeFileSync(config.output + "maven_graph_with_release.json", JSON.stringify(mavenGraph))
})();
