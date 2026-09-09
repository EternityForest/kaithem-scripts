#!/bin/bash
if ! command -v uv &> /dev/null
then
    if ! command -v pipx &> /dev/null
    then
        echo "pipx not installed, installing"
        sudo apt install -y pipx
    else
        echo "pipx already installed"
    fi

    echo "UV not installed, installing"
    python3 -m pipx ensurepath
    python3 -m pipx install uv
    uv tool update-shell
else
    echo "UV already installed"
fi