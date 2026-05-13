<?xml version='1.0' encoding='utf-8'?>
<TS version="2.1" language="zh_TW" sourcelanguage="en">
<context><name>HelpDialog</name><message>
        <location filename="../fns_help.py" line="163" />
        <source>Merge multiple files into a single text file</source>
        <translation>將多個檔案合併為一個文字檔案</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="164" />
        <source>Combine files of the formats below into one text file in any order. DOCX, PDF, and XLSX require the respective libraries to be installed.</source>
        <translation>將以下格式的檔案依您選擇的順序合併為一個文字檔案。DOCX、PDF、XLSX需安裝對應函式庫後才能擷取文字。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="167" />
        <source>&lt;b&gt;Add files&lt;/b&gt; — Click &lt;code&gt;[📄 Add Files]&lt;/code&gt; or drag and drop files onto the list. Unsupported formats are filtered out automatically.</source>
        <translation>&lt;b&gt;新增檔案&lt;/b&gt; — 點擊&lt;code&gt;[📄 新增檔案]&lt;/code&gt;或將檔案拖曳放置到清單中。不支援的格式會自動過濾。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="168" />
        <source>&lt;b&gt;Set order&lt;/b&gt; — Drag items in the list or use &lt;code&gt;[Up]&lt;/code&gt; / &lt;code&gt;[Down]&lt;/code&gt; to set the merge order.</source>
        <translation>&lt;b&gt;調整順序&lt;/b&gt; — 在清單中拖曳或使用&lt;code&gt;[上移]&lt;/code&gt;/&lt;code&gt;[下移]&lt;/code&gt;設定合併順序。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="169" />
        <source>&lt;b&gt;Set encoding&lt;/b&gt; — Select the &lt;b&gt;read encoding&lt;/b&gt; for each file via the combo box, and choose the &lt;b&gt;save encoding&lt;/b&gt; in the 'Save Settings' panel.</source>
        <translation>&lt;b&gt;設定編碼&lt;/b&gt; — 從每個檔案右側的下拉選單選擇&lt;b&gt;讀取編碼&lt;/b&gt;，在右側「儲存設定」面板選擇&lt;b&gt;儲存編碼&lt;/b&gt;。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="170" />
        <source>&lt;b&gt;File separator&lt;/b&gt; (optional) — Enable 'Insert File Separator' to automatically insert a divider line with the filename between each file.</source>
        <translation>&lt;b&gt;檔案分隔線&lt;/b&gt;（選填）— 勾選「插入檔案分隔線」後，合併時會在每個檔案之間自動插入含檔名的分隔線。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="171" />
        <source>&lt;b&gt;Set save path&lt;/b&gt; (optional) — Click &lt;code&gt;[Set Path]&lt;/code&gt; to pre-select a save location. If not set, a save dialog will appear when you run the merge.</source>
        <translation>&lt;b&gt;指定儲存路徑&lt;/b&gt;（選填）— 點擊&lt;code&gt;[指定路徑]&lt;/code&gt;預先設定儲存位置，執行時自動儲存。未設定則在執行時顯示儲存對話框。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="172" />
        <source>&lt;b&gt;&lt;code&gt;[▶ Merge &amp; Save]&lt;/code&gt;&lt;/b&gt; — Click to merge. The completion message shows a per-file encoding summary.</source>
        <translation>&lt;b&gt;&lt;code&gt;[▶ 合併儲存]&lt;/code&gt;&lt;/b&gt; — 點擊執行合併。完成訊息中可查看各檔案的編碼摘要。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="174" />
        <source>&lt;b&gt;Auto encoding detection&lt;/b&gt; — If chardet is installed, encoding is detected automatically when files are added. If accuracy is low, select manually.</source>
        <translation>&lt;b&gt;編碼自動偵測&lt;/b&gt; — 安裝chardet後，新增檔案時將自動偵測編碼。準確度低時請從下拉選單手動選擇。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="175" />
        <source>&lt;b&gt;Save encoding guide&lt;/b&gt; — UTF-8: general use / UTF-8-BOM: prevents garbled text in Excel / EUC-KR·CP949: legacy Korean apps / UTF-16: special use / &lt;b&gt;Shift-JIS·GBK·Big5&lt;/b&gt;: Japanese / Chinese (Simplified·Traditional) legacy systems</source>
        <translation>&lt;b&gt;儲存編碼選擇參考&lt;/b&gt; — UTF-8：通用推薦 / UTF-8-BOM：Excel中不亂碼 / EUC-KR·CP949：韓語舊版程式相容 / UTF-16：特殊用途 / &lt;b&gt;Shift-JIS·GBK·Big5&lt;/b&gt;：日文·中文（簡體·繁體）舊版系統相容</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="176" />
        <source>&lt;b&gt;Separator format&lt;/b&gt; — When enabled, the following line is inserted before each file: &lt;code&gt;───── ▶ filename.txt ──────&lt;/code&gt;</source>
        <translation>&lt;b&gt;分隔線格式&lt;/b&gt; — 啟用後，每個檔案前插入 &lt;code&gt;───── ▶ 檔案名稱.txt ──────&lt;/code&gt; 格式的行。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="177" />
        <source>If a file fails to read, it is skipped and the rest are merged normally. Errors are shown in the completion message.</source>
        <translation>讀取檔案時若發生錯誤，僅跳過該檔案，其餘檔案正常合併。錯誤內容顯示在完成訊息中。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="178" />
        <source>&lt;code&gt;[Undo]&lt;/code&gt; deletes the merged output file. &lt;b&gt;Original files are never modified.&lt;/b&gt;</source>
        <translation>&lt;code&gt;[復原]&lt;/code&gt;按鈕將刪除合併的輸出檔案。&lt;b&gt;原始檔案不會有任何修改。&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="182" />
        <source>Text Converter</source>
        <translation>Text Converter</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="183" />
        <source>Convert between TXT and EPUB formats</source>
        <translation>在TXT和EPUB格式之間轉換</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="184" />
        <source>Convert TXT files into EPUB e-books, or extract text from EPUB files. Multiple files are converted automatically in sequence.</source>
        <translation>將TXT檔案轉換為EPUB電子書，或從EPUB中擷取文字。新增多個檔案後將依序自動批次轉換。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="186" />
        <source>Select &lt;b&gt;[TXT → EPUB]&lt;/b&gt; or &lt;b&gt;[EPUB → TXT]&lt;/b&gt; at the top first.</source>
        <translation>請先選擇頂部的&lt;b&gt;[TXT → EPUB]&lt;/b&gt;或&lt;b&gt;[EPUB → TXT]&lt;/b&gt;分頁。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="187" />
        <source>&lt;b&gt;Add files&lt;/b&gt; — Click &lt;code&gt;[📄 Add Files]&lt;/code&gt; or drag and drop.</source>
        <translation>&lt;b&gt;新增檔案&lt;/b&gt; — 點擊&lt;code&gt;[📄 新增檔案]&lt;/code&gt;或拖放。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="188" />
        <source>&lt;b&gt;TXT → EPUB settings&lt;/b&gt; — Enter &lt;b&gt;title, author, and language&lt;/b&gt; in the 'Book Info' panel and choose a &lt;b&gt;chapter splitting method&lt;/b&gt;.</source>
        <translation>&lt;b&gt;TXT → EPUB 設定&lt;/b&gt; — 在右側「書籍資訊」面板中輸入&lt;b&gt;書名、作者、語言&lt;/b&gt;，並選擇&lt;b&gt;章節分割方式&lt;/b&gt;。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="189" />
        <source>&lt;b&gt;EPUB → TXT settings&lt;/b&gt; — Configure chapter separator, title inclusion, blank line cleanup, and save encoding in the 'Conversion Options' panel.</source>
        <translation>&lt;b&gt;EPUB → TXT 設定&lt;/b&gt; — 在右側「轉換選項」面板中設定章節分隔線插入、章節標題含入、連續空行整理及儲存編碼。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="190" />
        <source>&lt;b&gt;Output folder&lt;/b&gt; (optional) — The default output folder is set in ⚙ Settings (default: &lt;code&gt;Output/&lt;/code&gt;). The folder opens automatically after saving.</source>
        <translation>&lt;b&gt;輸出資料夾&lt;/b&gt;（選填）— 預設輸出資料夾由⚙設定中的全域設定決定（預設：&lt;code&gt;Output/&lt;/code&gt;）。儲存完成後輸出資料夾會自動開啟。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="191" />
        <source>&lt;b&gt;&lt;code&gt;[▶ Start Conversion]&lt;/code&gt;&lt;/b&gt; — The progress bar shows the status of each file.</source>
        <translation>&lt;b&gt;&lt;code&gt;[▶ 開始轉換]&lt;/code&gt;&lt;/b&gt; — 多檔案時進度列顯示各檔案的轉換狀態。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="193" />
        <source>TXT → EPUB Chapter Splitting</source>
        <translation>TXT → EPUB 章節分割方式</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="194" />
        <source>&lt;b&gt;Divider-based&lt;/b&gt; — Lines made of repeating symbols like &lt;code&gt;===&lt;/code&gt;, &lt;code&gt;---&lt;/code&gt;, or &lt;code&gt;★★★&lt;/code&gt; are treated as chapter boundaries.&lt;br&gt;&lt;br&gt;&lt;b&gt;3+ blank lines&lt;/b&gt; — Sections separated by 3 or more consecutive blank lines are treated as chapters.&lt;br&gt;&lt;br&gt;&lt;b&gt;Single chapter&lt;/b&gt; — The entire file is treated as one chapter.</source>
        <translation>&lt;b&gt;分隔線基準&lt;/b&gt; — 由&lt;code&gt;===&lt;/code&gt;、&lt;code&gt;---&lt;/code&gt;、&lt;code&gt;★★★&lt;/code&gt;等重複符號構成的行被識別為章節邊界。&lt;br&gt;&lt;br&gt;&lt;b&gt;連續3行以上空行&lt;/b&gt; — 連續3行以上的空白段落被識別為章節邊界。&lt;br&gt;&lt;br&gt;&lt;b&gt;全部作為一個章節&lt;/b&gt; — 將整個檔案作為一個章節處理。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="195" />
        <source>EPUB → TXT Conversion Options</source>
        <translation>EPUB → TXT 轉換選項</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="196" />
        <source>&lt;b&gt;Add chapter separator&lt;/b&gt; — Inserts a divider at each chapter boundary (default: on).&lt;br&gt;&lt;b&gt;Include chapter titles&lt;/b&gt; — Displays chapter titles from the EPUB below the divider (default: on).&lt;br&gt;&lt;b&gt;Clean up blank lines&lt;/b&gt; — Removes excessive blank lines generated during extraction (default: on).&lt;br&gt;&lt;b&gt;Save encoding&lt;/b&gt; — Choose the encoding for the output TXT file (default: UTF-8).</source>
        <translation>&lt;b&gt;新增章節分隔線&lt;/b&gt; — 在章節邊界插入分隔線（預設：開啟）。&lt;br&gt;&lt;b&gt;包含章節標題&lt;/b&gt; — 在分隔線下方顯示EPUB中儲存的章節標題（預設：開啟）。&lt;br&gt;&lt;b&gt;整理連續空行&lt;/b&gt; — 整理擷取過程中產生的多餘空行（預設：開啟）。&lt;br&gt;&lt;b&gt;儲存編碼&lt;/b&gt; — 選擇輸出TXT檔案的編碼（預設：UTF-8）。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="197" />
        <source>Setting an output folder keeps results separate from your originals, making it easy to collect all converted files in one place.</source>
        <translation>指定輸出資料夾後，可在不修改原檔案的情況下將轉換結果集中儲存在一處。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="198" />
        <source>Do not close the window while conversion is in progress — it may interrupt the process.</source>
        <translation>轉換過程中請勿關閉視窗，否則可能中斷轉換。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="202" />
        <source>Tag Editor</source>
        <translation>Tag Editor</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="203" />
        <source>Add or remove tags from file names in bulk</source>
        <translation>批次新增或移除檔名中的標籤</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="204" />
        <source>Batch-add or batch-remove bracket tags like &lt;code&gt;[Draft]&lt;/code&gt; or &lt;code&gt;[Final]&lt;/code&gt; from file names, and clean up leading zeros all at once.</source>
        <translation>批次新增或移除檔名中的&lt;code&gt;[暫存]&lt;/code&gt;、&lt;code&gt;[最終]&lt;/code&gt;等括號標籤，同時一次性整理多餘的前導0。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="206" />
        <source>Choose &lt;b&gt;[Remove Tags]&lt;/b&gt;, &lt;b&gt;[Add Tags]&lt;/b&gt;, or &lt;b&gt;[Remove Leading Zeros]&lt;/b&gt; from the top tab first.</source>
        <translation>請根據操作類型從頂部分頁選擇&lt;b&gt;[移除標籤]&lt;/b&gt;/&lt;b&gt;[新增標籤]&lt;/b&gt;/&lt;b&gt;[移除前導零]&lt;/b&gt;。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="207" />
        <source>&lt;b&gt;Add files or folders&lt;/b&gt; — Use &lt;code&gt;[📄 Add Files]&lt;/code&gt; / &lt;code&gt;[📂 Add Folder]&lt;/code&gt; or drag and drop. Adding a folder reads files recursively based on the 'Include subfolders' option.</source>
        <translation>&lt;b&gt;新增檔案或資料夾&lt;/b&gt; — 使用&lt;code&gt;[📄 新增檔案]&lt;/code&gt;/&lt;code&gt;[📂 新增資料夾]&lt;/code&gt;或拖放新增目標。新增資料夾時，依「包含子資料夾」選項遞迴讀取檔案。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="208" />
        <source>&lt;b&gt;Filter settings&lt;/b&gt; — Specify target extensions in the 'Filter' panel (comma-separated). Enable 'All extensions' to process all files regardless of type.</source>
        <translation>&lt;b&gt;篩選器設定&lt;/b&gt; — 在左下角「篩選器設定」面板中指定目標副檔名（逗號分隔）。勾選「所有副檔名」則不限類型處理所有檔案。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="209" />
        <source>&lt;b&gt;Configure options&lt;/b&gt; — Set mode-specific options in the right panel.</source>
        <translation>&lt;b&gt;選項設定&lt;/b&gt; — 在右側面板中設定各模式的選項。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="210" />
        <source>&lt;b&gt;Preview&lt;/b&gt; — Click &lt;code&gt;[Preview]&lt;/code&gt; to see the 'Before → After' table. &lt;b&gt;Always verify before applying.&lt;/b&gt;</source>
        <translation>&lt;b&gt;預覽確認&lt;/b&gt; — 點擊&lt;code&gt;[預覽]&lt;/code&gt;查看「原檔名 → 修改後檔名」的對照表。&lt;b&gt;請務必確認後再套用。&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="211" />
        <source>&lt;b&gt;Apply&lt;/b&gt; — Click &lt;code&gt;[Apply]&lt;/code&gt; if the results look correct.</source>
        <translation>&lt;b&gt;套用&lt;/b&gt; — 結果正確後點擊&lt;code&gt;[套用]&lt;/code&gt;。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="213" />
        <source>Remove Tags</source>
        <translation>移除標籤</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="214" />
        <source>Enter a specific tag in the tag field to remove only that tag. &lt;b&gt;Leave the field empty to remove all &lt;code&gt;[ ]&lt;/code&gt; bracket tags.&lt;/b&gt;&lt;br&gt;&lt;br&gt;Example: entering &lt;code&gt;Final&lt;/code&gt; removes only &lt;code&gt;[Final]&lt;/code&gt;, leaving other tags intact.</source>
        <translation>在標籤輸入欄中輸入特定標籤，則僅移除該標籤。&lt;b&gt;留空則移除檔名中所有&lt;code&gt;[ ]&lt;/code&gt;格式的標籤。&lt;/b&gt;&lt;br&gt;&lt;br&gt;範例：輸入&lt;code&gt;最終&lt;/code&gt; → 僅移除&lt;code&gt;[最終]&lt;/code&gt;，其他標籤保留</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="215" />
        <source>Add Tags</source>
        <translation>新增標籤</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="216" />
        <source>Choose the tag to add and its position (&lt;b&gt;front&lt;/b&gt; or &lt;b&gt;back&lt;/b&gt; of the filename) in the right panel. If the tag already exists, it will not be added again.</source>
        <translation>在右側面板中選擇要新增的標籤和插入位置（檔名&lt;b&gt;前&lt;/b&gt;/&lt;b&gt;後&lt;/b&gt;）。若已存在相同標籤，則不會重複新增。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="217" />
        <source>Remove Leading Zeros</source>
        <translation>移除前導零</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="218" />
        <source>Automatically removes leading zeros from file names (001 → 1, 007 → 7). &lt;b&gt;Numbers connected by hyphens, such as dates, are automatically protected.&lt;/b&gt;</source>
        <translation>自動移除檔名前端多餘的0（001 → 1、007 → 7）。&lt;b&gt;由連字號連接的日期格式數字將自動受到保護。&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="219" />
        <source>Meeting notes 001.docx</source>
        <translation>會議記錄 001.docx</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="219" />
        <source>Meeting notes 1.docx</source>
        <translation>會議記錄 1.docx</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="220" />
        <source>Lecture 007 final.pdf</source>
        <translation>講義資料 007 最終版.pdf</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="220" />
        <source>Lecture 7 final.pdf</source>
        <translation>講義資料 7 最終版.pdf</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="221" />
        <source>2024-01-01 diary.txt</source>
        <translation>2024-01-01 日記.txt</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="221" />
        <source>2024-01-01 diary.txt  ← protected, no change</source>
        <translation>2024-01-01 日記.txt  ← 受保護，無變化</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="222" />
        <source>&lt;b&gt;File renaming can be undone once with [Undo] immediately after applying.&lt;/b&gt; However, the undo data is lost if you run another task or close the window. Always verify with &lt;code&gt;[Preview]&lt;/code&gt; before clicking &lt;code&gt;[Apply]&lt;/code&gt;.</source>
        <translation>&lt;b&gt;檔名修改後可立即使用[復原]還原一次。&lt;/b&gt;但執行新任務或關閉視窗後還原資料將消失。請務必先透過&lt;code&gt;[預覽]&lt;/code&gt;確認後再點擊&lt;code&gt;[套用]&lt;/code&gt;。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="226" />
        <source>Batch Renamer</source>
        <translation>Batch Renamer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="227" />
        <source>Rename folders and files in bulk</source>
        <translation>批次重新命名資料夾和檔案</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="228" />
        <source>Rename subfolders or files using pattern-based rules. Supports 'Smart Extract' (auto-detect) and 'Sequential Number' (manual) modes.</source>
        <translation>使用以模式為基礎的規則批次重新命名子資料夾或檔案。支援自動識別編號的「智慧提取」和手動指定編號的「順序編號」兩種方式。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="230" />
        <source>Select &lt;b&gt;[Folder Rename]&lt;/b&gt; or &lt;b&gt;[File Rename]&lt;/b&gt; from the top tab first.</source>
        <translation>請先從頂部分頁選擇&lt;b&gt;[資料夾重新命名]&lt;/b&gt;或&lt;b&gt;[檔案重新命名]&lt;/b&gt;。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="231" />
        <source>&lt;b&gt;Select target folder&lt;/b&gt; — Use &lt;code&gt;[📂 Select Folder]&lt;/code&gt; or drag and drop to specify the &lt;b&gt;parent folder&lt;/b&gt;. The folder itself is not changed — only its &lt;b&gt;contents&lt;/b&gt; are renamed.</source>
        <translation>&lt;b&gt;指定目標資料夾&lt;/b&gt; — 使用&lt;code&gt;[📂 選擇資料夾]&lt;/code&gt;或拖放指定&lt;b&gt;上層資料夾&lt;/b&gt;。指定的資料夾本身不會改變，只有&lt;b&gt;其內部的下層項目&lt;/b&gt;才會被重新命名。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="232" />
        <source>&lt;b&gt;Select method&lt;/b&gt; — Choose 'Smart Extract' or 'Sequential Number' in the right panel.</source>
        <translation>&lt;b&gt;選擇方式&lt;/b&gt; — 在右側面板選擇「智慧提取」或「順序編號」。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="233" />
        <source>&lt;b&gt;Preview&lt;/b&gt; — Click &lt;code&gt;[Preview]&lt;/code&gt; to review changes. Conflicts are highlighted in the table.</source>
        <translation>&lt;b&gt;預覽確認&lt;/b&gt; — 點擊&lt;code&gt;[預覽]&lt;/code&gt;查看修改結果。名稱衝突時表格中會顯示警告。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="234" />
        <source>&lt;b&gt;Rename&lt;/b&gt; — Click &lt;code&gt;[Rename]&lt;/code&gt;. You can undo once with &lt;code&gt;[Undo]&lt;/code&gt; immediately after.</source>
        <translation>&lt;b&gt;執行重新命名&lt;/b&gt; — 點擊&lt;code&gt;[執行重新命名]&lt;/code&gt;。執行後可立即使用&lt;code&gt;[復原]&lt;/code&gt;還原一次。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="236" />
        <source>🔍 Smart Extract</source>
        <translation>🔍 智慧提取</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="237" />
        <source>Automatically extracts numbers from existing names and reconstructs them.&lt;br&gt;&lt;br&gt;&lt;b&gt;Common prefix handling&lt;/b&gt; — Auto-detect / Manual entry / Keep as-is.&lt;br&gt;&lt;b&gt;Prefix · Suffix&lt;/b&gt; — Text to add before or after the reconstructed name.</source>
        <translation>自動從現有名稱中提取編號並重新建構。&lt;br&gt;&lt;br&gt;&lt;b&gt;共用前綴處理&lt;/b&gt; — 自動偵測 / 手動指定 / 保留不變。&lt;br&gt;&lt;b&gt;前綴·後綴&lt;/b&gt; — 輸入在重構名稱前後新增的文字。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="238" />
        <source>🔢 Sequential Number</source>
        <translation>🔢 順序編號</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="239" />
        <source>Assigns numbers in sequence from first to last. All options are set manually.&lt;br&gt;&lt;br&gt;&lt;b&gt;Start number&lt;/b&gt; — Choose 00 or 01. &lt;b&gt;Digits&lt;/b&gt; — Auto or fixed 2/3/4. &lt;b&gt;Prefix · Suffix&lt;/b&gt; — Text around the number. &lt;b&gt;Name preservation&lt;/b&gt; — 'Number only' or 'Number + original name'. &lt;b&gt;Number reset&lt;/b&gt; — 'Continuous' or 'Reset per group'.</source>
        <translation>從頭到尾按順序分配編號。所有選項均手動指定。&lt;br&gt;&lt;br&gt;&lt;b&gt;起始編號&lt;/b&gt; — 選擇從00或01開始。&lt;b&gt;位數&lt;/b&gt; — 自動或固定2/3/4位。&lt;b&gt;前綴·後綴&lt;/b&gt; — 編號前後新增的文字。&lt;b&gt;名稱保留&lt;/b&gt; — 「僅編號」或「編號+原名稱」。&lt;b&gt;編號重置&lt;/b&gt; — 「全域連續」或「每組重置」。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="240" />
        <source>File extensions are always preserved automatically.</source>
        <translation>檔案重新命名時副檔名始終自動保留。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="241" />
        <source>Dragging a folder recursively scans subfolders and builds groups automatically.</source>
        <translation>拖放資料夾時會遞迴掃描子資料夾並自動建構分組。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="242" />
        <source>Explorer windows open to the target folder are automatically closed before renaming and reopened when done.</source>
        <translation>執行重新命名前，開啟目標資料夾的檔案總管視窗會自動關閉，完成後自動重新開啟。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="243" />
        <source>&lt;b&gt;Renaming takes effect immediately.&lt;/b&gt; You can undo once with &lt;code&gt;[Undo]&lt;/code&gt;, but the data is lost when you run another task or close the window.</source>
        <translation>&lt;b&gt;重新命名會立即生效。&lt;/b&gt;執行後可用&lt;code&gt;[復原]&lt;/code&gt;還原，但執行新任務或關閉視窗後還原資料將消失。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="244" />
        <source>The specified parent folder itself is not modified. Only its contents are renamed.</source>
        <translation>指定的上層資料夾本身不會被修改，僅對其下層項目進行操作。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="248" />
        <source>Text Fixer</source>
        <translation>Text Fixer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="249" />
        <source>Repair line breaks in OCR and e-book text</source>
        <translation>修復OCR和電子書文字的換行問題</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="250" />
        <source>Text extracted from PDFs or EPUBs often has forced line breaks at page width. Text Fixer intelligently restores paragraph structure.</source>
        <translation>從PDF或EPUB擷取的文字常因頁面寬度出現強制換行。Text Fixer可智慧還原段落結構。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="252" />
        <source>&lt;b&gt;Input methods&lt;/b&gt; — Drag a .txt file onto the drop zone, use &lt;code&gt;[📂 Open File]&lt;/code&gt;, or paste text directly into the left 'Original Text' pane.</source>
        <translation>&lt;b&gt;文字輸入方式&lt;/b&gt; — 將.txt檔案拖曳至放置區，使用&lt;code&gt;[📂 開啟檔案]&lt;/code&gt;，或直接在左側「原始文字」區域貼上。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="253" />
        <source>&lt;b&gt;Load text&lt;/b&gt; — Open a file or paste text into the left pane.</source>
        <translation>&lt;b&gt;輸入文字&lt;/b&gt; — 開啟檔案或將文字貼到左側區域。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="254" />
        <source>&lt;b&gt;Choose options&lt;/b&gt; — Combine the four options as needed. Start with &lt;b&gt;① + ④&lt;/b&gt; for most cases.</source>
        <translation>&lt;b&gt;選擇選項&lt;/b&gt; — 根據需要組合四個選項。大多數情況下先從&lt;b&gt;① + ④&lt;/b&gt;開始嘗試。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="255" />
        <source>&lt;b&gt;&lt;code&gt;[✦ Fix]&lt;/code&gt;&lt;/b&gt; — Compare the left (original) and right (result) panes side by side.</source>
        <translation>&lt;b&gt;&lt;code&gt;[✦ 執行修復]&lt;/code&gt;&lt;/b&gt; — 左側（原始）與右側（結果）並排比較，確認修復效果。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="256" />
        <source>&lt;b&gt;Save&lt;/b&gt; — Click &lt;code&gt;[Save ▼]&lt;/code&gt; if satisfied. If not, use &lt;code&gt;[Undo]&lt;/code&gt; to restore the original and retry with different options.</source>
        <translation>&lt;b&gt;儲存&lt;/b&gt; — 滿意後點擊&lt;code&gt;[儲存 ▼]&lt;/code&gt;。不滿意則使用&lt;code&gt;[復原]&lt;/code&gt;還原，更換選項後重新嘗試。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="258" />
        <source>① Merge Line Breaks (blank-line basis)</source>
        <translation>① 合併換行（以空行為基準）</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="259" />
        <source>Splits text into paragraphs by blank lines, then merges forced line breaks within each paragraph. &lt;b&gt;Not merged&lt;/b&gt; — Lines ending with period, exclamation, question mark, or quote; and divider lines like &lt;code&gt;───&lt;/code&gt;, &lt;code&gt;===&lt;/code&gt;, &lt;code&gt;★★★&lt;/code&gt;. This is the core option for fixing PDF/EPUB text. Enable it first in most cases.</source>
        <translation>以空行劃分段落，然後合併段落內被強制折斷的行。&lt;b&gt;不合併的情況&lt;/b&gt; — 以句號、驚嘆號、問號、引號結尾的行，以及&lt;code&gt;───&lt;/code&gt;、&lt;code&gt;===&lt;/code&gt;、&lt;code&gt;★★★&lt;/code&gt;等分隔線不參與合併。這是修復PDF/EPUB文字的核心選項，大多數情況下請先開啟。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="260" />
        <source>② Auto Paragraph Split (max N chars)</source>
        <translation>② 自動段落分割（最多N字）</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="261" />
        <source>After merging, splits overly long lines at sentence boundaries based on a character limit. Short sentences are grouped together within the limit. Default: 100 chars. Try 150-200 for long-sentence manuscripts.</source>
        <translation>①合併後過長的行在句子邊界按N字標準分割。較短的句子在N字範圍內自動組合。預設100字。句子較長時可嘗試調整為150~200字。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="262" />
        <source>③ Insert Blank Line Between Sentences</source>
        <translation>③ 在句子之間插入空行</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="263" />
        <source>Inserts a blank line after lines ending with period/quote, or before dialogue. Useful for improving readability in dialogue-heavy text.</source>
        <translation>在以句號/引號結尾的行後，或對話前自動插入空行。適用於提高對話較多的文字的可讀性。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="264" />
        <source>④ Reduce Excessive Blank Lines (max N lines)</source>
        <translation>④ 減少過多空行（最多N行）</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="265" />
        <source>Collapses consecutive blank lines to a maximum of N. Default 1 is recommended. Use 2 for multi-section documents.</source>
        <translation>將連續空行壓縮為最多N行。預設1行。多節結構的文件建議設為2行。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="267" />
        <source>&lt;b&gt;Recommended combinations&lt;/b&gt; — PDF/EPUB text: &lt;b&gt;① + ④&lt;/b&gt; / Dialogue-heavy text: &lt;b&gt;① + ③&lt;/b&gt; / OCR output with long paragraphs: &lt;b&gt;① + ② + ④&lt;/b&gt;</source>
        <translation>&lt;b&gt;推薦組合&lt;/b&gt; — PDF/EPUB文字修復：&lt;b&gt;① + ④&lt;/b&gt; / 對話為主的文字：&lt;b&gt;① + ③&lt;/b&gt; / OCR結果·長段落整理：&lt;b&gt;① + ② + ④&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="268" />
        <source>&lt;b&gt;Save options&lt;/b&gt; — &lt;b&gt;Save as [Fixed] beside original&lt;/b&gt;: keeps original, saves corrected version as &lt;code&gt;[Fixed]filename.txt&lt;/code&gt; / &lt;b&gt;Save As&lt;/b&gt;: choose location and name / &lt;b&gt;Undo&lt;/b&gt;: restores the pre-fix text in the left pane (available once after running Fix)</source>
        <translation>&lt;b&gt;儲存方式&lt;/b&gt; — &lt;b&gt;在原位置以[Fixed]標籤儲存&lt;/b&gt;：保留原檔案，修復版另存為&lt;code&gt;[Fixed]檔名.txt&lt;/code&gt; / &lt;b&gt;另存新檔&lt;/b&gt;：手動指定位置和檔名 / &lt;b&gt;復原&lt;/b&gt;：將修復前的原始文字還原到左側窗格（執行修復後可使用一次）</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="269" />
        <source>🟡 &lt;b&gt;Yellow lines&lt;/b&gt; = lines merged from multiple / 🟠 &lt;b&gt;Orange lines&lt;/b&gt; = blank line removed. Highlighting is skipped for files over 3,000 lines.</source>
        <translation>🟡 &lt;b&gt;黃色行&lt;/b&gt; = 多行合併為一行 / 🟠 &lt;b&gt;橙色行&lt;/b&gt; = 空行被刪除的位置。超過3,000行的大型檔案將跳過高亮顯示。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="270" />
        <source>The status bar at the bottom shows &lt;b&gt;merge count, blank lines removed, original line count, and final line count&lt;/b&gt;.</source>
        <translation>底部統計列顯示&lt;b&gt;合併次數、空行刪除數、原始行數、最終行數&lt;/b&gt;。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="271" />
        <source>Press &lt;b&gt;Ctrl+F&lt;/b&gt; to search within the source and result text. Enter jumps to the next match, Shift+Enter to the previous.</source>
        <translation>按&lt;b&gt;Ctrl+F&lt;/b&gt;可在原文和修改後的文字中搜尋關鍵字。Enter跳到下一個，Shift+Enter跳到上一個。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="272" />
        <source>Files are always saved as &lt;b&gt;UTF-8&lt;/b&gt;. Convert the encoding separately if you need to preserve the original (e.g. EUC-KR).</source>
        <translation>檔案始終以&lt;b&gt;UTF-8&lt;/b&gt;編碼儲存。如需保留原始編碼（如EUC-KR），請另行轉換。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="274" />
        <source>&lt;b&gt;Partially corrupted files&lt;/b&gt; — Files with damaged bytes can still be opened. Corrupted characters are shown as &lt;code&gt;�&lt;/code&gt; (U+FFFD), and the status bar shows a &lt;b&gt;⚠&lt;/b&gt; icon with a 'Partial encoding failure' warning.</source>
        <translation>&lt;b&gt;部分損毀檔案的處理&lt;/b&gt; — 部分位元組損毀的檔案也可以開啟。損毀的字元顯示為&lt;code&gt;�&lt;/code&gt;（U+FFFD），狀態列會顯示&lt;b&gt;⚠&lt;/b&gt;圖示和「部分編碼失敗」警告。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="275" />
        <source>Text Fixer is optimized for &lt;b&gt;detailed inspection of a single file&lt;/b&gt;. Open corrupted files to see exactly where the damage is, edit those spots manually, or decide whether to re-acquire the original.</source>
        <translation>Text Fixer 針對&lt;b&gt;單一檔案的精細審核&lt;/b&gt;進行了最佳化。開啟損毀檔案可直接檢視損毀位置，手動編輯該段，或判斷是否需要重新取得原始檔案。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="276" />
        <source>Files with tens of thousands of corrupted characters rarely recover well. Re-downloading from the source is usually better. Bulk Fixer automatically skips such files to protect the originals.</source>
        <translation>數萬字元以上的大量損毀檔案難以透過校正恢復品質。建議優先考慮從原來源重新下載。Bulk Fixer 會自動略過此類檔案以保護原始檔案。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="280" />
        <source>Bulk Fixer</source>
        <translation>Bulk Fixer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="281" />
        <source>Batch-correct line breaks across multiple TXT files</source>
        <translation>批量校正多個TXT檔案的換行</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="282" />
        <source>Applies the Text Fixer correction engine to many files at once. Ideal for cleaning up batches of TXT files extracted from OCR or e-books.</source>
        <translation>將Text Fixer的校正引擎批量應用於多個檔案。適用於一次性整理從OCR或電子書中提取的大量TXT檔案。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="284" />
        <source>&lt;b&gt;Add files&lt;/b&gt; — Use &lt;code&gt;[📄 Add files]&lt;/code&gt; or &lt;code&gt;[📂 Add folder]&lt;/code&gt; to load TXT files. You can also drag and drop folders directly onto the file list to recursively collect &lt;code&gt;.txt&lt;/code&gt; files.</source>
        <translation>&lt;b&gt;新增檔案&lt;/b&gt; — 使用&lt;code&gt;[📄 新增檔案]&lt;/code&gt;或&lt;code&gt;[📂 新增資料夾]&lt;/code&gt;載入TXT檔案。也可以將資料夾直接拖放到檔案清單中，自動遞迴收集&lt;code&gt;.txt&lt;/code&gt;檔案。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="285" />
        <source>&lt;b&gt;Set options&lt;/b&gt; — Choose the merge mode (Auto / Korean / English) and correction options in the right panel. Use the &lt;b&gt;Preset&lt;/b&gt; dropdown to quickly apply "General document" or "Book / Novel" settings.</source>
        <translation>&lt;b&gt;設定選項&lt;/b&gt; — 在右側面板中選擇合併模式（自動/韓語/英語）和四個校正選項。使用&lt;b&gt;預設&lt;/b&gt;下拉選單選擇「一般文件」或「書籍·小說」可一鍵配置選項。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="286" />
        <source>&lt;b&gt;Save settings&lt;/b&gt; — Specify an output folder, or leave it empty to save as &lt;code&gt;[Fixed]filename.txt&lt;/code&gt; beside each original file. Enable &lt;b&gt;Preserve folder structure&lt;/b&gt; to recreate the original subfolder hierarchy inside the output folder.</source>
        <translation>&lt;b&gt;儲存設定&lt;/b&gt; — 指定輸出資料夾，或留空則以&lt;code&gt;[Fixed]檔名.txt&lt;/code&gt;儲存在原檔案旁邊。勾選&lt;b&gt;保留資料夾結構&lt;/b&gt;可在輸出資料夾中重現原始子資料夾層級。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="287" />
        <source>&lt;b&gt;Click &lt;code&gt;[▶ Start batch fix]&lt;/code&gt;&lt;/b&gt; — Progress is shown during processing; a summary of successes and failures is displayed on completion.</source>
        <translation>&lt;b&gt;點擊&lt;code&gt;[▶ 開始批量校正]&lt;/code&gt;&lt;/b&gt; — 處理期間顯示進度，完成後通知成功和失敗檔案數。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="288" />
        <source>Click any file in the list to preview the corrected result in the preview panel on the right.</source>
        <translation>點擊檔案清單中的項目，可在右側預覽面板中預覽校正結果。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="289" />
        <source>The default output folder is &lt;code&gt;Output/&lt;/code&gt;. You can change it globally in ⚙ Settings or per-tab individually. The folder opens automatically after saving.</source>
        <translation>預設輸出資料夾為&lt;code&gt;Output/&lt;/code&gt;。可在⚙設定中全域更改，也可在各分頁單獨指定。儲存完成後自動開啟。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="290" />
        <source>Only TXT files are supported. Convert DOCX, PDF, etc. to TXT with Text Converter first.</source>
        <translation>僅支援TXT檔案。請先用Text Converter將DOCX、PDF等格式轉換為TXT後再使用。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="292" />
        <source>&lt;b&gt;Automatic corruption tiering&lt;/b&gt; — Bulk Fixer classifies partially corrupted files into three tiers based on damage severity:&lt;br&gt;• &lt;b&gt;Tier 1&lt;/b&gt; (1–500 damaged chars): Fixed + report generated&lt;br&gt;• &lt;b&gt;Tier 2&lt;/b&gt; (501–5,000 damaged chars): Fixed + report generated (review recommended)&lt;br&gt;• &lt;b&gt;Tier 3&lt;/b&gt; (5,001+ damaged chars): &lt;b&gt;Automatically skipped (original preserved)&lt;/b&gt; + report only</source>
        <translation>&lt;b&gt;編碼損毀檔案自動分級&lt;/b&gt; — Bulk Fixer 偵測到部分損毀檔案後，依據損毀程度分為三級處理：&lt;br&gt;• &lt;b&gt;Tier 1&lt;/b&gt;（1~500字元損毀）：校正後產生報告&lt;br&gt;• &lt;b&gt;Tier 2&lt;/b&gt;（501~5,000字元損毀）：校正後產生報告（建議審核）&lt;br&gt;• &lt;b&gt;Tier 3&lt;/b&gt;（5,001字元以上）：&lt;b&gt;自動略過（保護原始檔案）&lt;/b&gt; + 僅產生報告</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="293" />
        <source>Reports are created next to the fixed output as &lt;code&gt;{original_filename}.encoding_report.txt&lt;/code&gt;, detailing damaged line/column positions for up to 5,000 entries.</source>
        <translation>報告檔案以&lt;code&gt;{原檔名}.encoding_report.txt&lt;/code&gt;的形式產生在校正版旁邊，詳細記錄哪些行、哪些欄出現損毀，最多記錄 5,000 筆。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="294" />
        <source>Files skipped as Tier 3 should be &lt;b&gt;individually reviewed in Text Fixer&lt;/b&gt;. Heavy corruption usually means wrong encoding detection or a corrupted source, so re-acquiring the original is often better than forcing correction.</source>
        <translation>被 Tier 3 略過的檔案應&lt;b&gt;在 Text Fixer 中個別審核&lt;/b&gt;。大量損毀通常意味著編碼偵測錯誤或原始檔案本身有問題，與其強制批量校正，不如重新取得原始檔案。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="298" />
        <source>Shortcuts &amp; Tips</source>
        <translation>快捷鍵 &amp; 使用技巧</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="299" />
        <source>Use keyboard shortcuts to navigate quickly. All shortcuts can be customized in Settings.</source>
        <translation>使用鍵盤快捷鍵快速操作，可在設定中自訂。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="301" />
        <source>Go to Text Merger</source>
        <translation>前往 Text Merger</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="302" />
        <source>Go to Text Converter</source>
        <translation>前往 Text Converter</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="303" />
        <source>Go to Tag Editor</source>
        <translation>前往 Tag Editor</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="304" />
        <source>Go to Batch Renamer</source>
        <translation>前往 Batch Renamer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="305" />
        <source>Go to Text Fixer</source>
        <translation>前往 Text Fixer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="306" />
        <source>Go to Bulk Fixer</source>
        <translation>前往 Bulk Fixer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="307" />
        <source>Search text in Text Fixer</source>
        <translation>在 Text Fixer 中搜尋文字</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="308" />
        <source>⚙ button (top right)</source>
        <translation>⚙ 按鈕(右上角)</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="308" />
        <source>Open Settings — change theme, language, and shortcuts</source>
        <translation>開啟設定 — 可更改主題、語言和快捷鍵</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="309" />
        <source>Settings (theme, language, shortcuts) are saved automatically on exit and restored on next launch.</source>
        <translation>設定（主題、語言、快捷鍵）在關閉時自動儲存，下次啟動時還原。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="310" />
        <source>&lt;b&gt;Drag and drop&lt;/b&gt; is supported in all tabs. Dropping a folder adds all supported files inside it at once.</source>
        <translation>所有分頁均支援&lt;b&gt;拖放&lt;/b&gt;載入檔案。拖入資料夾時，將批次新增其中的支援檔案。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="311" />
        <source>🔋 &lt;b&gt;Sleep Prevention&lt;/b&gt; — While Text Merger, Text Converter, Text Fixer, or Bulk Fixer is running, Windows sleep mode is automatically blocked. It is released immediately when the task completes or an error occurs. Screen lock is unaffected.</source>
        <translation>🔋 &lt;b&gt;防止休眠&lt;/b&gt; — Text Merger、Text Converter、Text Fixer 或 Bulk Fixer 執行任務期間，Windows 休眠模式將被自動封鎖。任務完成或發生錯誤時立即解除。螢幕鎖定與休眠無關，處理過程中仍可正常使用。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="315" />
        <source>File creation notice</source>
        <translation>生成檔案說明</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="316" />
        <source>Files and folders created automatically during use</source>
        <translation>程式使用過程中自動建立的檔案和資料夾</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="317" />
        <source>File Nexus Suite automatically creates the following items in the program folder for settings storage, default output, and error logging.</source>
        <translation>File Nexus Suite會在程式所在資料夾中自動建立以下內容，用於儲存設定、預設輸出和錯誤記錄。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="319" />
        <source>&lt;b&gt;FileNexusSuite.json&lt;/b&gt; — Stores your theme, language, shortcuts, and tab settings. Saved on exit, restored on next launch.</source>
        <translation>&lt;b&gt;FileNexusSuite.json&lt;/b&gt; — 儲存主題、語言、快捷鍵及各分頁設定的設定檔。結束時自動儲存，下次啟動時還原。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="320" />
        <source>&lt;b&gt;Output/&lt;/b&gt; — Default output folder for Text Converter, Bulk Fixer, and Text Fixer. Created automatically on first launch. Change the location globally in ⚙ Settings; the folder opens automatically after saving.</source>
        <translation>&lt;b&gt;Output/&lt;/b&gt; — Text Converter、Bulk Fixer和Text Fixer的預設輸出資料夾。首次啟動時自動建立。可在⚙設定中全域更改位置，儲存完成時自動開啟。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="321" />
        <source>&lt;b&gt;logs/crash_*.log&lt;/b&gt; — Crash logs generated when an unexpected error occurs. Only the 3 most recent logs are kept; older ones are deleted automatically.</source>
        <translation>&lt;b&gt;logs/crash_*.log&lt;/b&gt; — 發生意外錯誤時自動生成的當機日誌。僅保留最近3個，舊檔案自動刪除。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="322" />
        <source>&lt;b&gt;_internal/&lt;/b&gt; — Created automatically in folder-style exe builds. Contains the Python runtime. &lt;b&gt;Deleting it will prevent the program from running.&lt;/b&gt;</source>
        <translation>&lt;b&gt;_internal/&lt;/b&gt; — 資料夾形式exe建置時自動生成的Python執行環境資料夾。&lt;b&gt;刪除後程式將無法執行。&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="323" />
        <source>You can safely delete any of these files or folders. Required items will be recreated automatically on the next launch.</source>
        <translation>可以直接刪除這些檔案和資料夾。下次啟動時，所需內容將自動重新建立。</translation>
    </message>
<message>
        <location filename="../fns_help.py" line="132" />
        <source>💡  Help — File Nexus Suite v%1</source>
        <translation>💡  說明 — File Nexus Suite v%1</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="532" />
        <source>💡  Help</source>
        <translation>💡  說明</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="582" />
        <source>Close</source>
        <translation>關閉</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="601" />
        <source>About</source>
        <translation>簡介</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="144" />
        <source>File Nexus Suite is an integrated file utility for managing text, e-books, and media files. Text merging, EPUB conversion, file-name tag editing, batch renaming, line-break correction, and bulk fixing — six core features, all in one window.</source>
        <translation>File Nexus Suite 是專為文字、電子書及媒體檔案作業設計的綜合檔案工具。文字合併、EPUB轉換、檔名標籤編輯、批次重新命名、換行校正、批次校正 — 六大核心功能集於一個視窗之中。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="162" />
        <source>Text Merger</source>
        <translation>Text Merger</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="452" />
        <source>Native support</source>
        <translation>原生支援</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="453" />
        <source>Library required</source>
        <translation>需安裝程式庫</translation>
    </message>
</context></TS>