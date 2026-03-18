#!/bin/bash

SESSION="policy_runs"
BASE_PORT=23000

tmux kill-session -t $SESSION 2>/dev/null

tmux new-session -d -s $SESSION

# create 6 panes
tmux split-window -h
tmux split-window -v
tmux select-pane -t 0
tmux split-window -v
tmux select-pane -t 2
tmux split-window -v
tmux select-pane -t 4
tmux split-window -v

tmux select-layout tiled

for PERM in {0..5}; do

PORT=$((BASE_PORT + PERM))

tmux send-keys -t $PERM "
cd $(pwd)
./worker.sh $PERM $PORT
" C-m

done

tmux attach -t $SESSION