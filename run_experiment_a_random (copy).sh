#!/bin/bash
# Set a default port
PORT=23000

# Loop through all arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -p|--port)
      PORT="$2"
      shift # Past the flag
      shift # Past the value
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

echo "Connecting to simulator on port: $PORT"

SESSION="experiment_a_random_$PORT"

SIM_CMD="coppeliasim -h -GzmqRemoteApi.rpcPort=$PORT scenes/example_a_pick_place.ttt"
PY_CMD="conda activate rpenv && python3 manipulator_random_exploration.py -p $PORT"

RUN_DIR="runs"
mkdir -p $RUN_DIR

# Kill old session if exists
tmux kill-session -t $SESSION 2>/dev/null

# Create new session detached
tmux new-session -d -s $SESSION -n runner

# Split top/bottom (50/50)
tmux split-window -v -t $SESSION:runner

# Bottom pane split vertically (left=sim, right=python)
tmux select-pane -t 1
tmux split-window -h -t $SESSION:runner

# Pane mapping
# pane 0: top → supervisor/runner
# pane 1: bottom-left → simulator
# pane 2: bottom-right → python

# Start supervisor loop in top pane
tmux select-pane -t 0
tmux send-keys "
while true; do
    TIMESTAMP=\$(date +'%Y_%m_%d_%H_%M_%S')
    LOG_DIR='$RUN_DIR'/\$TIMESTAMP
    mkdir -p \$LOG_DIR

    echo '======================================'
    echo \"Starting new experiment run\"
    echo \"Timestamp: \$TIMESTAMP\"
    echo \"Logs: \$LOG_DIR\"
    echo '======================================'

    # Launch simulator in bottom-left pane
    tmux send-keys -t $SESSION:runner.1 \"clear; echo 'Launching CoppeliaSim'; $SIM_CMD 2>&1 | tee \$LOG_DIR/simulator.log\" C-m

    sleep 5

    # Launch python in bottom-right pane
    tmux send-keys -t $SESSION:runner.2 \"clear; echo 'Launching Python script'; bash -i -c '$PY_CMD' 2>&1 | tee \$LOG_DIR/python.log\" C-m

    sleep 2

    SIM_PID=\$(pgrep -f example_a_pick_place.ttt)
    PY_PID=\$(pgrep -f manipulator_random_exploration.py)


    

    echo \"Simulator PID: \$SIM_PID\"
    echo \"Python PID: \$PY_PID\"
    echo \"Connected to port: $PORT\"
    echo \"Session: $SESSION\"

    # Monitor both processes
    while true; do
        SIM_RUNNING=1
        PY_RUNNING=1

        kill -0 \$SIM_PID 2>/dev/null || SIM_RUNNING=0
        kill -0 \$PY_PID 2>/dev/null || PY_RUNNING=0

        if [ \$SIM_RUNNING -eq 0 ] && [ \$PY_RUNNING -eq 0 ]; then
            echo 'Both processes exited.'
            break
        elif [ \$SIM_RUNNING -eq 0 ]; then
            echo 'Simulator exited!'
            break
        elif [ \$PY_RUNNING -eq 0 ]; then
            echo 'Python script exited!'
            break
        fi

        sleep 2
    done

    echo ''
    echo 'Restarting experiment...'
    echo ''

    kill -9 $SIM_PID #example_a_pick_place.ttt
    kill -9 $PY_PID #manipulator_random_exploration.py

    sleep 3
done
" C-m

# Attach to tmux session
tmux attach -t $SESSION