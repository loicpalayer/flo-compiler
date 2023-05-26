{pkgs ? import <nixpkgs> {}}:
with pkgs; # Same for pkgs.

  mkShell {
    buildInputs = [
      # Defines a python + set of packages.
      (python3.withPackages (ps:
        with ps;
        with python3Packages; [
          sly
          yapf
          syrupy
          pytest
        ]))
      nasm
    ];
  }
