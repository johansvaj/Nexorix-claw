#!/usr/bin/env bash
# Nexcorix Claw - Universal Launcher v6.0 with Notifications

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Nexcorix Claw Universal Launcher v6.0   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"

# ---------- 1. Deteksi Python ----------
detect_python() {
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}[ERROR] Python tidak ditemukan. Install Python 3.8+.${NC}"
        exit 1
    fi
    
    PY_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
    PY_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')
    
    if [ "$PY_MAJOR" -lt 3 ] || ( [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ] ); then
        echo -e "${RED}[ERROR] Python $PY_MAJOR.$PY_MINOR < 3.8. Upgrade Python.${NC}"
        exit 1
    fi
    echo -e "${GREEN}[✓] Python $PY_MAJOR.$PY_MINOR ($PYTHON_CMD)${NC}"
}

# ---------- 2. Setup Virtual Environment ----------
setup_venv() {
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}[i] Membuat virtual environment...${NC}"
        $PYTHON_CMD -m venv venv
        echo -e "${GREEN}[✓] Virtual environment dibuat.${NC}"
    fi
    # Aktivasi
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    echo -e "${GREEN}[✓] Virtual environment aktif (venv)${NC}"
    PYTHON_CMD="python"
}

# ---------- 3. Install library dengan notifikasi ----------
install_with_notify() {
    local lib=$1
    echo -e "${YELLOW}[⏳] Menginstall $lib...${NC}"
    if $PYTHON_CMD -m pip install "$lib" --quiet; then
        echo -e "${GREEN}[✅] $lib berhasil diinstall.${NC}"
        return 0
    else
        echo -e "${RED}[❌] $lib gagal diinstall.${NC}"
        return 1
    fi
}

install_libs() {
    echo -e "${YELLOW}[i] Upgrade pip...${NC}"
    $PYTHON_CMD -m pip install --upgrade pip > /dev/null 2>&1
    echo -e "${GREEN}[✓] pip upgrade selesai.${NC}"

    # Minimal libraries
    MINIMAL=("requests" "urllib3")
    for lib in "${MINIMAL[@]}"; do
        install_with_notify "$lib"
    done

    echo ""
    echo -e "${YELLOW}Install library advanced untuk fitur penuh? (chromadb, fastapi, dll) [y/N]:${NC}"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        ADVANCED=(
            "chromadb"
            "sentence-transformers"
            "fastapi"
            "uvicorn"
            "python-telegram-bot"
            "discord.py"
            "schedule"
            "pyyaml"
            "sqlite-utils"
        )
        for lib in "${ADVANCED[@]}"; do
            install_with_notify "$lib"
        done
        echo -e "${GREEN}[✓] Semua library advanced telah diproses.${NC}"
    else
        echo -e "${GREEN}[i] Lewati install library advanced.${NC}"
    fi
}

# ---------- 4. Jalankan program ----------
run_claw() {
    if [ ! -f "nexcorix_claw.py" ]; then
        echo -e "${RED}[ERROR] File nexcorix_claw.py tidak ditemukan.${NC}"
        exit 1
    fi
    echo -e "${GREEN}[✓] Menjalankan Nexcorix Claw...${NC}"
    $PYTHON_CMD nexcorix_claw.py
}

# ---------- Main ----------
detect_python
setup_venv
install_libs
run_claw
