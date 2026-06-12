#!/usr/bin/env bash
# VDC Document Intelligence - PicoCloth Deployment Script
# Deploys the Trayini.ai VDC app using Node-A (Curiosity Brain) and Node-B (Executor)
# with all 5 document characters and digital twins enabled.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VDC_DIR="$(dirname "$SCRIPT_DIR")"
PICOCLOTH_DIR="${PICOCLOTH_DIR:-/home/shivaramgoud/tinkering/tinkering-with-claws/picocloth}"
PICOCLAW_BINARY="${PICOCLAW_BINARY:-/tmp/picoclaw/picoclaw}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

log() { echo -e "${BLUE}[VDC-DEPLOY]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERR]${NC} $1"; }
info() { echo -e "${CYAN}[INFO]${NC} $1"; }
char() { echo -e "${MAGENTA}[CHAR]${NC} $1"; }

# ============================================
# STEP 0: Prerequisites
# ============================================
check_prerequisites() {
    log "Checking prerequisites..."

    if [ ! -f "$PICOCLAW_BINARY" ]; then
        error "PicoClaw binary not found at $PICOCLAW_BINARY"
        exit 1
    fi
    success "PicoClaw binary: $PICOCLAW_BINARY"

    if [ ! -d "$PICOCLOTH_DIR" ]; then
        error "PicoCloth directory not found at $PICOCLOTH_DIR"
        exit 1
    fi
    success "PicoCloth directory: $PICOCLOTH_DIR"

    if [ -z "${XAI_API_KEY:-}" ]; then
        warn "XAI_API_KEY not set. Nodes may fail to initialize LLM providers."
    else
        success "XAI_API_KEY is set"
    fi
}

# ============================================
# STEP 1: Stop existing fleet
# ============================================
stop_existing() {
    log "Stopping any existing PicoCloth fleet..."
    bash "$PICOCLOTH_DIR/scripts/launch-fleet.sh" stop 2>/dev/null || true

    # Kill any existing Flask / frontend servers
    pkill -f "python.*backend/app.py" 2>/dev/null || true
    pkill -f "http.server 8080" 2>/dev/null || true
    sleep 2
    success "Existing services stopped"
}

# ============================================
# STEP 2: Backup original configs
# ============================================
backup_configs() {
    log "Backing up original node configs..."
    mkdir -p "$SCRIPT_DIR/backups"

    for node in node-a node-b; do
        local orig="$PICOCLOTH_DIR/$node/config.json"
        local backup="$SCRIPT_DIR/backups/$node-config.json.orig"
        if [ -f "$orig" ] && [ ! -f "$backup" ]; then
            cp "$orig" "$backup"
            success "Backed up $node config"
        fi
    done
}

# ============================================
# STEP 3: Copy VDC configs
# ============================================
install_vdc_configs() {
    log "Installing VDC-specific node configs..."

    if [ -z "${XAI_API_KEY:-}" ]; then
        error "XAI_API_KEY is required to populate node configs."
        exit 1
    fi

    # Substitute placeholder with actual env var so keys never live in committed JSON.
    sed "s/__XAI_API_KEY__/${XAI_API_KEY}/g" "$SCRIPT_DIR/node-a-vdc-config.json" > "$PICOCLOTH_DIR/node-a/config.json"
    sed "s/__XAI_API_KEY__/${XAI_API_KEY}/g" "$SCRIPT_DIR/node-b-vdc-config.json" > "$PICOCLOTH_DIR/node-b/config.json"

    # Also copy to home dirs so picoclaw picks them up
    sed "s/__XAI_API_KEY__/${XAI_API_KEY}/g" "$SCRIPT_DIR/node-a-vdc-config.json" > "$PICOCLOTH_DIR/node-a/home/config.json"
    sed "s/__XAI_API_KEY__/${XAI_API_KEY}/g" "$SCRIPT_DIR/node-b-vdc-config.json" > "$PICOCLOTH_DIR/node-b/home/config.json"

    success "VDC configs installed for node-a and node-b"
}

