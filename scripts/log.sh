#!/usr/bin/env bash
#
# Define a function (log) that takes a level and a message and logs it (with color)
#
# Import this function into another script with the source command:
#     source log.sh
#
# Usage:
#
#     log "info" "This is an info message"
#     log "warn" "This is a warning message"
#     log "error" "This is an error message"
#     log "success" "This is a success message"
#

log() {
  local level=$1
  local message=$2
  local color

  case $level in
    "info")
      color="\033[0;34m"
      ;;
    "warn")
      color="\033[0;33m"
      ;;
    "error")
      color="\033[0;31m"
      ;;
    "success")
      color="\033[0;32m"
      ;;
    *)
      color="\033[0m"
      ;;
  esac

  echo -e "$color[$level]\033[0m $message"
}

newlines() {
  local n=$1
  for i in $(seq 1 $n); do
    echo ""
  done
}
