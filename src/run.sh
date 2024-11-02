#!/bin/bash

# Configuration
DIR=$(realpath "$(dirname $0)/../")
DOTENV="$DIR/.env"
BOT_SCRIPT="$DIR/src/bot_service.py"
API_SCRIPT="$DIR/src/api_service.py"
VENV_ACTIVATE="$DIR/.venv/bin/activate"

LOG_DIR="$DIR/logs"
DATE=$(date '+%Y-%m-%d %H:%M:%S')
mkdir -p "$LOG_DIR"

# Function to activate virtual environment
activate_venv() {
  source $VENV_ACTIVATE
  source $DOTENV
  local python=$(which python)
  if [ ! -f "$python" ]; then
    echo "Error: Failed to activate virtual environment. '$python' does not exist."
    exit 1
  fi
}


# Function to start the API server
start_api_service() {
  local script=$1
  local mode=$2
  local log_file="$LOG_DIR/$(basename ${script%.*}).log"
  echo "Starting $script..." >&2
  echo -e "---[API][$DATE]----------------------------------------------\n">> $log_file
  if [ "$mode" = "dev" ]; then
    nohup fastapi dev "$script" >> "$log_file" 2>&1 &
  else
    nohup fastapi run "$script" >> "$log_file" 2>&1 &
  fi
  echo $!
}

# Function to start the bot service
start_bot_service() {
  local script=$1
  local log_file="$LOG_DIR/$(basename ${script%.*}).log"
  echo "Starting $script..." >&2
  echo -e "---[BOT][$DATE]----------------------------------------------\n">> $log_file
  PYTHONUNBUFFERED=1 nohup python "$script" >> "$log_file" 2>&1 &
  echo $!
}

# Function to cleanup processes on exit
cleanup() {
  echo "Stopping services..."
  if [ ! -z "$BOT_PID" ]; then
    kill $BOT_PID 2>/dev/null
  fi
  if [ ! -z "$API_PID" ]; then
    kill $API_PID 2>/dev/null
  fi
  exit 0
}

# Function to check if a process is running
check_process() {
  local pid=$1
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "process $pid dead"
    return 1
  fi
  return 0
}

# -------------------------------------------------------------------------------------

trap cleanup EXIT INT TERM

if [ ! -f "$BOT_SCRIPT" ]; then
  echo "Error: $BOT_SCRIPT not found"
  exit 1
fi

if [ ! -f "$API_SCRIPT" ]; then
  echo "Error: $API_SCRIPT not found"
  exit 1
fi

if [ ! -f "$VENV_ACTIVATE" ]; then
  echo "Error: $VENV_ACTIVATE not found"
  exit 1
fi

activate_venv

BOT_PID=$(start_bot_service "$BOT_SCRIPT")
echo "BOT_PID=$BOT_PID"

API_PID=$(start_api_service "$API_SCRIPT")
echo "API_PID=$API_PID"

# Monitor processes
while true; do
  if ! check_process "$BOT_PID"; then
    echo "Bot script crashed, restarting..."
    BOT_PID=$(start_bot_service "$BOT_SCRIPT")
    echo "BOT_PID=$BOT_PID"
  fi
  if ! check_process "$API_PID"; then
    echo "API script crashed, restarting..."
    API_PID=$(start_api_service "$API_SCRIPT")
    echo "API_PID=$API_PID"
  fi
  sleep 5
done
