#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
打包腳本

這個腳本用於將背景網頁開啟工具打包成可執行檔，以便在其他電腦上使用。
使用PyInstaller進行打包。
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_requirements():
    """檢查是否已安裝PyInstaller"""
    try:
        import PyInstaller
        print("✓ PyInstaller已安裝")
        return True
    except ImportError:
        print("× PyInstaller未安裝，正在安裝...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller安裝成功")
            return True
        except subprocess.CalledProcessError:
            print("× PyInstaller安裝失敗，請手動安裝：pip install pyinstaller")
            return False


def build_executable():
    """打包成可執行檔"""
    print("\n開始打包程式...")
    
    # 創建dist和build資料夾（如果不存在）
    os.makedirs("dist", exist_ok=True)
    os.makedirs("build", exist_ok=True)
    
    # 清理舊的打包文件
    for item in os.listdir("dist"):
        path = os.path.join("dist", item)
        if os.path.isfile(path):
            os.unlink(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    
    # 執行PyInstaller
    cmd = [
        sys.executable, 
        "-m", 
        "PyInstaller",
        "--name=BackgroundWebOpener",  # 使用英文檔名
        "--onefile",
        "--windowed",
        "--clean",
        "background_web.py"
    ]
    
    # 刪除中文spec檔案（如果存在）
    chinese_spec = "背景網頁開啟工具.spec"
    if os.path.exists(chinese_spec):
        try:
            os.remove(chinese_spec)
            print(f"已刪除舊的中文spec檔案: {chinese_spec}")
        except Exception as e:
            print(f"無法刪除中文spec檔案: {e}")
    
    try:
        subprocess.check_call(cmd)
        print("\n✓ 打包成功！")
        
        # 獲取可執行檔路徑
        exe_path = os.path.join("dist", "BackgroundWebOpener.exe")
        abs_path = os.path.abspath(exe_path)
        
        print(f"\n可執行檔位置: {abs_path}")
        print("\n您可以將dist資料夾中的可執行檔複製到其他電腦使用。")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n× 打包失敗: {e}")
        return False


def main():
    """主函數"""
    print("===== Background Web Opener 打包程式 =====\n")
    
    # 檢查當前目錄是否有background_web.py
    if not os.path.exists("background_web.py"):
        print("× 錯誤: 找不到background_web.py文件，請確保您在正確的目錄中執行此腳本。")
        return False
    
    # 檢查PyInstaller
    if not check_requirements():
        return False
    
    # 打包程式
    return build_executable()


if __name__ == "__main__":
    success = main()
    
    # 等待用戶按下任意鍵退出
    input("\n按下Enter鍵退出...")
    sys.exit(0 if success else 1)