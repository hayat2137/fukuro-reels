#!/usr/bin/env bash
# VOICEVOX core 0.17.1 を /home/claude/vv に用意する（ちび式じい = style 42）
set -euo pipefail
VV=/home/claude/vv
mkdir -p "$VV" && cd "$VV"
pip install --break-system-packages -q https://github.com/VOICEVOX/voicevox_core/releases/download/0.17.1/voicevox_core-0.17.1-cp310-abi3-manylinux_2_34_x86_64.whl
[ -d voicevox_onnxruntime-linux-x64-1.23.2 ] || { curl -sSLO https://github.com/VOICEVOX/onnxruntime-builder/releases/download/voicevox_onnxruntime-1.23.2/voicevox_onnxruntime-linux-x64-1.23.2.tgz && tar xzf voicevox_onnxruntime-linux-x64-1.23.2.tgz; }
[ -f 10.vvm ] || curl -sSL -o 10.vvm https://github.com/VOICEVOX/voicevox_vvm/releases/download/0.17.1/10.vvm
[ -d open_jtalk_dic_utf_8-1.11 ] || { curl -sSL -o dict.tgz https://github.com/r9y9/open_jtalk/releases/download/v1.11.1/open_jtalk_dic_utf_8-1.11.tar.gz && tar xzf dict.tgz; }
echo "voicevox ready"
