#!/usr/bin/env bash
# VDC Document Intelligence - PicoCloth Stop & Restore Script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VDC_DIR="$(dirname "$SCRIPT_DIR")"
PICOCLOTH_DIR="${PICOCLOTH_DIR:-/home/shivaramgoud/tinkering/tinkering-with-claws/picocloth}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[VDC-STOP]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERR]${NC} $1"; }

stop_fleet() {
    log "Stopping PicoCloth fleet..."
    bash "$PICOCLOTH_DIR/scripts/launch-fleet.sh" stop 2>/dev/null || true
    success "Fleet stopped"
}

stop_backend() {
    log "Stopping VDC backend..."
    if [ -f "$VDC_DIR/backend.pid" ]; then
        kill "$(cat "$VDC_DIR/backend.pid")" 2>/dev/null || true
        rm -f "$VDC_DIR/backend.pid"
    fi
    pkill -f "python.*backend/app.py" 2>/dev/null || true
    success "Backend stopped"
}

stop_frontend() {
    log "Stopping VDC frontend..."
    if [ -f "$VDC_DIR/frontend.pid" ]; then
        kill "$(cat "$VDC_DIR/frontend.pid")" 2>/dev/null || true
        rm -f "$VDC_DIR/frontend.pid"
    fi
    pkill -f "http.server 8080" 2>/dev/null || true
    success "Frontend stopped"
}

restore_configs() {
    log "Restoring original PicoCloth node configs..."
    for node in node-a node-b; do
        local backup="$SCRIPT_DIR/backups/$node-config.json.orig"
        local target="$PICOCLOTH_DIR/$node/config.json"
        local home_target="$PICOCLOTH_DIR/$node/home/config.json"
        if [ -f "$backup" ]; then
            cp "$backup" "$target"
            cp "$backup" "$home_target"
            success "Restored $node config from backup"
        else
            warn "No backup found for $node"
        fi
    done
}

cleanup_shared_memory() {
    log "Cleaning up VDC-specific shared memory content..."
    rm -f "$PICOCLOTH_DIR/shared/doctrine/skills/vdc-document-intelligence.md"
    rm -rf "$PICOCLOTH_DIR/shared/project/documents"
    rm -f "$PICOCLOTH_DIR/shared/project/entities/arch-drawing-notes.json"
    rm -f "$PICOCLOTH_DIR/shared/project/entities/fire-protection-spec.json"
    rm -f "$PICOCLOTH_DIR/shared/project/entities/mech-spec-hvac.json"
    rm -f "$PICOCLOTH_DIR/shared/project/entities/rfi-log.json"
    rm -f "$PICOCLOTH_DIR/shared/project/entities/struct-spec.json"
    rm -f "$PICOCLOTH_DIR/shared/project/facts/vdc-deployment.jsonl"
    success "VDC shared memory cleaned up"
}

show_help() {
    echo "VDC Document Intelligence - Stop Script"
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --restore     Restore original PicoCloth configs (default: just stop)"
    echo "  --cleanup     Remove VDC content from shared memory"
    echo "  --full        Stop + restore + cleanup (full reset)"
    echo "  --help        Show this help"
}

main() {
    local restore=false
    local cleanup=false

    for arg in "$@"; do
        case "$arg" in
            --restore) restore=true ;;
            --cleanup) cleanup=true ;;
            --full) restore=true; cleanup=true ;;
            --help) show_help; exit 0 ;;
        esac
    done

    echo "🛑 Stopping VDC Document Intelligence deployment..."
    echo "====================================================="

    stop_frontend
    stop_backend
    stop_fleet

    if [ "$restore" = true ]; then
        restore_configs
    fi

    if [ "$cleanup" = true ]; then
        cleanup_shared_memory
    fi

    echo ""
    success "VDC deployment stopped."
    if [ "$restore" = true ]; then
        info "Original PicoCloth configs restored."
    fi
    if [ "$cleanup" = true ]; then
        info "Shared memory cleaned."
    fi
}

main "$@"
