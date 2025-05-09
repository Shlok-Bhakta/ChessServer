{
  description = "Dev flake for a Python Flask chess server with libsql";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        pythonWP = pkgs.python313.withPackages (
          ps: with ps; [
            flask
            requests
          ]
        );
        startScript = pkgs.writeShellScriptBin "start" ''
          bash start.sh
        '';
        stopScript = pkgs.writeShellScriptBin "stop" ''
          bash stop.sh
        '';
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonWP
            pkgs.sqld
            pkgs.sqlite
            startScript
            stopScript
          ];
          shellHook = ''
            export FLASK_APP=app.py

            BACKEND_PORT=7456
            FRONTEND_PORT=7457

            echo "Python Flask chess dev shell with libsql ready!"
            zsh
          '';
        };
      }
    );
}
