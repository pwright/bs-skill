#!/usr/bin/env bash
set -euo pipefail
cat - | python -m skill.cli --provider codex
