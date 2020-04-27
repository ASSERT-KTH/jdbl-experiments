angular
  .module("jdbl-website", ["ngRoute", "anguFixedHeaderTable"])
  .directive("keypressEvents", [
    "$document",
    "$rootScope",
    function($document, $rootScope) {
      return {
        restrict: "A",
        link: function() {
          $document.bind("keydown", function(e) {
            $rootScope.$broadcast("keypress", e);
            $rootScope.$broadcast("keypress:" + e.which, e);
          });
        }
      };
    }
  ])
  .controller("libController", function(
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

    $scope.$watch("$parent.filteredBugs", function() {
      $ctrl.bugs = $scope.$parent.filteredBugs;
      $ctrl.index = getIndex($routeParams.benchmark, $routeParams.id);
    });
    $scope.$watch("$parent.classifications", function() {
      $ctrl.classifications = $scope.$parent.classifications;
    });

    var getIndex = function(benchmark, bugId) {
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

    $scope.$on("$routeChangeStart", function(next, current) {
      $ctrl.index = getIndex(current.params.benchmark, current.params.id);
    });

    var modalInstance = null;
    $scope.$watch("index", function() {
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
              bug: function() {
                return $scope.bugs[$scope.index];
              },
              classifications: $scope.classifications
            }
          });
          modalInstance.result.then(
            function() {
              modalInstance = null;
              $location.path("/");
            },
            function() {
              modalInstance = null;
              $location.path("/");
            }
          );
        } else {
          $rootScope.$emit("new_bug", $scope.bugs[$scope.index]);
        }
      }
    });
    var nextPatch = function() {
      var index = $scope.index + 1;
      if (index == $ctrl.bugs.length) {
        index = 0;
      }
      $location.path(
        "/bug/" + $ctrl.bugs[index].benchmark + "/" + $ctrl.bugs[index].bugId
      );
      return false;
    };
    var previousPatch = function() {
      var index = $scope.index - 1;
      if (index < 0) {
        index = $ctrl.bugs.length - 1;
      }
      $location.path(
        "/bug/" + $ctrl.bugs[index].benchmark + "/" + $ctrl.bugs[index].bugId
      );
      return false;
    };

    $scope.$on("keypress:39", function() {
      $scope.$apply(function() {
        nextPatch();
      });
    });
    $scope.$on("keypress:37", function() {
      $scope.$apply(function() {
        previousPatch();
      });
    });
    $rootScope.$on("next_bug", nextPatch);
    $rootScope.$on("previous_bug", previousPatch);
  })
  .filter("percentage", [
    "$filter",
    function($filter) {
      return function(input, decimals) {
        return $filter("number")(input * 100, decimals) + "%";
      };
    }
  ])
  .controller("mainController", function($scope, $http) {
    $scope.sortType = ["benchmark", "bugId"]; // set the default sort type
    $scope.sortReverse = false;
    $scope.match = "all";
    $scope.filters = {};

    // create the list of sushi rolls
    $scope.bugs = [];
    $scope.currentLibName = "";
    $scope.currentVersions = [];
    $scope.currentVersionName = "";
    $scope.currentClients = {};
    $scope.currentClientName = "";
    $scope.currentClient = {};
    $scope.currentLog = "";

    $http.get("data/raw_results.json").then(function(response) {
      $scope.bugs = response.data;
      $scope.openLib(Object.keys($scope.bugs)[0]);
    });

    $scope.openLib = function(lib) {
      $scope.currentLibName = lib;
      $scope.currentVersions = $scope.bugs[$scope.currentLibName];
      $scope.openVersion(Object.keys($scope.currentVersions)[0]);
    };
    $scope.openVersion = function(version) {
      $scope.currentVersionName = version;
      $scope.currentVersion = $scope.currentVersions[$scope.currentVersionName];
      $scope.currentClients = $scope.currentVersion.clients;
      $scope.openClient(Object.keys($scope.currentClients)[0]);
    };

    $scope.openClient = function(client) {
      $scope.currentClientName = client;
      $scope.currentClient = $scope.currentClients[$scope.currentClientName];

      $scope.getLog();
    };

    $scope.getLog = function() {
      $scope.currentLog = "";
      const lib_repo = $scope.currentVersion.repo_name.replace("/", "_");
      const client_repo = $scope.currentClient.repo_name.replace("/", "_");
      $http
        .get("data/logs/" + lib_repo + "_" + client_repo + ".log")
        .then(function(response) {
          $scope.currentLog = response.data;
        });
    };

    $scope.naturalCompare = function(a, b) {
      if (a.type === "number") {
        return a.value - b.value;
      }
      return naturalSort(a.value, b.value);
    };
  });
