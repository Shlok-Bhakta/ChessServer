# frontend
tmux new-window -n "frontend"
tmux send-keys "nix develop" C-m
tmux send-keys "cd chess-frontend" C-m
tmux send-keys "npm install" C-m
tmux send-keys "npm run dev" C-m


tmux new-window -n "backend"
tmux send-keys "nix develop" C-m
tmux send-keys "cd chess-backend" C-m
tmux send-keys "flask run --debug" C-m
