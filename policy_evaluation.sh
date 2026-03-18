#!/bin/bash

############################################
# configuration
############################################

export OMP_NUM_THREADS=1

BASE_PORT=23010
SESSION="policy_runs"

COLLECTION_NAMES="pick-place-random pick-place-informed"

LIMIT_START=500
LIMIT_END=8000
LIMIT_STEP=500

PERM_INDEXES=(0 1 2 3 4 5)

PROJECT_DIR="$(pwd)"
SCENE="$PROJECT_DIR/scenes/example_a_pick_place.ttt"

RUN_ROOT="$PROJECT_DIR/runs_$(date +%Y_%m_%d_%H_%M_%S)"
MANIFEST="$RUN_ROOT/manifest.csv"

mkdir -p "$RUN_ROOT"

echo "dataset,perm,limit,port,status" > "$MANIFEST"

RUNS_PER_WORKER=$(( 2 * ((LIMIT_END-LIMIT_START)/LIMIT_STEP + 1) ))

############################################
# create tmux dashboard
############################################

tmux kill-session -t $SESSION 2>/dev/null

tmux new-session -d -s $SESSION -c "$PROJECT_DIR"

tmux split-window -h -c "$PROJECT_DIR"
tmux split-window -v -c "$PROJECT_DIR"
tmux select-pane -t 0
tmux split-window -v -c "$PROJECT_DIR"
tmux select-pane -t 2
tmux split-window -v -c "$PROJECT_DIR"
tmux select-pane -t 4
tmux split-window -v -c "$PROJECT_DIR"

tmux select-layout tiled

############################################
# launch workers
############################################

for PERM in "${PERM_INDEXES[@]}"; do

PORT=$((BASE_PORT + PERM))

tmux send-keys -t $PERM "

cd $PROJECT_DIR

source ~/anaconda3/etc/profile.d/conda.sh
conda activate rpenv

RUN_COUNT=0
TOTAL=$RUNS_PER_WORKER

progress_bar() {
    local progress=\$1
    local total=\$2
    local width=30

    local filled=\$((progress * width / total))
    local empty=\$((width - filled))

    printf '['
    printf '%0.s#' \$(seq 1 \$filled)
    printf '%0.s-' \$(seq 1 \$empty)
    printf ']'
}

echo \"Worker perm=$PERM port=$PORT\"
echo \"Total runs: \$TOTAL\"

for DATASET in $COLLECTION_NAMES; do
for ((LIMIT=$LIMIT_START; LIMIT<=$LIMIT_END; LIMIT+=$LIMIT_STEP)); do

RUN_COUNT=\$((RUN_COUNT+1))

RUN_NAME=\"dataset_\${DATASET}_perm_${PERM}_limit_\${LIMIT}\"
LOG_DIR=\"$RUN_ROOT/\$RUN_NAME\"

mkdir -p \$LOG_DIR

clear
echo \"Worker perm=$PERM  port=$PORT\"
echo \"Run \$RUN_COUNT / \$TOTAL\"

progress_bar \$RUN_COUNT \$TOTAL
echo
echo \"Dataset: \$DATASET\"
echo \"Limit: \$LIMIT\"

SIM_LOG=\$LOG_DIR/simulator.log
PY_LOG=\$LOG_DIR/python.log

################################
# launch simulator
################################

coppeliasim -h -GzmqRemoteApi.rpcPort=$PORT \"$SCENE\" \
> \$SIM_LOG 2>&1 &

SIM_PID=\$!

sleep 5

################################
# run python policy executor
################################

python3 -u policy_executor.py \
-p $PORT \
-l \$LIMIT \
-i $PERM \
-d \$DATASET \
> \$PY_LOG 2>&1

STATUS=\$?

################################
# shutdown simulator
################################

kill \$SIM_PID 2>/dev/null
sleep 2
kill -9 \$SIM_PID 2>/dev/null

################################
# record manifest
################################

if [ \$STATUS -eq 0 ]; then
echo \"\$DATASET,$PERM,\$LIMIT,$PORT,success\" >> \"$MANIFEST\"
else
echo \"\$DATASET,$PERM,\$LIMIT,$PORT,fail\" >> \"$MANIFEST\"
fi

sleep 2

done
done

echo 'Worker finished.'

" C-m

done

############################################
# attach dashboard
############################################

tmux attach -t $SESSION