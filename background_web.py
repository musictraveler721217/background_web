#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
背景網頁開啟工具

這個程式允許使用者在背景同時開啟多個網頁，特別適合用於同時登入並播放多個課程影片。
主要功能：
1. 背景開啟多個網頁同時登入播放課程影片，不受干擾（類似無痕視窗）
2. 防止網頁因閒置時間而被登出，透過模擬真實使用者行為
3. 使用原本Cookie或模擬Chrome瀏覽器，避免被偵測為非正常瀏覽器
4. 提供多種瀏覽器設定選項，增強使用體驗
5. 可以封裝成可執行檔在其他電腦使用
"""

import sys
import os
import time
import json
import random
import threading
import platform
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QListWidget, QListWidgetItem, QMessageBox, 
                             QCheckBox, QSpinBox, QGroupBox, QFormLayout,
                             QComboBox, QStatusBar, QMenu, QAction, QTabWidget,
                             QRadioButton, QButtonGroup, QFileDialog, QToolTip)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings, QTimer, QSize
from PyQt5.QtGui import QIcon, QCursor, QFont, QPixmap
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# 設定日誌
log_dir = os.path.join(os.path.expanduser("~"), "background_web_data", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"background_web_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)


class BrowserThread(QThread):
    """瀏覽器執行緒，負責在背景開啟和維護瀏覽器"""
    
    # 定義信號用於更新UI
    status_update = pyqtSignal(str, str)  # (browser_id, status_message)
    browser_closed = pyqtSignal(str)  # browser_id
    
    def __init__(self, browser_id, url, keep_alive_interval=60, incognito_mode=True, 
                 disable_images=False, proxy_server="", custom_user_agent="", 
                 advanced_stealth=True, parent=None):
        """初始化瀏覽器執行緒
        
        Args:
            browser_id (str): 瀏覽器ID，用於識別不同的瀏覽器實例
            url (str): 要開啟的網址
            keep_alive_interval (int): 防止閒置登出的操作間隔（秒）
            incognito_mode (bool): 是否使用無痕模式
            disable_images (bool): 是否禁用圖片載入以提高效能
            proxy_server (str): 代理伺服器設定 (格式: "ip:port")
            custom_user_agent (str): 自訂使用者代理字串
            advanced_stealth (bool): 是否啟用進階防偵測功能
            parent: 父物件
        """
        super().__init__(parent)
        self.browser_id = browser_id
        self.url = url
        self.keep_alive_interval = keep_alive_interval
        self.incognito_mode = incognito_mode
        self.disable_images = disable_images
        self.proxy_server = proxy_server
        self.custom_user_agent = custom_user_agent
        self.advanced_stealth = advanced_stealth
        self.driver = None
        self.is_running = False
        self.user_data_dir = os.path.join(os.path.expanduser("~"), "background_web_data", browser_id)
        self.logger = logging.getLogger(f"Browser_{browser_id}")
        
        # 隨機活動設定（已移除右鍵相關功能）
        self.activity_types = [
            "scroll",          # 滾動頁面
            "mouse_move",      # 移動滑鼠
            "click_safe",      # 安全點擊（避開按鈕和連結）
            "key_press",       # 按鍵盤
            "mouse_event",     # 觸發滑鼠事件（已移除右鍵功能）
            "touch_simulation", # 模擬觸控
            "tab_switch",      # 切換分頁
            "text_selection"   # 選取文字
        ]
        

    
    def run(self):
        """執行緒主函數，開啟瀏覽器並保持活動狀態"""
        self.is_running = True
        self.status_update.emit(self.browser_id, "正在啟動瀏覽器...")
        self.logger.info(f"啟動瀏覽器，網址: {self.url}")
        
        try:
            # 設定Chrome選項
            chrome_options = Options()
            
            # 基本設定
            if not self.incognito_mode:
                chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")
            else:
                chrome_options.add_argument("--incognito")
                
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 避免被偵測為自動化工具
            
            # 效能優化選項
            if self.disable_images:
                chrome_options.add_argument("--disable-images")
                
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-notifications")
            
            # 代理伺服器設定
            if self.proxy_server:
                chrome_options.add_argument(f"--proxy-server={self.proxy_server}")
            
            # 設定使用者代理字串，模擬正常Chrome瀏覽器
            if self.custom_user_agent:
                chrome_options.add_argument(f"--user-agent={self.custom_user_agent}")
            else:
                # 更新的使用者代理字串列表，包含最新的Chrome版本
                user_agents = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
                ]
                chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            # 添加實驗性選項，進一步避免被偵測為自動化工具
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            
            # 啟動瀏覽器
            try:
                self.status_update.emit(self.browser_id, "正在啟動Chrome瀏覽器...")
                
                # 添加額外的選項以繞過版本檢查
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--ignore-certificate-errors")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
                
                # 直接使用selenium內建的驅動程式管理器
                self.logger.info("使用selenium內建驅動程式管理器啟動Chrome瀏覽器")
                self.driver = webdriver.Chrome(options=chrome_options)
                self.logger.info("Chrome瀏覽器啟動成功")
            except Exception as e:
                self.logger.error(f"Chrome瀏覽器啟動失敗: {str(e)}")
                self.status_update.emit(self.browser_id, f"Chrome瀏覽器啟動失敗: {str(e)}")
                raise Exception(f"無法啟動瀏覽器: {str(e)}")
            
            # 進階防偵測設定
            if self.advanced_stealth:
                # 修改 navigator.webdriver 屬性
                self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                        
                        // 覆蓋 Permissions API
                        if (navigator.permissions) {
                            const originalQuery = navigator.permissions.query;
                            navigator.permissions.query = (parameters) => (
                                parameters.name === 'notifications' ?
                                Promise.resolve({ state: Notification.permission }) :
                                originalQuery(parameters)
                            );
                        }
                        
                        // 覆蓋 Plugins API
                        Object.defineProperty(navigator, 'plugins', {
                            get: () => {
                                const plugins = [];
                                for (let i = 0; i < 5; i++) {
                                    plugins.push({
                                        name: `Plugin ${i}`,
                                        description: `Plugin description ${i}`,
                                        filename: `plugin_${i}.dll`
                                    });
                                }
                                return plugins;
                            }
                        });
                        
                        // 覆蓋 Languages API
                        Object.defineProperty(navigator, 'languages', {
                            get: () => ['zh-TW', 'zh', 'en-US', 'en']
                        });
                    """
                })
                
                # 設定視窗大小為常見的螢幕解析度
                common_resolutions = [
                    (1366, 768),  # 最常見的筆電解析度
                    (1920, 1080), # 全高清
                    (1440, 900),  # MacBook
                    (1536, 864),  # 常見的Windows解析度
                    (1280, 720)   # HD
                ]
                width, height = random.choice(common_resolutions)
                self.driver.set_window_size(width, height)
            
            # 開啟網頁
            try:
                self.status_update.emit(self.browser_id, "正在開啟網頁...")
                self.driver.get(self.url)
                self.logger.info(f"瀏覽器已開啟，視窗大小: {self.driver.get_window_size()}")
                self.status_update.emit(self.browser_id, "瀏覽器已開啟")
            except WebDriverException as e:
                self.logger.error(f"開啟網頁失敗: {str(e)}")
                self.status_update.emit(self.browser_id, f"開啟網頁失敗: {str(e)}")
                raise Exception(f"無法開啟網頁: {str(e)}")
            except Exception as e:
                self.logger.error(f"未知錯誤: {str(e)}")
                self.status_update.emit(self.browser_id, f"未知錯誤: {str(e)}")
                raise
            
            # 保持瀏覽器活動狀態的迴圈
            activity_count = 0
            last_activity_type = None
            while self.is_running:
                try:
                    # 執行一些隨機操作來防止閒置登出
                    if self.driver.current_url != "about:blank":
                        activity_count += 1
                        
                        # 選擇一個不同於上次的活動類型
                        available_activities = [a for a in self.activity_types if a != last_activity_type]
                        activity_type = random.choice(available_activities)
                        last_activity_type = activity_type
                        
                        self.logger.debug(f"執行活動: {activity_type}")
                        
                        if activity_type == "scroll":
                            # 滾動頁面，模擬閱讀行為
                            scroll_amount = random.randint(100, 300)
                            scroll_direction = random.choice([1, -1])  # 1: 向下, -1: 向上
                            scroll_steps = random.randint(3, 8)  # 分多次滾動，更自然
                            
                            for step in range(scroll_steps):
                                step_amount = scroll_amount // scroll_steps * scroll_direction
                                self.driver.execute_script(f"window.scrollBy(0, {step_amount});")
                                time.sleep(random.uniform(0.1, 0.3))
                            
                            # 有時候會滾回一點，模擬找尋特定內容
                            if random.random() < 0.3:  # 30%的機率
                                time.sleep(random.uniform(0.5, 1.5))
                                self.driver.execute_script(f"window.scrollBy(0, {-scroll_direction * random.randint(50, 150)});")
                        
                        elif activity_type == "mouse_move":
                            # 移動滑鼠，模擬瀏覽頁面元素
                            actions = ActionChains(self.driver)
                            
                            # 嘗試找到頁面上的一些元素並移動到它們上面
                            try:
                                # 常見的頁面元素
                                elements = self.driver.find_elements(By.CSS_SELECTOR, 
                                    "p, h1, h2, h3, h4, h5, img, div[class], span[class]")
                                
                                if elements and len(elements) > 0:
                                    # 隨機選擇1-3個元素進行互動
                                    for _ in range(random.randint(1, 3)):
                                        element = random.choice(elements)
                                        try:
                                            actions.move_to_element(element)
                                            actions.pause(random.uniform(0.2, 0.8))
                                            actions.perform()
                                            time.sleep(random.uniform(0.3, 1.0))
                                        except:
                                            pass
                                else:
                                    # 如果找不到元素，就隨機移動
                                    for _ in range(random.randint(2, 5)):
                                        actions.move_by_offset(random.randint(-100, 100), random.randint(-100, 100))
                                        actions.pause(random.uniform(0.1, 0.5))
                                    actions.perform()
                            except Exception:
                                # 隨機移動滑鼠
                                actions.move_by_offset(random.randint(-100, 100), random.randint(-100, 100))
                                actions.perform()
                        
                        elif activity_type == "click_safe":
                            # 安全點擊（避開按鈕、連結和表單元素）
                            try:
                                # 找到頁面上的安全元素（段落、標題、圖片等非互動元素）
                                safe_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                                    "p, h1, h2, h3, h4, h5, div:not(button):not(a):not(input):not(select):not(textarea)")
                                
                                if safe_elements and len(safe_elements) > 0:
                                    # 隨機選擇一個安全元素
                                    safe_element = random.choice(safe_elements)
                                    
                                    # 檢查元素是否可見且可點擊
                                    if safe_element.is_displayed():
                                        actions = ActionChains(self.driver)
                                        actions.move_to_element(safe_element)
                                        actions.pause(random.uniform(0.2, 0.5))
                                        actions.click()
                                        actions.perform()
                                else:
                                    # 如果找不到安全元素，就點擊頁面上的隨機位置
                                    body = self.driver.find_element(By.TAG_NAME, "body")
                                    actions = ActionChains(self.driver)
                                    actions.move_to_element_with_offset(body, random.randint(100, 500), random.randint(100, 500))
                                    actions.pause(random.uniform(0.2, 0.5))
                                    actions.click()
                                    actions.perform()
                            except Exception:
                                pass
                        
                        elif activity_type == "key_press":
                            # 模擬按鍵盤
                            try:
                                # 找到可以接收鍵盤輸入的元素
                                body = self.driver.find_element(By.TAG_NAME, "body")
                                actions = ActionChains(self.driver)
                                actions.move_to_element(body)
                                
                                # 模擬按下方向鍵或Page Up/Down
                                keys = [Keys.PAGE_DOWN, Keys.PAGE_UP, Keys.DOWN, Keys.UP, Keys.RIGHT, Keys.LEFT]
                                actions.send_keys(random.choice(keys))
                                actions.perform()
                            except Exception:
                                pass
                        
                        elif activity_type == "mouse_event":
                            # 觸發滑鼠事件
                            try:
                                body = self.driver.find_element(By.TAG_NAME, "body")
                                actions = ActionChains(self.driver)
                                actions.move_to_element(body)
                                actions.pause(random.uniform(0.1, 0.3))
                                
                                # 隨機選擇滑鼠事件：懸停、雙擊（已移除右鍵功能）
                                event_type = random.choice(["hover", "double_click"])
                                if event_type == "hover":
                                    actions.move_by_offset(random.randint(-50, 50), random.randint(-50, 50))
                                elif event_type == "double_click":
                                    actions.double_click()
                                
                                actions.perform()
                            except Exception:
                                pass
                        
                        elif activity_type == "touch_simulation":
                            # 模擬觸控操作
                            try:
                                # 使用JavaScript模擬觸控事件
                                x = random.randint(100, 500)
                                y = random.randint(100, 500)
                                self.driver.execute_script(f"""
                                    var touchObj = new Touch({{
                                        identifier: Date.now(),
                                        target: document.elementFromPoint({x}, {y}),
                                        clientX: {x},
                                        clientY: {y},
                                        pageX: {x},
                                        pageY: {y},
                                        radiusX: 2.5,
                                        radiusY: 2.5,
                                        rotationAngle: 10,
                                        force: 0.5
                                    }});
                                    
                                    var touchEvent = new TouchEvent('touchstart', {{
                                        cancelable: true,
                                        bubbles: true,
                                        touches: [touchObj],
                                        targetTouches: [touchObj],
                                        changedTouches: [touchObj]
                                    }});
                                    
                                    document.elementFromPoint({x}, {y}).dispatchEvent(touchEvent);
                                """)
                            except Exception:
                                pass
                        
                        elif activity_type == "tab_switch":
                            # 模擬切換分頁
                            try:
                                # 獲取當前所有分頁
                                handles = self.driver.window_handles
                                if len(handles) > 1:
                                    # 如果有多個分頁，隨機切換到另一個分頁
                                    current_handle = self.driver.current_window_handle
                                    other_handles = [h for h in handles if h != current_handle]
                                    self.driver.switch_to.window(random.choice(other_handles))
                                    time.sleep(random.uniform(0.5, 1.0))
                                    # 切換回原來的分頁
                                    self.driver.switch_to.window(current_handle)
                                else:
                                    # 如果只有一個分頁，嘗試開啟一個新分頁然後關閉它
                                    original_handle = self.driver.current_window_handle
                                    self.driver.execute_script("window.open('about:blank', '_blank');")
                                    self.driver.switch_to.window(self.driver.window_handles[-1])
                                    time.sleep(random.uniform(0.5, 1.0))
                                    self.driver.close()
                                    self.driver.switch_to.window(original_handle)
                            except Exception:
                                pass
                        
                        elif activity_type == "text_selection":
                            # 模擬選取文字
                            try:
                                # 找到頁面上的文字元素
                                text_elements = self.driver.find_elements(By.CSS_SELECTOR, "p, span, div, h1, h2, h3, h4, h5, h6")
                                if text_elements and len(text_elements) > 0:
                                    element = random.choice(text_elements)
                                    if element.is_displayed() and element.text.strip():
                                        # 使用JavaScript模擬選取文字
                                        self.driver.execute_script("""
                                            var element = arguments[0];
                                            var range = document.createRange();
                                            range.selectNodeContents(element);
                                            var selection = window.getSelection();
                                            selection.removeAllRanges();
                                            selection.addRange(range);
                                        """, element)
                                        time.sleep(random.uniform(0.5, 1.0))
                                        # 取消選取
                                        self.driver.execute_script("""
                                            window.getSelection().removeAllRanges();
                                        """)
                            except Exception:
                                pass
                                
                    # 等待一段時間後再執行下一個活動
                    time.sleep(self.keep_alive_interval)
                        
                except WebDriverException as e:
                    self.status_update.emit(self.browser_id, f"瀏覽器錯誤: {str(e)}")
                    break
                    
        except Exception as e:
            self.logger.error(f"瀏覽器執行緒發生異常: {str(e)}")
            self.status_update.emit(self.browser_id, f"錯誤: {str(e)}")
            # 確保異常信息被正確顯示在UI上
            import traceback
            self.logger.error(f"異常詳細信息: {traceback.format_exc()}")
        finally:
            self.logger.info(f"瀏覽器執行緒 {self.browser_id} 結束，執行清理操作")
            self.cleanup()
    
    def cleanup(self):
        """清理資源，關閉瀏覽器"""
        self.is_running = False
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass  # 忽略關閉時的錯誤
            self.driver = None
        self.browser_closed.emit(self.browser_id)
        
    def stop(self):
        """停止執行緒"""
        self.is_running = False


