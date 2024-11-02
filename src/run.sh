#!/bin/bash

DIR=$(realpath "$(dirname $0)/../")
DOTENV="$DIR/.env"
BOT_SCRIPT="$DIR/src/bot_service.py"
API_SCRIPT="$DIR/src/api_service.py"
VENV_ACTIVATE="$DIR/.venv/bin/activate"

LOG_DIR="$DIR/logs"

get_date() {
  date '+%Y-%m-%d %H:%M:%S'
}

log() {
  # $1 - INFO, DEBUG, WARN, ERROR
  printf "| %s | %-5s | %s\n" "$(get_date)" "$1" "$2" >&2
}

activate_venv() {
  source $VENV_ACTIVATE
  source $DOTENV
  local python=$(which python)
  if [ ! -f "$python" ]; then
    log ERROR "Failed to activate venv. '$python' does not exist."
    exit 1
  fi
}

start_api_service() {
  local script=$1
  local mode=$2
  local log_file="$LOG_DIR/$(basename ${script%.*}).log"
  echo -e "---[API][$(get_date)]--------------------------------------------\n">> $log_file
  if [ "$mode" = "dev" ]; then
    FORCE_COLOR=1 nohup fastapi dev "$script" >> "$log_file" 2>&1 &
  else
    FORCE_COLOR=1 nohup fastapi run "$script" >> "$log_file" 2>&1 &
  fi
  log INFO "started API service [PID: $(echo $!)]"
}

start_bot_service() {
  local script=$1
  local log_file="$LOG_DIR/$(basename ${script%.*}).log"
  echo -e "---[BOT][$(get_date)]--------------------------------------------\n">> $log_file
  PYTHONUNBUFFERED=1 FORCE_COLOR=1 nohup python "$script" >> "$log_file" 2>&1 &
  log INFO "started BOT service [PID: $(echo $!)]"
}

cleanup() {
  log INFO "stopping services"
  if [ ! -z "$BOT_PID" ]; then
    kill $BOT_PID 2>/dev/null
  fi
  if [ ! -z "$API_PID" ]; then
    kill $API_PID 2>/dev/null
  fi
  exit 0
}

check_process() {
  local pid=$1
  if ! kill -0 "$pid" 2>/dev/null; then
    return 1
  fi
  return 0
}

# -------------------------------------------------------------------------------------

trap cleanup EXIT INT TERM

if [ ! -f "$BOT_SCRIPT" ]; then
  log ERROR "$BOT_SCRIPT not found"
  exit 1
fi

if [ ! -f "$API_SCRIPT" ]; then
  log ERROR "$API_SCRIPT not found"
  exit 1
fi

if [ ! -f "$VENV_ACTIVATE" ]; then
  log ERROR "$VENV_ACTIVATE not found"
  exit 1
fi

mkdir -p "$LOG_DIR"
activate_venv

BOT_PID=$(start_bot_service "$BOT_SCRIPT")
API_PID=$(start_api_service "$API_SCRIPT")

while true; do
  if check_process "$BOT_PID"; then
    log ERROR "BOT service crashed... restarting."
    BOT_PID=$(start_bot_service "$BOT_SCRIPT")
  fi
  if check_process "$API_PID"; then
    log ERROR "API service crashed... restarting."
    API_PID=$(start_api_service "$API_SCRIPT")
  fi
  sleep 5
done
