# 背景網頁開啟工具 (Background Web Opener) (バックグラウンドウェブオープナー)

**版本: v1.0.0**

[中文](#背景網頁開啟工具) | [English](#background-web-opener) | [日本語](#バックグラウンドウェブオープナー)

**現在您可以直接從GitHub倉庫下載可執行檔：[點擊下載最新版本](https://github.com/musictraveler721217/background_web/releases/latest/download/BackgroundWebOpener.exe)。或參考下方「從源碼安裝」的方法。**

> 最後更新日期: 2023/11/15

## 背景網頁開啟工具

這個程式允許使用者在背景同時開啟多個網頁，特別適合用於同時登入並播放多個課程影片。提供多種瀏覽器設定選項，增強使用體驗，並有效防止網頁閒置登出。

### 主要功能

1. 背景開啟多個網頁同時登入播放課程影片，不受干擾（支援無痕模式）
2. 進階防閒置功能，透過模擬真實使用者行為防止網頁登出
3. 使用原本Cookie或模擬Chrome瀏覽器，避免被偵測為非正常瀏覽器
4. 提供多種瀏覽器設定選項，包括無痕模式、禁用圖片、代理伺服器等
5. 進階防偵測功能，有效避免被網站識別為自動化工具

### 安裝說明

#### 方法一：直接下載可執行檔（推薦）

1. **[點擊下載最新版本](https://github.com/musictraveler721217/background_web/releases/latest/download/BackgroundWebOpener.exe)**
2. 下載完成後，直接雙擊執行檔案即可使用
3. 無需安裝Python或其他依賴項

#### 方法二：從源碼安裝

##### 必要條件

- Python 3.7 或更高版本
- Google Chrome 瀏覽器

##### 安裝步驟

1. 安裝所需的Python套件：

```
pip install -r requirements.txt
```

2. 執行程式：

```
python background_web.py
```

### 使用說明

#### 基本設定

1. 在網址欄位中輸入您想要開啟的網頁網址
2. 設定防閒置間隔時間（預設為10分鐘）
3. 點擊「開啟新網頁」按鈕
4. 您可以重複以上步驟開啟多個網頁
5. 使用「關閉選定網頁」或「關閉所有網頁」按鈕來管理已開啟的網頁

#### 進階設定

在「進階設定」標籤頁中，您可以自訂以下選項：

1. **瀏覽器設定**
   - 無痕模式：啟用後，每個瀏覽器實例使用獨立的設定檔
   - 禁用圖片：啟用後，瀏覽器不會載入圖片，提高效能
   - 進階防偵測：啟用後，使用多種技術避免被網站識別為自動化工具

2. **代理伺服器設定**
   - 可設定代理伺服器，格式為「ip:port」

3. **使用者代理字串設定**
   - 使用隨機使用者代理字串：系統會從最新的Chrome版本中隨機選擇
   - 使用自訂使用者代理字串：可自行輸入特定的使用者代理字串

### 封裝為可執行檔

若要將程式封裝為可執行檔以便在其他電腦上使用，可以使用PyInstaller：

1. 安裝PyInstaller：

```
pip install pyinstaller
```

2. 創建可執行檔：

```
pyinstaller --onefile --windowed background_web.py
```

3. 完成後，可執行檔將會在`dist`資料夾中生成

### 注意事項

- 程式會在使用者目錄下創建`background_web_data`資料夾來儲存瀏覽器資料和日誌
- 每個開啟的網頁會使用獨立的瀏覽器設定檔，類似於無痕視窗的效果
- 程式關閉時會自動關閉所有開啟的網頁
- 進階防閒置功能會模擬真實使用者行為，包括滑鼠移動、滾動頁面、按鍵盤等
- 使用代理伺服器功能時，請確保代理伺服器可用且格式正確
- 自訂使用者代理字串時，建議使用真實瀏覽器的使用者代理字串，避免被網站識別

### 贊助支持

如果您覺得這個工具對您有幫助，歡迎透過以下虛擬貨幣地址贊助支持開發者：

- 虛擬貨幣地址：`0x959D929A0533bd6a7F1543CCF32e15c037c79A19`

---

## Background Web Opener

**Version: v1.0.0**

**You can now download the executable file directly from the GitHub repository: [Download Latest Version](https://github.com/musictraveler721217/background_web/releases/latest/download/BackgroundWebOpener.exe). Alternatively, you can refer to the "Install from Source Code" method below.**

> Last updated: 2023/11/15

This program allows users to open multiple web pages in the background simultaneously, especially suitable for logging in and playing multiple course videos at the same time. It provides various browser settings to enhance the user experience and effectively prevents web page idle logout.

### Main Features

1. Open multiple web pages in the background to log in and play course videos simultaneously without interference (supports incognito mode)
2. Advanced anti-idle function that prevents webpage logout by simulating real user behavior
3. Use original cookies or simulate Chrome browser to avoid being detected as an abnormal browser
4. Provide various browser setting options, including incognito mode, disable images, proxy server, etc.
5. Advanced anti-detection features to effectively avoid being identified as an automation tool by websites

### Installation Instructions

#### Method 1: Download Executable File (Recommended)

1. **[Download Latest Version](https://github.com/musictraveler721217/background_web/releases/latest/download/BackgroundWebOpener.exe)**
2. After downloading, simply double-click the file to use it
3. No need to install Python or other dependencies

#### Method 2: Install from Source Code

##### Requirements

- Python 3.7 or higher
- Google Chrome browser

##### Installation Steps

1. Install the required Python packages:

```
pip install -r requirements.txt
```

2. Run the program:

```
python background_web.py
```

### Usage Instructions

#### Basic Settings

1. Enter the URL of the webpage you want to open in the URL field
2. Set the anti-idle interval time (default is 10 minutes)
3. Click the "Open New Webpage" button
4. You can repeat the above steps to open multiple webpages
5. Use the "Close Selected Webpage" or "Close All Webpages" buttons to manage opened webpages

#### Advanced Settings

In the "Advanced Settings" tab, you can customize the following options:

1. **Browser Settings**
   - Incognito Mode: When enabled, each browser instance uses an independent profile
   - Disable Images: When enabled, the browser will not load images, improving performance
   - Advanced Anti-detection: When enabled, uses various techniques to avoid being identified as an automation tool by websites

2. **Proxy Server Settings**
   - You can set a proxy server in the format "ip:port"

3. **User Agent String Settings**
   - Use Random User Agent String: The system will randomly select from the latest Chrome versions
   - Use Custom User Agent String: You can enter a specific user agent string

### Package as Executable

To package the program as an executable for use on other computers, you can use PyInstaller:

1. Install PyInstaller:

```
pip install pyinstaller
```

2. Create the executable:

```
pyinstaller --onefile --windowed background_web.py
```

3. After completion, the executable will be generated in the `dist` folder

### Notes

- The program will create a `background_web_data` folder in the user directory to store browser data and logs
- Each opened webpage will use an independent browser profile, similar to the effect of an incognito window
- The program will automatically close all opened webpages when it is closed
- The advanced anti-idle function simulates real user behavior, including mouse movement, scrolling pages, pressing keyboard, etc.
- When using the proxy server function, please ensure that the proxy server is available and the format is correct
- When customizing the user agent string, it is recommended to use a real browser's user agent string to avoid being identified by websites

### Sponsorship

If you find this tool helpful, please consider supporting the developer through the following cryptocurrency address:

- Cryptocurrency Address: `0x959D929A0533bd6a7F1543CCF32e15c037c79A19`

---

## バックグラウンドウェブオープナー

**バージョン: v1.0.0**

**GitHubリポジトリから実行可能ファイルを直接ダウンロードできるようになりました：[ここをクリックして最新の実行可能ファイル(.exe)をダウンロード](https://github.com/musictraveler721217/background_web/releases/latest/download/BackgroundWebOpener.exe)。または、以下の「ソースコードからインストール」方法を参照してください。**

> 最終更新日: 2023/11/15

このプログラムは、ユーザーが複数のウェブページを同時にバックグラウンドで開くことを可能にし、特に複数のコース動画に同時にログインして再生するのに適しています。様々なブラウザ設定オプションを提供し、ユーザー体験を向上させ、ウェブページのアイドルログアウトを効果的に防止します。

### 主な機能

1. 複数のウェブページをバックグラウンドで開き、コース動画に同時にログインして再生（シークレットモードをサポート）
2. 実際のユーザー行動をシミュレートすることでウェブページのログアウトを防止する高度なアンチアイドル機能
3. 元のCookieを使用するか、Chromeブラウザをシミュレートして、異常なブラウザとして検出されるのを回避
4. シークレットモード、画像の無効化、プロキシサーバーなど、様々なブラウザ設定オプションを提供
5. ウェブサイトから自動化ツールとして識別されるのを効果的に回避する高度な検出防止機能

### インストール手順

#### 方法1：実行可能ファイルをダウンロード（推奨）

1. [ここをクリックして最新の実行可能ファイル(.exe)をダウンロード](https://github.com/musictraveler721217/background_web/releases/latest/download/BackgroundWebOpener.exe)
2. ダウンロード後、ファイルをダブルクリックするだけで使用できます
3. Pythonやその他の依存関係をインストールする必要はありません

#### 方法2：ソースコードからインストール

##### 必要条件

- Python 3.7以上
- Google Chromeブラウザ

##### インストール手順

1. 必要なPythonパッケージをインストールします：

```
pip install -r requirements.txt
```

2. プログラムを実行します：

```
python background_web.py
```

### 使用方法

#### 基本設定

1. URLフィールドに開きたいウェブページのURLを入力します
2. アンチアイドル間隔時間を設定します（デフォルトは10分）
3. 「新しいウェブページを開く」ボタンをクリックします
4. 上記の手順を繰り返して複数のウェブページを開くことができます
5. 「選択したウェブページを閉じる」または「すべてのウェブページを閉じる」ボタンを使用して、開いたウェブページを管理します

#### 詳細設定

「詳細設定」タブでは、以下のオプションをカスタマイズできます：

1. **ブラウザ設定**
   - シークレットモード：有効にすると、各ブラウザインスタンスは独立したプロファイルを使用します
   - 画像の無効化：有効にすると、ブラウザは画像を読み込まず、パフォーマンスが向上します
   - 高度な検出防止：有効にすると、ウェブサイトから自動化ツールとして識別されるのを回避するための様々な技術を使用します

2. **プロキシサーバー設定**
   - 「ip:port」形式でプロキシサーバーを設定できます

3. **ユーザーエージェント文字列設定**
   - ランダムユーザーエージェント文字列を使用：システムは最新のChromeバージョンからランダムに選択します
   - カスタムユーザーエージェント文字列を使用：特定のユーザーエージェント文字列を入力できます

### 実行可能ファイルとしてパッケージ化

プログラムを他のコンピュータで使用するために実行可能ファイルとしてパッケージ化するには、PyInstallerを使用できます：

1. PyInstallerをインストールします：

```
pip install pyinstaller
```

2. 実行可能ファイルを作成します：

```
pyinstaller --onefile --windowed background_web.py
```

3. 完了後、実行可能ファイルは`dist`フォルダに生成されます

### 注意事項

- プログラムはユーザーディレクトリに`background_web_data`フォルダを作成し、ブラウザデータとログを保存します
- 開かれた各ウェブページは独立したブラウザプロファイルを使用し、シークレットウィンドウの効果に似ています
- プログラムが閉じられると、開かれたすべてのウェブページは自動的に閉じられます
- 高度なアンチアイドル機能は、マウスの移動、ページのスクロール、キーボードの押下などの実際のユーザー行動をシミュレートします
- プロキシサーバー機能を使用する場合は、プロキシサーバーが利用可能で形式が正しいことを確認してください
- ユーザーエージェント文字列をカスタマイズする場合は、ウェブサイトから識別されるのを避けるために、実際のブラウザのユーザーエージェント文字列を使用することをお勧めします

### スポンサーシップ

このツールが役立つと思われる場合は、以下の仮想通貨アドレスを通じて開発者をサポートすることを検討してください：

- 仮想通貨アドレス：`0x959D929A0533bd6a7F1543CCF32e15c037c79A19`