class MainWindow(QMainWindow):
    """主視窗類別"""
    
    def __init__(self):
        super().__init__()
        self.browsers = {}  # 存儲所有瀏覽器執行緒
        self.settings = QSettings("BackgroundWeb", "Settings")
        self.initUI()
        self.loadSettings()
        
    def initUI(self):
        """初始化使用者介面"""
        self.setWindowTitle("背景網頁開啟工具")
        self.setMinimumSize(700, 600)
        
        # 主佈局
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # 創建標籤頁
        self.tabs = QTabWidget()
        
        # 基本設定標籤頁
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # 網址輸入區域
        url_group = QGroupBox("網址設定")
        url_layout = QFormLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("請輸入網址...")
        url_layout.addRow("網址:", self.url_input)
        
        # 保持活動間隔設定
        self.keep_alive_interval = QSpinBox()
        self.keep_alive_interval.setRange(1, 60)
        self.keep_alive_interval.setValue(10)
        self.keep_alive_interval.setSuffix(" 分鐘")
        url_layout.addRow("防閒置間隔:", self.keep_alive_interval)
        
        url_group.setLayout(url_layout)
        basic_layout.addWidget(url_group)
        
        # 按鈕區域
        button_layout = QHBoxLayout()
        
        self.open_button = QPushButton("開啟新網頁")
        self.open_button.clicked.connect(self.openNewBrowser)
        button_layout.addWidget(self.open_button)
        
        self.close_button = QPushButton("關閉選定網頁")
        self.close_button.clicked.connect(self.closeSelectedBrowser)
        button_layout.addWidget(self.close_button)
        
        self.close_all_button = QPushButton("關閉所有網頁")
        self.close_all_button.clicked.connect(self.closeAllBrowsers)
        button_layout.addWidget(self.close_all_button)
        
        basic_layout.addLayout(button_layout)
        
        # 瀏覽器列表
        list_group = QGroupBox("開啟的網頁")
        list_layout = QVBoxLayout()
        
        self.browser_list = QListWidget()
        list_layout.addWidget(self.browser_list)
        
        list_group.setLayout(list_layout)
        basic_layout.addWidget(list_group)
        
        # 進階設定標籤頁
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        # 瀏覽器設定
        browser_group = QGroupBox("瀏覽器設定")
        browser_layout = QFormLayout()
        
        # 無痕模式選項
        self.incognito_mode = QCheckBox("啟用")
        self.incognito_mode.setChecked(True)
        self.incognito_mode.setToolTip("啟用無痕模式，每個瀏覽器實例使用獨立的設定檔")
        browser_layout.addRow("無痕模式:", self.incognito_mode)
        
        # 禁用圖片選項
        self.disable_images = QCheckBox("啟用")
        self.disable_images.setToolTip("禁用圖片載入以提高效能")
        browser_layout.addRow("禁用圖片:", self.disable_images)
        
        # 進階防偵測選項
        self.advanced_stealth = QCheckBox("啟用")
        self.advanced_stealth.setChecked(True)
        self.advanced_stealth.setToolTip("啟用進階防偵測功能，避免被網站識別為自動化工具")
        browser_layout.addRow("進階防偵測:", self.advanced_stealth)
        
        browser_group.setLayout(browser_layout)
        advanced_layout.addWidget(browser_group)
        
        # 代理伺服器設定
        proxy_group = QGroupBox("代理伺服器設定")
        proxy_layout = QFormLayout()
        
        self.proxy_server = QLineEdit()
        self.proxy_server.setPlaceholderText("格式: ip:port")
        proxy_layout.addRow("代理伺服器:", self.proxy_server)
        
        proxy_group.setLayout(proxy_layout)
        advanced_layout.addWidget(proxy_group)
        
        # 使用者代理字串設定
        ua_group = QGroupBox("使用者代理字串設定")
        ua_layout = QVBoxLayout()
        
        # 使用隨機使用者代理字串
        self.random_ua_radio = QRadioButton("使用隨機使用者代理字串")
        self.random_ua_radio.setChecked(True)
        ua_layout.addWidget(self.random_ua_radio)
        
        # 使用自訂使用者代理字串
        self.custom_ua_radio = QRadioButton("使用自訂使用者代理字串")
        ua_layout.addWidget(self.custom_ua_radio)
        
        self.custom_ua_input = QLineEdit()
        self.custom_ua_input.setPlaceholderText("輸入自訂使用者代理字串...")
        self.custom_ua_input.setEnabled(False)
        ua_layout.addWidget(self.custom_ua_input)
        
        # 連接信號
        self.custom_ua_radio.toggled.connect(self.toggleCustomUA)
        
        ua_group.setLayout(ua_layout)
        advanced_layout.addWidget(ua_group)
        
        # 添加彈性空間
        advanced_layout.addStretch(1)
        
        # 添加標籤頁
        self.tabs.addTab(basic_tab, "基本設定")
        self.tabs.addTab(advanced_tab, "進階設定")
        
        main_layout.addWidget(self.tabs)
        
        # 狀態欄
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就緒")
        
        self.setCentralWidget(main_widget)
        
    def toggleCustomUA(self, checked):
        """切換自訂使用者代理字串輸入框的啟用狀態"""
        self.custom_ua_input.setEnabled(checked)
        
    def loadSettings(self):
        """載入設定"""
        self.url_input.setText("")
        self.keep_alive_interval.setValue(int(self.settings.value("keep_alive_interval", 10)))
        
        # 載入進階設定
        self.incognito_mode.setChecked(self.settings.value("incognito_mode", "true") == "true")
        self.disable_images.setChecked(self.settings.value("disable_images", "false") == "true")
        self.advanced_stealth.setChecked(self.settings.value("advanced_stealth", "true") == "true")
        self.proxy_server.setText(self.settings.value("proxy_server", ""))
        
        use_custom_ua = self.settings.value("use_custom_ua", "false") == "true"
        self.custom_ua_radio.setChecked(use_custom_ua)
        self.random_ua_radio.setChecked(not use_custom_ua)
        self.custom_ua_input.setText(self.settings.value("custom_ua", ""))
        self.custom_ua_input.setEnabled(use_custom_ua)
        
    def saveSettings(self):
        """儲存設定"""
        self.settings.setValue("last_url", self.url_input.text())
        self.settings.setValue("keep_alive_interval", self.keep_alive_interval.value())
        
        # 儲存進階設定
        self.settings.setValue("incognito_mode", str(self.incognito_mode.isChecked()).lower())
        self.settings.setValue("disable_images", str(self.disable_images.isChecked()).lower())
        self.settings.setValue("advanced_stealth", str(self.advanced_stealth.isChecked()).lower())
        self.settings.setValue("proxy_server", self.proxy_server.text())
        self.settings.setValue("use_custom_ua", str(self.custom_ua_radio.isChecked()).lower())
        self.settings.setValue("custom_ua", self.custom_ua_input.text())
        
    def openNewBrowser(self):
        """開啟新的瀏覽器"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "警告", "請輸入有效的網址")
            return
            
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url
            self.url_input.setText(url)
            
        # 生成唯一的瀏覽器ID
        browser_id = f"browser_{int(time.time())}_{len(self.browsers)}"
        
        # 獲取進階設定
        incognito_mode = self.incognito_mode.isChecked()
        disable_images = self.disable_images.isChecked()
        advanced_stealth = self.advanced_stealth.isChecked()
        proxy_server = self.proxy_server.text().strip()
        
        # 獲取使用者代理字串設定
        custom_user_agent = ""
        if self.custom_ua_radio.isChecked():
            custom_user_agent = self.custom_ua_input.text().strip()
        
        # 創建新的瀏覽器執行緒
        browser_thread = BrowserThread(
            browser_id=browser_id,
            url=url,
            keep_alive_interval=self.keep_alive_interval.value() * 60,  # 將分鐘轉換為秒
            incognito_mode=incognito_mode,
            disable_images=disable_images,
            proxy_server=proxy_server,
            custom_user_agent=custom_user_agent,
            advanced_stealth=advanced_stealth
        )
        
        # 連接信號
        browser_thread.status_update.connect(self.updateBrowserStatus)
        browser_thread.browser_closed.connect(self.onBrowserClosed)
        
        # 添加到列表
        item = QListWidgetItem(f"{url} - 正在啟動...")
        item.setData(Qt.UserRole, browser_id)
        self.browser_list.addItem(item)
        
        # 儲存執行緒並啟動
        self.browsers[browser_id] = {
            "thread": browser_thread,
            "item": item,
            "url": url
        }
        
        try:
            browser_thread.start()
            # 更新狀態欄
            self.statusBar.showMessage(f"正在開啟網頁: {url}")
        except Exception as e:
            # 如果執行緒啟動失敗，顯示錯誤訊息並清理資源
            error_msg = f"無法開啟瀏覽器: {str(e)}"
            QMessageBox.critical(self, "錯誤", error_msg)
            self.statusBar.showMessage(error_msg)
            # 從列表中移除
            self.browser_list.takeItem(self.browser_list.row(item))
            del self.browsers[browser_id]
            return
        
        # 儲存設定
        self.saveSettings()
        
    def updateBrowserStatus(self, browser_id, status):
        """更新瀏覽器狀態"""
        if browser_id in self.browsers:
            browser_info = self.browsers[browser_id]
            
            # 檢查狀態訊息是否包含錯誤信息
            if "錯誤" in status or "失敗" in status:
                # 顯示更詳細的錯誤訊息對話框
                error_msg = status
                if "Chrome驅動程式安裝失敗" in status:
                    error_msg += "\n\n可能的解決方法：\n"
                    error_msg += "1. 確保您的Chrome瀏覽器是最新版本\n"
                    error_msg += "2. 檢查網路連接是否正常\n"
                    error_msg += "3. 嘗試重新啟動程式\n"
                    error_msg += "4. 如果問題持續存在，請嘗試手動下載Chrome驅動程式\n"
                    error_msg += "\n詳細錯誤信息：\n"
                    if "There is no such driver by url" in status:
                        error_msg += "找不到對應版本的Chrome驅動程式，程式將嘗試使用替代方法安裝。\n"
                        error_msg += "如果問題持續存在，請考慮降級Chrome瀏覽器版本或手動安裝驅動程式。"
                    elif "ChromeDriver only supports Chrome version" in status:
                        error_msg += "Chrome驅動程式版本與瀏覽器版本不匹配，程式將嘗試使用替代方法安裝。\n"
                        error_msg += "如果問題持續存在，請考慮更新Chrome瀏覽器或手動安裝匹配的驅動程式。"
                
                QMessageBox.warning(self, "瀏覽器錯誤", error_msg)
                self.statusBar.showMessage(status)
            item = browser_info["item"]
            url = browser_info["url"]
            item.setText(f"{url} - {status}")
            
    def closeSelectedBrowser(self):
        """關閉選定的瀏覽器"""
        selected_items = self.browser_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "提示", "請先選擇要關閉的網頁")
            return
            
        for item in selected_items:
            browser_id = item.data(Qt.UserRole)
            if browser_id in self.browsers:
                self.browsers[browser_id]["thread"].stop()
                
    def closeAllBrowsers(self):
        """關閉所有瀏覽器"""
        if not self.browsers:
            return
            
        reply = QMessageBox.question(self, "確認", "確定要關閉所有開啟的網頁嗎？",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for browser_id, browser_info in list(self.browsers.items()):
                browser_info["thread"].stop()
                
    def onBrowserClosed(self, browser_id):
        """處理瀏覽器關閉事件"""
        if browser_id in self.browsers:
            item = self.browsers[browser_id]["item"]
            row = self.browser_list.row(item)
            self.browser_list.takeItem(row)
            del self.browsers[browser_id]
            
    def closeEvent(self, event):
        """處理視窗關閉事件"""
        if self.browsers:
            reply = QMessageBox.question(self, "確認", "關閉程式將會關閉所有開啟的網頁，確定要繼續嗎？",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.closeAllBrowsers()
                # 等待所有瀏覽器關閉
                for browser_info in self.browsers.values():
                    browser_info["thread"].wait(1000)  # 等待最多1秒
                event.accept()
            else:
                event.ignore()
        else:
            self.saveSettings()
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())