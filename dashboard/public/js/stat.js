function loadData(callback) {
  var result = null;

  function end() {
    callback(result);
  }
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      result = JSON.parse(this.responseText);
      end();
    }
  };
  xhttp.open("GET", "/data/raw_results.json", true);
  xhttp.send();
}
function sum(numbers) {
  return numbers.reduce((a, b) => a + b, 0);
}
function mean(numbers) {
  var total = sum(numbers);
  return Math.round((total * 100) / numbers.length) / 100;
}
/**
 * The "median" is the "middle" value in the list of numbers.
 *
 * @param {Array} numbers An array of numbers.
 * @return {Number} The calculated median value from the specified numbers.
 */
function median(numbers) {
  // median of [3, 5, 4, 4, 1, 1, 2, 3] = 3
  var median = 0,
    numsLen = numbers.length;
  numbers.sort();

  if (
    numsLen % 2 ===
    0 // is even
  ) {
    // average of two middle numbers
    median = (numbers[numsLen / 2 - 1] + numbers[numsLen / 2]) / 2;
  } else {
    // is odd
    // middle number only
    median = numbers[(numsLen - 1) / 2];
  }
  return median;
}

function displayResult(title, value, of) {
  const parent = document.getElementById("page-wrapper");
  let text = ``;
  if (Array.isArray(value)) {
    text += ` ${sum(value)}`;
    if (of) {
      text += ` (${Math.round((sum(value) * 100) / sum(of))}%)`;
    }
    text += ` average ${mean(value)} median ${median(value)}`;
  } else {
    text += ` ${value}`;
    if (of) {
      text += ` (${Math.round((value * 100) / of)}%)`;
    }
  }
  const element = document.createElement("div");
  element.className = "stat";

  const label = document.createElement("span");
  label.className = "label";

  label.innerText = `${title}:`;
  element.appendChild(label);
  const content = document.createElement("span");
  content.className = "content";

  content.innerText = text;
  element.appendChild(content);
  parent.appendChild(element);
  console.log(title, text);
}
loadData((result) => {
  const libs = [];
  for (let libId in result) {
    for (let version in result[libId]) {
      result[libId].version = version;
      libs.push(result[libId][version]);
    }
  }

  const nbLib = libs.length;
  displayResult("# Lib", nbLib);
  const nbCompiled = libs.filter((l) => l.compiled).length;
  displayResult("# Compiled Lib", nbCompiled, nbLib);
  const nbDebloated = libs.filter((l) => l.debloat).length;
  displayResult("# Debloated Lib", nbDebloated, nbCompiled);

  const debloatTime = libs.filter((l) => l.debloat).map((l) => l.debloatTime);
  displayResult("Debloat time", debloatTime);

  const nbDependencies = libs.map((l) => Object.keys(l.dependencies).length);
  displayResult("# Dependencies", nbDependencies);

  const nbClass = libs.map((l) => l.nb_class);
  displayResult("# Class", nbClass);
  const nbBloatedClass = libs.map((l) => l.nb_debloat_class);
  displayResult("# Debloated Class", nbBloatedClass, nbClass);

  const nbMethod = libs.map((l) => l.nb_method);
  displayResult("# Method", nbMethod);
  const nbDebloatedMethod = libs.map((l) => l.nb_debloat_method);
  displayResult("# Debloated Method", nbDebloatedMethod, nbMethod);

  const coverages = libs
    .filter((l) => l.coverage != null)
    .map((l) => l.coverage.coverage * 100);
  displayResult("Coverage", coverages);

  const nbTest = libs.map(
    (l) =>
      l.original_test.error + l.original_test.failing + l.original_test.passing
  );
  displayResult("# Test", nbTest);

  const nbFailingTest = libs.map((l) => l.original_test.failing);
  displayResult("# Failing Test", nbFailingTest, nbTest);

  const nbErrorTest = libs.map((l) => l.original_test.error);
  displayResult("# Error Test", nbErrorTest, nbTest);

  const nbPassingTest = libs.map((l) => l.original_test.passing);
  displayResult("# Passing Test", nbPassingTest, nbTest);

  const testExecution = libs.map((l) => l.original_test.execution_time);
  displayResult("Test Execution", testExecution);


  const nbDeboatTest = libs.filter((l) => l.debloat).map(
    (l) =>
      l.original_test.error + l.debloat_test.failing + l.debloat_test.passing
  );
  displayResult("# Deboated Test", nbDeboatTest);

  const nbDeboatFailingTest = libs.filter((l) => l.debloat).map((l) => l.debloat_test.failing);
  displayResult("# Deboated Failing Test", nbDeboatFailingTest, nbDeboatTest);

  const nbDeboatErrorTest = libs.filter((l) => l.debloat).map((l) => l.debloat_test.error);
  displayResult("# Deboated Error Test", nbDeboatErrorTest, nbDeboatTest);

  const nbDeboatPassingTest = libs.filter((l) => l.debloat).map((l) => l.debloat_test.passing);
  displayResult("# Deboated Passing Test", nbDeboatPassingTest, nbDeboatTest);

  const testDeboatExecution = libs.filter((l) => l.debloat).map((l) => l.debloat_test.execution_time);
  displayResult("Deboated Test Execution", testDeboatExecution);

  const jarSize = libs.filter((l) => l.debloat).map((l) => l.original_jar_size);
  displayResult("Jar size", jarSize);

  const debloatJarSize = libs
    .filter((l) => l.debloat)
    .map((l) => l.debloat_jar_size);
  displayResult("Debloat Jar size", debloatJarSize, jarSize);

  const clients = libs.map((l) => Object.values(l.clients));
  const nbClient = clients.map((c) => c.length);
  displayResult("# Clients", nbClient);
  const nbCompiledClient = clients.map(
    (c) => c.filter((o) => o.compiled).length
  );
  displayResult("# Compiled Clients", nbCompiledClient, nbClient);

  const nbDebloatedClient = clients.map(
    (c) => c.filter((o) => o.debloat).length
  );
  displayResult("# Debloated Clients", nbDebloatedClient, nbCompiledClient);
});
