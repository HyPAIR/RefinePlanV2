#!/bin/bash

############################################
# args
############################################

PERM=$1
PORT=$2
PRIORITY=$3   # optional

if [ -z "$PERM" ] || [ -z "$PORT" ]; then
    echo "Usage: ./worker_tmux_single.sh <perm_index> <port> [priority=random|informed]"
    exit 1
fi

if [ -z "$PRIORITY" ]; then
    PRIORITY="random"
fi

############################################
# dataset order
############################################

if [ "$PRIORITY" == "informed" ]; then
    COLLECTION_NAMES=("pick-place-random")
else
    COLLECTION_NAMES=("pick-place-random")
fi

############################################
# config
############################################

SESSION="worker_perm_${PERM}_port_${PORT}"
PROJECT_DIR="$(pwd)"
RUN_ROOT="$PROJECT_DIR/runs_perm_${PERM}_$(date +%Y_%m_%d_%H_%M_%S)"

LIMIT_START=15000
LIMIT_END=16000
LIMIT_STEP=1000

mkdir -p "$RUN_ROOT"

SIM_CMD="coppeliasim -h -GzmqRemoteApi.rpcPort=$PORT $PROJECT_DIR/scenes/example_a_pick_place.ttt"

echo "Starting Worker | Perm=$PERM | Port=$PORT | Priority=$PRIORITY"

############################################
# tmux setup
############################################

tmux kill-session -t "$SESSION" 2>/dev/null
tmux new-session -d -s "$SESSION" -n runner -c "$PROJECT_DIR"

# Layout: top runner, bottom split
tmux split-window -v -t "$SESSION:runner"
tmux select-pane -t 1
tmux split-window -h -t "$SESSION:runner"

############################################
# supervisor loop
############################################

tmux select-pane -t 0
tmux send-keys "
cd $PROJECT_DIR

source ~/anaconda3/etc/profile.d/conda.sh

# dynamic totals
NUM_DATASETS=\${#COLLECTION_NAMES[@]}
NUM_LIMITS=\$(( (LIMIT_END - LIMIT_START) / LIMIT_STEP + 1 ))
TOTAL=\$(( NUM_DATASETS * NUM_LIMITS ))

RUN_COUNT=0

echo \"Datasets: \$NUM_DATASETS | Limits: \$NUM_LIMITS | Total: \$TOTAL\"

for DATASET in ${COLLECTION_NAMES[@]}; do
for ((LIMIT=$LIMIT_START; LIMIT<=$LIMIT_END; LIMIT+=$LIMIT_STEP)); do

    RUN_COUNT=\$((RUN_COUNT+1))

    TIMESTAMP=\$(date +'%Y_%m_%d_%H_%M_%S')
    LOG_DIR='$RUN_ROOT'/\${TIMESTAMP}_\${DATASET}_L\${LIMIT}
    mkdir -p \$LOG_DIR

    echo '======================================'
    echo \"Run \$RUN_COUNT / \$TOTAL\"
    echo \"Dataset: \$DATASET | Limit: \$LIMIT | Perm: $PERM | Port: $PORT\"
    echo \"Logs: \$LOG_DIR\"
    echo '======================================'

    ################################
    # launch simulator
    ################################

    tmux send-keys -t $SESSION:runner.1 \"clear; $SIM_CMD 2>&1 | tee \$LOG_DIR/simulator.log\" C-m
    sleep 8

    ################################
    # launch python
    ################################

    tmux send-keys -t $SESSION:runner.2 \"clear; bash -i -c 'conda activate rpenv && python3 -u policy_executor.py -p $PORT -l \$LIMIT -i $PERM -d \$DATASET' 2>&1 | tee \$LOG_DIR/python.log\" C-m
    sleep 5

    ################################
    # capture PIDs (robust)
    ################################

    SIM_PID=\$(pgrep -nf \"coppeliaSim.*rpcPort=$PORT\")
    PY_PID=\$(pgrep -nf \"policy_executor.py.*-p $PORT\")

    if [ -z \"\$SIM_PID\" ] || [ -z \"\$PY_PID\" ]; then
        echo \"[ERROR] PID detection failed! Sim: \$SIM_PID | Py: \$PY_PID\"
    else
        echo \"Monitoring Sim (\$SIM_PID) and Python (\$PY_PID)...\"

        while true; do
            kill -0 \$SIM_PID 2>/dev/null || { echo 'Simulator stopped.'; break; }
            kill -0 \$PY_PID 2>/dev/null || { echo 'Python stopped.'; break; }
            sleep 3
        done
    fi

    ################################
    # cleanup
    ################################

    echo \"Cleaning up...\"

    [ -n \"\$PY_PID\" ] && kill \$PY_PID 2>/dev/null
    [ -n \"\$SIM_PID\" ] && kill \$SIM_PID 2>/dev/null
    sleep 2

    [ -n \"\$PY_PID\" ] && kill -9 \$PY_PID 2>/dev/null
    [ -n \"\$SIM_PID\" ] && kill -9 \$SIM_PID 2>/dev/null

    pkill -9 -f \"rpcPort=$PORT\" 2>/dev/null
    pkill -9 -f \"policy_executor.py.*-p $PORT\" 2>/dev/null

    echo 'Next run in 3 seconds...'
    sleep 3

done
done

echo 'All runs complete.'
" C-m

############################################
# attach
############################################

tmux attach -t "$SESSION"