#!/bin/bash

# Default Port
PORT=23000

# 1. Handle Arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -p|--port)
      PORT="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: ./simulator.sh [-p|--port PORT]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# 2. Setup Variables
SESSION="experiment_a_study_$PORT"
RUN_DIR="runs"
mkdir -p "$RUN_DIR"

# Define commands with absolute clarity for pgrep
SIM_CMD="coppeliasim -h -GzmqRemoteApi.rpcPort=$PORT scenes/example_a_pick_place.ttt"
PY_CMD="conda activate rpenv && python3 -u manipulator_study.py -p $PORT"

echo "Initializing Session: $SESSION on Port: $PORT"

# 3. Tmux Orchestration
tmux kill-session -t "$SESSION" 2>/dev/null
tmux new-session -d -s "$SESSION" -n runner

# Layout: Top (Supervisor), Bottom-Left (Sim), Bottom-Right (Python)
tmux split-window -v -t "$SESSION:runner"
tmux select-pane -t 1
tmux split-window -h -t "$SESSION:runner"

# 4. Start Supervisor Loop
# We use a heredoc (EOF) to make the nested quoting much easier to read
tmux select-pane -t 0
tmux send-keys "
while true; do
    TIMESTAMP=\$(date +'%Y_%m_%d_%H_%M_%S')
    LOG_DIR='$RUN_DIR'/\$TIMESTAMP
    mkdir -p \$LOG_DIR

    echo '======================================'
    echo \"Starting Experiment on PORT: $PORT\"
    echo \"Logs: \$LOG_DIR\"
    echo '======================================'

    # Launch Simulator in Pane 1
    tmux send-keys -t $SESSION:runner.1 \"clear; $SIM_CMD 2>&1 | tee \$LOG_DIR/simulator.log\" C-m
    sleep 8

    # Launch Python in Pane 2
    tmux send-keys -t $SESSION:runner.2 \"clear; bash -i -c '$PY_CMD' 2>&1 | tee \$LOG_DIR/python.log\" C-m
    sleep 5

    # CAPTURE PIDs - specifically matching the PORT
    # -n (newest) ensures we don't grab a zombie from a previous crash
    SIM_PID=\$(pgrep -nf \"coppeliaSim.*rpcPort=$PORT\")
    PY_PID=\$(pgrep -nf \"manipulator_study.py.*-p $PORT\")

    if [ -z \"\$SIM_PID\" ] || [ -z \"\$PY_PID\" ]; then
        echo \"[ERROR] Could not find PIDs! Sim: \$SIM_PID | Py: \$PY_PID\"
        echo \"Attempting cleanup and restart...\"
    else
        echo \"Monitoring Sim (\$SIM_PID) and Python (\$PY_PID)...\"
        
        while true; do
            # Check if both are still alive
            kill -0 \$SIM_PID 2>/dev/null || { echo 'Simulator stopped.'; break; }
            kill -0 \$PY_PID 2>/dev/null || { echo 'Python script stopped.'; break; }
            sleep 3
        done
    fi

    # CLEANUP PHASE
    echo \"Cleaning up processes for Port $PORT...\"
    
    # Try graceful kill first
    [ -n \"\$PY_PID\" ] && kill \$PY_PID 2>/dev/null
    [ -n \"\$SIM_PID\" ] && kill \$SIM_PID 2>/dev/null
    sleep 2

    # Force kill by PID
    [ -n \"\$PY_PID\" ] && kill -9 \$PY_PID 2>/dev/null
    [ -n \"\$SIM_PID\" ] && kill -9 \$SIM_PID 2>/dev/null

    # Absolute safety: kill anything left on this specific port
    pkill -9 -f \"rpcPort=$PORT\" 2>/dev/null
    pkill -9 -f \"exploration.py.*-p $PORT\" 2>/dev/null

    echo 'Restarting in 5 seconds...'
    sleep 5
done
" C-m

# 5. Attach
tmux attach -t "$SESSION"