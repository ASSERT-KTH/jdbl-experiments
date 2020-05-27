angular
  .module("jdbl-website", ["ngRoute", "anguFixedHeaderTable"])
  .directive("keypressEvents", [
    "$document",
    "$rootScope",
    function ($document, $rootScope) {
      return {
        restrict: "A",
        link: function () {
          $document.bind("keydown", function (e) {
            $rootScope.$broadcast("keypress", e);
            $rootScope.$broadcast("keypress:" + e.which, e);
          });
        },
      };
    },
  ])
  .controller("libController", function (
    $scope,
    $location,
    $rootScope,
    $routeParams,
    $uibModal
  ) {
    var $ctrl = $scope;
    $ctrl.bugs = $scope.$parent.filteredBugs;
    $ctrl.classifications = $scope.$parent.classifications;
    $ctrl.index = -1;
    $ctrl.bug = null;

    $scope.$watch("$parent.filteredBugs", function () {
      $ctrl.bugs = $scope.$parent.filteredBugs;
      $ctrl.index = getIndex($routeParams.benchmark, $routeParams.id);
    });
    $scope.$watch("$parent.classifications", function () {
      $ctrl.classifications = $scope.$parent.classifications;
    });

    var getIndex = function (benchmark, bugId) {
      if ($ctrl.bugs == null) {
        return -1;
      }
      for (var i = 0; i < $ctrl.bugs.length; i++) {
        if (
          $ctrl.bugs[i].benchmark == benchmark &&
          ($ctrl.bugs[i].bugId == bugId || bugId == null)
        ) {
          return i;
        }
      }
      return -1;
    };

    $scope.$on("$routeChangeStart", function (next, current) {
      $ctrl.index = getIndex(current.params.benchmark, current.params.id);
    });

    var modalInstance = null;
    $scope.$watch("index", function () {
      if ($scope.index != -1) {
        if (modalInstance == null) {
          modalInstance = $uibModal.open({
            animation: true,
            ariaLabelledBy: "modal-title",
            ariaDescribedBy: "modal-body",
            templateUrl: "modelPatch.html",
            controller: "bugModal",
            controllerAs: "$ctrl",
            size: "lg",
            resolve: {
              bug: function () {
                return $scope.bugs[$scope.index];
              },
              classifications: $scope.classifications,
            },
          });
          modalInstance.result.then(
            function () {
              modalInstance = null;
              $location.path("/");
            },
            function () {
              modalInstance = null;
              $location.path("/");
            }
          );
        } else {
          $rootScope.$emit("new_bug", $scope.bugs[$scope.index]);
        }
      }
    });
    var nextPatch = function () {
      var index = $scope.index + 1;
      if (index == $ctrl.bugs.length) {
        index = 0;
      }
      $location.path(
        "/bug/" + $ctrl.bugs[index].benchmark + "/" + $ctrl.bugs[index].bugId
      );
      return false;
    };
    var previousPatch = function () {
      var index = $scope.index - 1;
      if (index < 0) {
        index = $ctrl.bugs.length - 1;
      }
      $location.path(
        "/bug/" + $ctrl.bugs[index].benchmark + "/" + $ctrl.bugs[index].bugId
      );
      return false;
    };

    $scope.$on("keypress:39", function () {
      $scope.$apply(function () {
        nextPatch();
      });
    });
    $scope.$on("keypress:37", function () {
      $scope.$apply(function () {
        previousPatch();
      });
    });
    $rootScope.$on("next_bug", nextPatch);
    $rootScope.$on("previous_bug", previousPatch);
  })
  .filter("percentage", [
    "$filter",
    function ($filter) {
      return function (input, decimals) {
        return $filter("number")(input * 100, decimals) + "%";
      };
    },
  ])
  .filter("log", [
    "$sce",
    function ($sce) {
      return function (input) {
        if (!input) {
          return $sce.trustAs("html", "Log not available!");
        }
        let output = "";
        for (let line of input.split("\n")) {
          output += line
            .replace("[INFO]", "<span class='info'>[INFO]</span>")
            .replace(" INFO ", " <span class='info'>INFO</span> ")
            .replace("[ERROR]", "<span class='error'>[ERROR]</span>")
            .replace(" ERROR ", " <span class='error'>ERROR</span> ")
            .replace("<<< FAILURE!", " <span class='error'><<< FAILURE!</span> ")
            .replace("<<< ERROR!", " <span class='error'><<< ERROR!</span> ")
            .replace("[WARNING]", "<span class='warning'>[WARNING]</span>")
            .replace(" WARNING ", " <span class='warning'>WARNING</span> ")
            .replace(" WARN ", " <span class='warning'>WARN</span> ")
            .replace("[DEBUG]", "<span class='debug'>[DEBUG]</span>")
            .replace(" DEBUG ", " <span class='debug'>DEBUG</span> ")
            .replace("[exit]", "<span class='error'>[EXIT]</span>");
          output += "</br>";
        }
        return $sce.trustAs("html", output);
      };
    },
  ])
  .filter('filterObj', function() {
    return function(input, search) {
      if (!input) return input;
      if (!search) return input;
      var result = {};
      angular.forEach(input, function(value, key) {
        if (search(value)) {
          result[key] = value;
        }
      });
      return result;
    }
  })
  .controller("mainController", function ($scope, $http) {
    $scope.filters = {
      libDebloatTest: 'all',
      libDebloat: 'all',
      clientDebloatTest: 'all',
      clientDebloat: 'all',
      client: 'pass',
    };

    // create the list of sushi rolls
    $scope.bugs = [];
    $scope.currentLibName = "";
    $scope.currentVersions = [];
    $scope.currentVersionName = "";
    $scope.currentClients = {};
    $scope.currentClientName = "";
    $scope.currentClient = {};
    $scope.currentFrameworkLog = "";
    $scope.currentLibBuildLog = "";
    $scope.currentLibDebloatLog = "";
    $scope.currentClientBuildLog = "";
    $scope.currentClientDebloatLog = "";

    $scope.clientCategories = [];
    $scope.clientsCategories = {};
    $scope.currentClientCategories = [];

    $scope.currentLibCategories = [];
    $scope.libCategories = [];
    $scope.libsCategories = {};
    function getCategories() {
      $http.get("/data/client_categories.json").then(function (response) {
        $scope.clientCategories = [];
        $scope.clientsCategories = response.data;
        for (let id in $scope.clientsCategories) {
          for (let cat of $scope.clientsCategories[id]) {
            if ($scope.clientCategories.indexOf(cat) == -1) {
              $scope.clientCategories.push(cat);
            }
          }
        }
      });

      $http.get("/data/lib_categories.json").then(function (response) {
        $scope.libCategories = [];
        $scope.libsCategories = response.data;
        for (let id in $scope.libsCategories) {
          for (let cat of $scope.libsCategories[id]) {
            if ($scope.libCategories.indexOf(cat) == -1) {
              $scope.libCategories.push(cat);
            }
          }
        }
      });
    }
    getCategories();

    $http.get("data/raw_results.json").then(function (response) {
      $scope.bugs = response.data;
      const firstLib = Object.values($scope.bugs).filter($scope.libFilter)[0];
      
      for (let i in $scope.bugs) {
        if ($scope.bugs[i] == firstLib) {
          return $scope.openLib(i);
        }
      }
    });
    $scope.$watch('filters', () => {
      console.log("new filter")
      const firstLib = Object.values($scope.bugs).filter($scope.libFilter)[0];
      
      for (let i in $scope.bugs) {
        if ($scope.bugs[i] == firstLib) {
          return $scope.openLib(i);
        }
      }
    }, true)
    $scope.libFilter = function (lib) {
      const nbClient = Object.values(lib).filter($scope.versionFilter).length;
      return nbClient != 0;
    }
    $scope.versionFilter = function (lib) {
      const nbClient = Object.values(lib.clients).filter($scope.clientFilter).length;
      if (nbClient == 0) {
        return false;
      }
      if ($scope.filters.libDebloatTest == 'all' && $scope.filters.libDebloat == 'all') {
        return true;
      }
      let matchLibDebloatTest = false;
      if ($scope.filters.libDebloatTest != 'all') {
        if (!lib.debloat_test || !lib.original_test) {
          matchLibDebloatTest = false;
        } else if (lib.debloat_test.error > lib.original_test.error || 
          lib.debloat_test.failing > lib.original_test.failing) {
            matchLibDebloatTest = true;
        } else {
          matchLibDebloatTest = false;
        }
        if ($scope.filters.libDebloatTest == 'pass') {
          matchLibDebloatTest = !matchLibDebloatTest;
        }
      }

      let matchLibDebloat = false;
      if ($scope.filters.libDebloat != 'all') {
        matchLibDebloat = !lib.debloat;
        if ($scope.filters.libDebloat == 'pass') {
          matchLibDebloat = !matchLibDebloat;
        }
      }
      return matchLibDebloatTest || matchLibDebloat;
    }

    $scope.clientFilter = function (client) {
      if ($scope.filters.clientDebloatTest == 'all' && $scope.filters.clientDebloat == 'all'  && $scope.filters.client == 'all') {
        return true;
      }
      let matchClientDebloatTest = false;
      if ($scope.filters.clientDebloatTest != 'all') {
        if (!client.debloat_test || !client.original_test) {
          matchClientDebloatTest = false;
        } else if (client.debloat_test.error > client.original_test.error || 
          client.debloat_test.failing > client.original_test.failing) {
          matchClientDebloatTest = true;
        } else {
          matchClientDebloatTest = false;
        }
        if ($scope.filters.clientDebloatTest == 'pass') {
          matchClientDebloatTest = !matchClientDebloatTest;
        }
      }

      let matchClientDebloat = false;
      if ($scope.filters.clientDebloat != 'all') {
        matchClientDebloat = !client.debloat_test;
        if ($scope.filters.clientDebloat == 'pass') {
          matchClientDebloat = !matchClientDebloat;
        }
      }

      let matchClient = false;
      if ($scope.filters.client != 'all') {
        matchClient = !client.compiled;
        if ($scope.filters.client == 'pass') {
          matchClient = !matchClient;
        }
      }

      return (matchClientDebloatTest || matchClientDebloat) || matchClient;
    }

    $scope.openLib = function (lib) {
      $scope.currentLibName = lib;
      $scope.currentVersions = $scope.bugs[$scope.currentLibName];

      const firstLib = Object.values($scope.currentVersions).filter($scope.versionFilter)[0];
      
      for (let i in $scope.currentVersions) {
        if ($scope.currentVersions[i] == firstLib) {
          return $scope.openVersion(i);
        }
      }
    };
    $scope.openVersion = function (version) {
      $scope.currentVersionName = version;
      $scope.currentVersion = $scope.currentVersions[$scope.currentVersionName];
      $scope.currentClients = $scope.currentVersion.clients;

      const firstLib = Object.values($scope.currentClients).filter($scope.clientFilter)[0];
      
      for (let i in $scope.currentClients) {
        if ($scope.currentClients[i] == firstLib) {
          $scope.openClient(i);
          break;
        }
      }

      const key = $scope.currentLibName + "_" + $scope.currentVersionName;
      $scope.currentLibCategories = $scope.libsCategories[key] || [];
    };

    $scope.openClient = function (client) {
      $scope.currentClientName = client;
      $scope.currentClient = $scope.currentClients[$scope.currentClientName];

      $scope.getLog();

      const key =
        $scope.currentLibName +
        "_" +
        $scope.currentVersionName +
        "_" +
        $scope.currentClientName;
      $scope.currentClientCategories = $scope.clientsCategories[key] || [];
    };

    $scope.getLog = function () {
      $scope.currentFrameworkLog = "Loading!";
      $scope.currentLibBuildLog = "Loading!";
      $scope.currentLibDebloatLog = "Loading!";
      $scope.currentClientBuildLog = "Loading!";
      $scope.currentClientDebloatLog = "Loading!";

      const lib_repo = $scope.currentVersion.repo_name.replace("/", "_");
      const client_repo = $scope.currentClient.repo_name.replace("/", "_");

      const base =
        "/data/" +
        $scope.currentLibName +
        "/" +
        $scope.currentVersionName +
        "/";
      $http
        .get("/data/executions/" + lib_repo + "_" + client_repo + ".log")
        .then(
          function (response) {
            $scope.currentFrameworkLog = response.data;
          },
          () => {
            $scope.currentFrameworkLog = "";
          }
        );
      $http.get(base + "/original/execution.log").then(
        function (response) {
          $scope.currentLibBuildLog = response.data;
        },
        () => {
          $scope.currentLibBuildLog = "";
        }
      );
      $http.get(base + "/debloat/execution.log").then(
        function (response) {
          $scope.currentLibDebloatLog = response.data;
        },
        () => {
          $scope.currentLibDebloatLog = "";
        }
      );
      $http
        .get(
          base +
            "/clients/" +
            $scope.currentClientName +
            "/original/execution.log"
        )
        .then(
          function (response) {
            $scope.currentClientBuildLog = response.data;
          },
          () => {
            $scope.currentClientBuildLog = "";
          }
        );
      $http
        .get(
          base +
            "/clients/" +
            $scope.currentClientName +
            "/debloat/execution.log"
        )
        .then(
          function (response) {
            $scope.currentClientDebloatLog = response.data;
          },
          () => {
            $scope.currentClientDebloatLog = "";
          }
        );
    };

    $scope.newClientCategory = "";
    $scope.newLibCategory = "";

    $scope.addLibCategory = function (caterogy) {
      const key = $scope.currentLibName + "_" + $scope.currentVersionName;
      $http
        .post(
          "/api/" +
            $scope.currentLibName +
            "/" +
            $scope.currentVersionName +
            "/" +
            caterogy
        )
        .then(() => {
          if (!$scope.libsCategories[key]) {
            $scope.libsCategories[key] = [];
          }
          let index = $scope.libsCategories[key].indexOf(caterogy);
          if (index > -1) {
            $scope.libsCategories[key].splice(index, 1);
            index = $scope.currentLibCategories.indexOf(caterogy);
            if (index > -1) {
              $scope.currentLibCategories.splice(index, 1);
            }
          } else {
            $scope.libsCategories[key].push(caterogy);
            $scope.currentLibCategories.push(caterogy);
          }
        });
    };

    $scope.createLibCategory = function () {
      if ($scope.libCategories.indexOf($scope.newLibCategory) == -1) {
        $scope.libCategories.push($scope.newLibCategory);
        $scope.addLibCategory($scope.newLibCategory);
      }
      $scope.newLibCategory = "";
    };

    $scope.addClientCategory = function (caterogy) {
      const key =
        $scope.currentLibName +
        "_" +
        $scope.currentVersionName +
        "_" +
        $scope.currentClientName;
      $http
        .post(
          "/api/" +
            $scope.currentLibName +
            "/" +
            $scope.currentVersionName +
            "/" +
            $scope.currentClientName +
            "/" +
            caterogy
        )
        .then(() => {
          if (!$scope.clientsCategories[key]) {
            $scope.clientsCategories[key] = [];
          }
          let index = $scope.clientsCategories[key].indexOf(caterogy);
          if (index > -1) {
            $scope.clientsCategories[key].splice(index, 1);
            index = $scope.currentClientCategories.indexOf(caterogy);
            if (index > -1) {
              $scope.currentClientCategories.splice(index, 1);
            }
          } else {
            $scope.clientsCategories[key].push(caterogy);
            $scope.currentClientCategories.push(caterogy);
          }
        });
    };

    $scope.createClientCategory = function () {
      if ($scope.clientCategories.indexOf($scope.newClientCategory) == -1) {
        $scope.clientCategories.push($scope.newClientCategory);
        $scope.addClientCategory($scope.newClientCategory);
      }
      $scope.newClientCategory = "";
    };

    $scope.naturalCompare = function (a, b) {
      if (a.type === "number") {
        return a.value - b.value;
      }
      return naturalSort(a.value, b.value);
    };
  });
