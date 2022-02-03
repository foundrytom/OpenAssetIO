#!/usr/bin/env bash
set -xeo pipefail
sudo apt-get update
# Install gcc and Python 3 (via pip, which will bring along Python 3 as
# a dependency).
sudo apt-get install -y build-essential python3-pip
# Install additional build tools.
sudo pip3 install conan cmake==3.21 ninja
# root doesn't have /usr/local on PATH, which is needed for
# pip-installed binaries.
export PATH=/usr/local/bin:$PATH
# Use alternative conan root path, so user doesn't need access to /root.
export CONAN_USER_HOME=$HOME/conan
# Use old C++11 ABI as per VFX ref platform <= 2022.
conan config set compiler.libcxx=libstdc++
# Install openassetio third-party dependencies from public Conan Center
# package repo.
conan install --install-folder $HOME/conan --build=missing $GITHUB_WORKSPACE/ci