# ============================================
# STEP 4: Initialize shared memory with VDC content
# ============================================
seed_shared_memory() {
    log "Initializing shared memory with VDC Document Intelligence content..."

    SHARED_DIR="$PICOCLOTH_DIR/shared"

    # Layer 1: Doctrine
    mkdir -p "$SHARED_DIR/doctrine/skills"
    mkdir -p "$SHARED_DIR/doctrine/schemas"
    mkdir -p "$SHARED_DIR/doctrine/policies"
    cp "$SCRIPT_DIR/doctrine/vdc-document-intelligence.md" "$SHARED_DIR/doctrine/skills/"

    # Layer 2: Project - Documents
    mkdir -p "$SHARED_DIR/project/documents"
    mkdir -p "$SHARED_DIR/project/facts"
    mkdir -p "$SHARED_DIR/project/decisions"
    mkdir -p "$SHARED_DIR/project/entities"

    # Copy ALL sample docs (characters)
    for doc in "$VDC_DIR/sample_docs"/*.txt; do
        if [ -f "$doc" ]; then
            cp "$doc" "$SHARED_DIR/project/documents/"
            char "Loaded character: $(basename "$doc")"
        fi
    done

    # Copy character entities
    cp "$SCRIPT_DIR/characters"/*.json "$SHARED_DIR/project/entities/"
    success "All 5 document characters loaded into shared memory"

    # Create VDC fleet state
    cat > "$SHARED_DIR/state/fleet-state.json" << 'EOF'
{
  "version": "1.0",
  "deployment": "vdc-document-intelligence",
  "last_updated": "2026-04-24T11:30:00Z",
  "orchestrator": "trelo-labs",
  "project": "DOWNTOWN OFFICE TOWER",
  "nodes": {
    "node-a": {
      "status": "initializing",
      "role": "document-curiosity-brain",
      "description": "Researches and queries construction documents",
      "last_heartbeat": null,
      "active_turns": 0,
      "active_subagents": 0,
      "daily_tokens_used": 0,
      "daily_cost_usd": 0.0,
      "characters_managed": ["A-101", "RFI-LOG"]
    },
    "node-b": {
      "status": "initializing",
      "role": "document-executor-builder",
      "description": "Executes backend, drafts RFIs, runs scans",
      "last_heartbeat": null,
      "active_turns": 0,
      "active_subagents": 0,
      "daily_tokens_used": 0,
      "daily_cost_usd": 0.0,
      "characters_managed": ["MECH-HVAC", "FPS-211313", "STRUCT-CIP"]
    }
  },
  "characters": {
    "arch-drawing-notes": { "name": "A-101", "status": "active", "digital_twin": true },
    "fire-protection-spec": { "name": "FPS-211313", "status": "active", "digital_twin": true },
    "mech-spec-hvac": { "name": "MECH-HVAC", "status": "active", "digital_twin": true },
    "rfi-log": { "name": "RFI-LOG", "status": "active", "digital_twin": true },
    "struct-spec": { "name": "STRUCT-CIP", "status": "active", "digital_twin": true }
  },
  "metrics": {
    "total_tasks_completed": 0,
    "total_digital_twins_created": 0,
    "total_compactions": 0,
    "documents_ingested": 5,
    "rfis_drafted": 0,
    "contradictions_found": 0
  }
}
EOF

    # Seed initial project facts
    cat > "$SHARED_DIR/project/facts/vdc-deployment.jsonl" << 'EOF'
{"type":"deployment","content":"VDC Document Intelligence deployed via PicoCloth 2-node fleet","confidence":1.0,"extracted_at":"2026-04-24T11:30:00Z"}
{"type":"document_character","content":"A-101 (Architectural Drawing Notes) - Design Visionary character loaded","confidence":1.0,"extracted_at":"2026-04-24T11:30:00Z"}
{"type":"document_character","content":"FPS-211313 (Fire Protection Spec) - Safety Guardian character loaded","confidence":1.0,"extracted_at":"2026-04-24T11:30:00Z"}
{"type":"document_character","content":"MECH-HVAC (Mechanical Spec) - Climate Controller character loaded","confidence":1.0,"extracted_at":"2026-04-24T11:30:00Z"}
{"type":"document_character","content":"RFI-LOG (Question Keeper) - Tracks all active contradictions","confidence":1.0,"extracted_at":"2026-04-24T11:30:00Z"}
{"type":"document_character","content":"STRUCT-CIP (Structural Spec) - Structure Engineer character loaded","confidence":1.0,"extracted_at":"2026-04-24T11:30:00Z"}
{"type":"contradiction","content":"RFI-001: Column spacing mismatch at C-4 - Structural 24'-0\" vs Architectural 25'-0\"","confidence":0.95,"extracted_at":"2026-04-24T11:30:00Z"}
{"type":"contradiction","content":"RFI-002: Mechanical room ceiling height 10 ft vs 12 ft minimum clear","confidence":0.95,"extracted_at":"2026-04-24T11:30:00Z"}
{"type":"contradiction","content":"RFI-003: Window U-factor 0.30 vs 0.28 code requirement","confidence":0.90,"extracted_at":"2026-04-24T11:30:00Z"}
{"type":"contradiction","content":"RFI-005: Lobby floor finish - polished concrete vs terrazzo","confidence":0.90,"extracted_at":"2026-04-24T11:30:00Z"}
EOF

    # Layer 3: State
    mkdir -p "$SHARED_DIR/state"
    echo '[]' > "$SHARED_DIR/state/task-queue.json"

    # Layer 4: Run
    mkdir -p "$SHARED_DIR/run"

    # Digital Twins Archive
    mkdir -p "$SHARED_DIR/digital-twins/node-a"
    mkdir -p "$SHARED_DIR/digital-twins/node-b"

    # Compaction Archive
    mkdir -p "$SHARED_DIR/compaction-archive/node-a"
    mkdir -p "$SHARED_DIR/compaction-archive/node-b"

    success "Shared memory initialized with VDC content and all 5 characters"
}

# ============================================
# STEP 5: Launch PicoCloth fleet
# ============================================
launch_fleet() {
    log "Launching PicoCloth fleet with VDC Document Intelligence..."

    export PICOCLAW_HOOK_TWIN_DIR=""
    export PICOCLAW_HOOK_PROJECT_DIR=""
    export PICOCLAW_HOOK_NODE_ID=""
    export PICOCLAW_HOOK_MAX_FACTS=""

    bash "$PICOCLOTH_DIR/scripts/launch-fleet.sh" start
}

# ============================================
# STEP 6: Start VDC Flask Backend
# ============================================
start_backend() {
    log "Starting VDC Document Intelligence backend..."

    cd "$VDC_DIR"
    source venv-docling/bin/activate 2>/dev/null || true

    nohup python3 backend/app.py > "$VDC_DIR/backend.log" 2>&1 &
    echo $! > "$VDC_DIR/backend.pid"

    success "Backend starting on http://localhost:5001 (PID: $(cat "$VDC_DIR/backend.pid"))"
    info "Logs: tail -f $VDC_DIR/backend.log"
}

# ============================================
# STEP 7: Seed backend with sample docs
# ============================================
seed_backend() {
    log "Seeding backend with sample documents..."
    cd "$VDC_DIR"
    source venv-docling/bin/activate 2>/dev/null || true

    sleep 3  # Give backend time to start
    python3 seed_demo.py >> "$VDC_DIR/backend.log" 2>&1 || warn "Seed script had issues (backend may still be starting)"
    success "Backend seeded with sample documents"
}

# ============================================
# STEP 8: Start Frontend
# ============================================
start_frontend() {
    log "Starting VDC frontend..."

    cd "$VDC_DIR/frontend"
    nohup python3 -m http.server 8080 > "$VDC_DIR/frontend.log" 2>&1 &
    echo $! > "$VDC_DIR/frontend.pid"

    success "Frontend starting on http://localhost:8080 (PID: $(cat "$VDC_DIR/frontend.pid"))"
}

# ============================================
# Dashboard
# ============================================
show_dashboard() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║           🏗️  VDC DOCUMENT INTELLIGENCE - PICO CLOTH DEPLOYMENT            ║"
    echo "╠══════════════════════════════════════════════════════════════════════════════╣"
    echo "║                                                                              ║"
    echo "║  📡 FLEET NODES                                                              ║"
    echo "║  ├─ Node-A (Curiosity Brain)  │  Gateway: http://127.0.0.1:18790           ║"
    echo "║  │   Role: Research & Query   │  Characters: A-101, RFI-LOG                 ║"
    echo "║  ├─ Node-B (Executor Builder) │  Gateway: http://127.0.0.1:18791           ║"
    echo "║  │   Role: Build & Execute   │  Characters: MECH-HVAC, FPS-211313, STRUCT  ║"
    echo "║  └─ MCP Fleet Server          │  stdio via config                          ║"
    echo "║                                                                              ║"
    echo "║  🎭 ALL CHARACTERS (DOCUMENT ENTITIES)                                       ║"
    echo "║  ├─ 🎨 A-101           │ Architectural Drawing Notes  │ Design Visionary    ║"
    echo "║  ├─ 🔥 FPS-211313      │ Fire Protection Spec         │ Safety Guardian     ║"
    echo "║  ├─ ❄️  MECH-HVAC      │ Mechanical HVAC Spec         │ Climate Controller  ║"
    echo "║  ├─ 📋 RFI-LOG         │ Request for Information Log  │ Question Keeper     ║"
    echo "║  └─ 🏛️  STRUCT-CIP     │ Structural Concrete Spec     │ Structure Engineer  ║"
    echo "║                                                                              ║"
    echo "║  🧠 DIGITAL TWINS                                                            ║"
    echo "║  ├─ Node-A twins:  shared/digital-twins/node-a/                              ║"
    echo "║  ├─ Node-B twins:  shared/digital-twins/node-b/                              ║"
    echo "║  └─ Pre-compaction hooks: ENABLED on both nodes                              ║"
    echo "║                                                                              ║"
    echo "║  🌐 APPLICATION                                                              ║"
    echo "║  ├─ Backend API:    http://localhost:5001                                    ║"
    echo "║  ├─ Frontend UI:    http://localhost:8080                                    ║"
    echo "║  └─ Sample Docs:    5 documents seeded                                       ║"
    echo "║                                                                              ║"
    echo "║  📊 OBSERVABILITY                                                            ║"
    echo "║  └─ Langfuse:       http://localhost:3000                                    ║"
    echo "║                                                                              ║"
    echo "║  📁 SHARED MEMORY                                                            ║"
    echo "║  └─ $PICOCLOTH_DIR/shared/                     ║"
    echo "║                                                                              ║"
    echo "╠══════════════════════════════════════════════════════════════════════════════╣"
    echo "║  COMMANDS:                                                                   ║"
    echo "║    tail -f $PICOCLOTH_DIR/node-a/node.log        # Node-A logs               ║"
    echo "║    tail -f $PICOCLOTH_DIR/node-b/node.log        # Node-B logs               ║"
    echo "║    tail -f $VDC_DIR/backend.log                  # Backend logs              ║"
    echo "║    bash $SCRIPT_DIR/stop.sh                      # Stop everything           ║"
    echo "║                                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo ""
}

# ============================================
# Main
# ============================================
main() {
    echo "🏗️  VDC Document Intelligence - PicoCloth Deployment"
    echo "======================================================"

    check_prerequisites
    stop_existing
    backup_configs
    install_vdc_configs
    seed_shared_memory
    launch_fleet
    start_backend
    seed_backend
    start_frontend

    sleep 2
    show_dashboard

    log "Deployment complete! All 5 characters loaded. Digital twins enabled."
}

main "$@"
