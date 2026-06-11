#!/usr/bin/env python3
"""
Auto Fixer for Nexcorix Claw - Merapikan struktur folder modules/
Jalankan sekali: python3 fixer.py
"""

import os
import shutil
import re

def fix_structure():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    modules_dir = os.path.join(base_dir, "modules")
    
    print("🔧 Memperbaiki struktur folder...")
    
    # 1. Pastikan folder modules/ ada
    os.makedirs(modules_dir, exist_ok=True)
    
    # 2. Pindahkan semua file .py dari SUBFOLDER APAPUN ke modules/
    py_files = []
    for root, dirs, files in os.walk(modules_dir):
        if root == modules_dir:
            continue
        for f in files:
            if f.endswith(".py"):
                src = os.path.join(root, f)
                dst = os.path.join(modules_dir, f)
                py_files.append((src, dst))
    
    for src, dst in py_files:
        try:
            shutil.move(src, dst)
            print(f"   📦 Pindah: {os.path.relpath(src, base_dir)} -> {os.path.relpath(dst, base_dir)}")
        except Exception as e:
            print(f"   ❌ Gagal pindah {src}: {e}")
    
    # 3. Hapus semua folder kosong (termasuk bersarang)
    for root, dirs, files in os.walk(modules_dir, topdown=False):
        if root == modules_dir:
            continue
        try:
            os.rmdir(root)
            print(f"   🗑️  Hapus folder kosong: {os.path.relpath(root, base_dir)}")
        except OSError:
            pass  # tidak kosong atau error
    
    # 4. Hapus folder module/ di root jika ada
    module_root = os.path.join(base_dir, "module")
    if os.path.exists(module_root):
        shutil.rmtree(module_root, ignore_errors=True)
        print("   🗑️  Hapus folder 'module/' di root")
    
    # 5. Rename file yang typo / ada spasi
    rename_map = {
        "Observability. py": "observability.py",
        "voice. py": "voice.py",
        "webui. py": "webui.py",
        "rag. py": "rag.py",
        "mcp_.py": "mcp_client.py",
        "_init_.py": "__init__.py",
        "mcp_client.py": "mcp_client.py",
        "skill_marketplace.py": "skill_marketplace.py",
        "multi_agent.py": "multi_agent.py",
        "memory_advanced.py": "memory_advanced.py",
        "memory_compactor.py": "memory_compactor.py",
        "knowledge_graph.py": "knowledge_graph.py"
    }
    for old, new in rename_map.items():
        old_path = os.path.join(modules_dir, old)
        new_path = os.path.join(modules_dir, new)
        if os.path.exists(old_path) and old != new:
            try:
                os.rename(old_path, new_path)
                print(f"   ✏️  Rename: {old} -> {new}")
            except:
                pass
    
    # 6. Buat __init__.py jika belum ada
    init_file = os.path.join(modules_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# Nexcorix Claw modules\n\n")
        print("   📄 Buat __init__.py")
    
    # 7. Pastikan tool_registry.py, memory_store.py, skill_manager.py, workspace.py ada (buat minimal jika tidak ada)
    core_files = ["tool_registry.py", "memory_store.py", "skill_manager.py", "workspace.py"]
    for cf in core_files:
        cf_path = os.path.join(modules_dir, cf)
        if not os.path.exists(cf_path):
            with open(cf_path, "w") as f:
                f.write("# Auto-generated stub for " + cf + "\n\n")
            print(f"   ⚠️  Buat file kosong: {cf}")
    
    print("✅ Perbaikan selesai!")
    print("Struktur modules/ sekarang rapi. Anda bisa menjalankan nexcorix_claw.py")

if __name__ == "__main__":
    fix_structure()
