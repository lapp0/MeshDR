{
  description = "Mesh Domain Randomization";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/release-21.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python39;
        pythonPackages = python.pkgs;

        python-lxml = pythonPackages.buildPythonPackage rec {
          pname = "lxml";
          version = "4.8.0";

          src = pkgs.fetchFromGitHub {
            owner = pname;
            repo = pname;
            rev = "lxml-${version}";
            sha256 = "sha256-ppyLn8B0YFQivRCOE8TjKGdDDQHbb7UdTUkevznoVC8=";
          };

          # setuptoolsBuildPhase needs dependencies to be passed through nativeBuildInputs
          nativeBuildInputs = with pkgs; [ libxml2.dev libxslt.dev pythonPackages.cython ] ++ lib.optionals stdenv.isDarwin [ xcodebuild ];
          buildInputs = with pkgs; [ libxml2 libxslt zlib ];

          # tests are meant to be ran "in-place" in the same directory as src
          doCheck = false;

          pythonImportsCheck = [ "lxml" "lxml.etree" ];
        };

        python-requests = pythonPackages.buildPythonPackage rec {
          pname = "requests";
          version = "2.27.1";

          src = pythonPackages.fetchPypi {
            inherit pname version;
            hash = "sha256-aNfFb9WomZiHco7zBKbRLtx7508c+kdxT8i0FFJcmmE=";
          };

          propagatedBuildInputs = with pythonPackages; [
            certifi
            idna
            urllib3
            chardet
          ] ++ pkgs.lib.optionals isPy3k [
            brotlicffi
            charset-normalizer
          ] ++ pkgs.lib.optionals isPy27 [
            brotli
          ];
          doCheck = false;
        };

        /*
        pythonPackagesOverridden = pythonPackages.override {
          requests = python-requests;
          lxml = python-lxml;
        };
        */

        pygem = pythonPackages.buildPythonPackage rec {
          pname = "pygem";
          version = "0.1.6";
          src = pythonPackages.fetchPypi {
            inherit pname version;
            sha256 = "sha256-30MGGMJe7lcsvSqp+hU/AcTpiuihgJLT3OmpZmEkXm4=";
          };
          propagatedBuildInputs = with pythonPackages; [
            numpy
            scipy
            matplotlib
            pandas
            python-lxml
            python-requests
          ];
          checkInputs = with pythonPackages; [
            python-requests
            pytest
          ];
        };

      in {
        packages.meshdr = pkgs.callPackage
          ({ stdenv, lib }:
            pythonPackages.buildPythonPackage rec {
              pname = "meshdr";
              version = "1.0.0";
              src = ./.;
              propagatedBuildInputs = [
                pygem
              ];
              doCheck = false;
            }) { };
        defaultPackage = self.packages.${system}.meshdr;
        apps = {
          meshdr = flake-utils.lib.mkApp {
            drv = self.packages."${system}".meshdr;
          };
        };
        devShell = pkgs.mkShell {
          nativeBuildInputs = [
            python
          ];
          inputsFrom = [
            self.packages."${system}".meshdr
          ];
        };
      }
    );
}
