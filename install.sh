#!/bin/bash

# apt dependencies
./install_deps.sh

# symlink gdb
sudo ln /usr/bin/gdb-multiarch /usr/bin/arm-none-eabi-gdb

# python3 venv
mkdir ~/envs
python3 -m venv ~/envs/halucinator
source ~/envs/halucinator/bin/activate

# python dependencies
pip install -r src/requirements.txt
pip install -e src

# avatar2
python -m avatar2.installer

# exit venv
deactivate

# env variables
echo "export HALUCINATOR_QEMU=\`readlink -f ~/.avatar2/avatar-qemu/arm-softmmu/qemu-system-arm\`" >> ~/envs/halucinator/bin/activate
