#!/usr/bin/env bash
# Nexcorix Claw - Smart Installer v9.0 (Skip installed libraries)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Nexcorix Claw Smart Installer v9.0      ║${NC}"
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
        echo -e "${RED}[ERROR] Python $PY_MAJOR.$PY_MINOR < 3.8.${NC}"
        exit 1
    fi
    echo -e "${GREEN}[✓] Python $PY_MAJOR.$PY_MINOR ($PYTHON_CMD)${NC}"
}

# ---------- 2. Virtual Environment ----------
setup_venv() {
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}[i] Membuat virtual environment...${NC}"
        $PYTHON_CMD -m venv venv
    fi
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    echo -e "${GREEN}[✓] Virtual environment aktif${NC}"
    PYTHON_CMD="python"
}

# ---------- 3. Fungsi Cek & Install ----------
is_installed() {
    $PYTHON_CMD -c "import $1" 2>/dev/null && return 0 || return 1
}

install_if_missing() {
    local import_name=$1
    local pkg_name=${2:-$import_name}
    if is_installed "$import_name"; then
        echo -e "${GREEN}[✓] $import_name sudah terinstall, lewati.${NC}"
    else
        echo -e "${YELLOW}[i] Menginstall $pkg_name...${NC}"
        $PYTHON_CMD -m pip install "$pkg_name"
    fi
}

# ---------- 4. Pilih Mode ----------
choose_mode() {
    echo ""
    echo -e "${YELLOW}Pilih mode instalasi (library yang sudah ada akan dilewati):${NC}"
    echo "  1) Minimal (<2 MB)    - hanya requests, urllib3"
    echo "  2) Medium (~50 MB)    - + chromadb, onnxruntime (memori cerdas dengan ONNX)"
    echo "  3) Full (~300 MB)     - semua library + WebUI, Telegram, Discord, dll. (sentence-transformers ditanya)"
    echo "  4) Custom             - pilih sendiri library berat yang ingin diinstall"
    echo -n "Masukkan pilihan [1/2/3/4]: "
    read -r mode
    case $mode in
        1) INSTALL_MODE="minimal" ;;
        2) INSTALL_MODE="medium" ;;
        3) INSTALL_MODE="full" ;;
        4) INSTALL_MODE="custom" ;;
        *) echo -e "${RED}Pilihan tidak valid, menggunakan minimal.${NC}"; INSTALL_MODE="minimal" ;;
    esac
}

# ---------- 5. Install Berdasarkan Mode ----------
install_libs() {
    echo -e "${YELLOW}[i] Upgrade pip...${NC}"
    $PYTHON_CMD -m pip install --upgrade pip > /dev/null 2>&1

    # Minimal (wajib)
    echo -e "${YELLOW}[i] Memeriksa library minimal...${NC}"
    install_if_missing "requests"
    install_if_missing "urllib3"

    if [ "$INSTALL_MODE" = "medium" ] || [ "$INSTALL_MODE" = "full" ]; then
        echo -e "${YELLOW}[i] Memeriksa library medium...${NC}"
        install_if_missing "chromadb"
        install_if_missing "onnxruntime"
        # Pre-download model ONNX (sekitar 30 MB) agar tidak mengganggu saat runtime
        if ! $PYTHON_CMD -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()" 2>/dev/null; then
            echo -e "${YELLOW}[i] Mengunduh model ONNX MiniLM-L6-v2 (sekitar 30 MB)...${NC}"
            $PYTHON_CMD -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()"
        else
            echo -e "${GREEN}[✓] Model ONNX sudah tersedia.${NC}"
        fi
    fi

    if [ "$INSTALL_MODE" = "full" ]; then
        echo -e "${YELLOW}[i] Memeriksa library full...${NC}"
        install_if_missing "fastapi"
        install_if_missing "uvicorn"
        install_if_missing "telegram" "python-telegram-bot"
        install_if_missing "discord" "discord.py"
        install_if_missing "schedule"
        install_if_missing "yaml" "pyyaml"

        # Sentence-transformers (berat, tanya)
        echo -e "${YELLOW}Install sentence-transformers ( ~80 MB + PyTorch ~1GB )? [y/N]:${NC}"
        read -r ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            install_if_missing "sentence_transformers" "sentence-transformers"
        else
            echo -e "${GREEN}[i] Lewati sentence-transformers (fallback ke ONNX).${NC}"
        fi
    fi

    if [ "$INSTALL_MODE" = "custom" ]; then
        echo -e "${YELLOW}Pilih library berat yang ingin diinstall (pisah dengan spasi):${NC}"
        echo "  chromadb onnxruntime fastapi uvicorn python-telegram-bot discord.py schedule pyyaml sentence-transformers"
        read -r -a custom_libs
        for lib in "${custom_libs[@]}"; do
            case $lib in
                chromadb) install_if_missing "chromadb" ;;
                onnxruntime) install_if_missing "onnxruntime" ;;
                fastapi) install_if_missing "fastapi" ;;
                uvicorn) install_if_missing "uvicorn" ;;
                python-telegram-bot) install_if_missing "telegram" "python-telegram-bot" ;;
                discord.py) install_if_missing "discord" "discord.py" ;;
                schedule) install_if_missing "schedule" ;;
                pyyaml) install_if_missing "yaml" "pyyaml" ;;
                sentence-transformers)
                    echo -e "${YELLOW}Install sentence-transformers ( ~80 MB + PyTorch ~1GB )? [y/N]:${NC}"
                    read -r ans
                    if [[ "$ans" =~ ^[Yy]$ ]]; then
                        install_if_missing "sentence_transformers" "sentence-transformers"
                    fi
                    ;;
                *) echo -e "${RED}Library $lib tidak dikenal.${NC}" ;;
            esac
        done
    fi

    echo -e "${GREEN}[✓] Instalasi selesai.${NC}"
}

# ---------- 6. Jalankan Program ----------
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
choose_mode
install_libs
run_claw
