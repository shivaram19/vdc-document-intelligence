#!/bin/bash
# VDC Agent Mesh — Startup Script
# No APIs. Pure agent-driven document intelligence.
# 
# Usage:
#   ./start-agent-mesh.sh           # Start all services
#   ./start-agent-mesh.sh --stop    # Stop all services
#   ./start-agent-mesh.sh --status  # Check status

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
AGENTS_DIR="$PROJECT_ROOT/picocloth/agents"
SHARED_DIR="$PROJECT_ROOT/picocloth/shared/project/vdc"
LOG_DIR="$PROJECT_ROOT"

cd "$PROJECT_ROOT"

start_services() {
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║          🧠 MEDHA — Agent-Driven Document Intelligence       ║"
    echo "║                     No APIs. Pure Agents.                    ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo

    # Ensure shared memory directories exist
    mkdir -p "$SHARED_DIR"/{inbox,documents,embeddings,chunks,facts,contradictions,rfis,queries,tasks}
    
    # Stop any existing services
    pkill -f "agent_bridge.py" 2>/dev/null || true
    pkill -f "inbox_watcher.py" 2>/dev/null || true
    sleep 1

    # Start Agent Bridge (WebSocket + HTTP inbox)
    echo "[1/3] Starting Agent Bridge on ws://localhost:8765 ..."
    cd "$AGENTS_DIR"
    nohup python3 ../bridge/agent_bridge.py > "$LOG_DIR/agent_bridge.log" 2>&1 &
    BRIDGE_PID=$!
    sleep 3
    if curl -s http://localhost:8765/health > /dev/null; then
        echo "      ✅ Agent Bridge running (PID: $BRIDGE_PID)"
    else
        echo "      ❌ Agent Bridge failed to start. Check agent_bridge.log"
        exit 1
    fi

    # Start Inbox Watcher
    echo "[2/3] Starting Inbox Watcher ..."
    nohup python3 inbox_watcher.py --interval 3 > "$LOG_DIR/inbox_watcher.log" 2>&1 &
    WATCHER_PID=$!
    sleep 1
    echo "      ✅ Inbox Watcher running (PID: $WATCHER_PID)"

    # Ensure nginx is running
    echo "[3/3] Checking nginx ..."
    if sudo systemctl is-active --quiet nginx; then
        echo "      ✅ nginx is active"
    else
        echo "      🔄 Starting nginx ..."
        sudo systemctl start nginx
        echo "      ✅ nginx started"
    fi

    echo
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Dashboard:   http://localhost (or medha.trelolabs.com)"
    echo "  WebSocket:   ws://localhost/ws"
    echo "  Inbox:       $SHARED_DIR/inbox/"
    echo "  Health:      http://localhost/health"
    echo "═══════════════════════════════════════════════════════════════"
    echo
    echo "  Drop files into inbox/ and watch the agents process them."
    echo "  Open the dashboard to interact with the agent mesh."
    echo
}

stop_services() {
    echo "Stopping Medha Agent Mesh ..."
    pkill -f "agent_bridge.py" 2>/dev/null || true
    pkill -f "inbox_watcher.py" 2>/dev/null || true
    echo "  ✅ Agent Bridge stopped"
    echo "  ✅ Inbox Watcher stopped"
}

show_status() {
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                    Medha Agent Mesh Status                   ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo
    
    echo "--- Agent Bridge ---"
    if pgrep -f "agent_bridge.py" > /dev/null; then
        PID=$(pgrep -f "agent_bridge.py" | head -1)
        echo "  Status: ✅ Running (PID: $PID)"
        curl -s http://localhost:8765/health | python3 -m json.tool 2>/dev/null || echo "  Health: ❌ Not responding"
    else
        echo "  Status: ❌ Not running"
    fi
    
    echo
    echo "--- Inbox Watcher ---"
    if pgrep -f "inbox_watcher.py" > /dev/null; then
        PID=$(pgrep -f "inbox_watcher.py" | head -1)
        echo "  Status: ✅ Running (PID: $PID)"
    else
        echo "  Status: ❌ Not running"
    fi
    
    echo
    echo "--- nginx ---"
    if sudo systemctl is-active --quiet nginx; then
        echo "  Status: ✅ Active"
    else
        echo "  Status: ❌ Inactive"
    fi
    
    echo
    echo "--- Shared Memory ---"
    echo "  Projects:    $(ls "$SHARED_DIR/documents/"/*.json 2>/dev/null | wc -l) documents"
    echo "  Embeddings:  $(ls "$SHARED_DIR/embeddings/"/*.npy 2>/dev/null | wc -l) projects indexed"
    echo "  Inbox:       $(ls "$SHARED_DIR/inbox/"/*.txt "$SHARED_DIR/inbox/"/*.pdf "$SHARED_DIR/inbox/"/*.docx 2>/dev/null | wc -l) files pending"
    
    echo
    echo "--- Fleet Nodes (tmux) ---"
    for node in a b c d e f g h i j; do
        if tmux has-session -t "node-$node" 2>/dev/null; then
            echo "  node-$node: ✅ Online"
        else
            echo "  node-$node: ❌ Offline"
        fi
    done
}

case "${1:-}" in
    --stop)
        stop_services
        ;;
    --status)
        show_status
        ;;
    *)
        start_services
        ;;
esac
