<?xml version='1.0' encoding='utf-8'?>
<TS version="2.1" language="ja_JP" sourcelanguage="en">
<context><name>HelpDialog</name><message>
        <location filename="../fns_help.py" line="163" />
        <source>Merge multiple files into a single text file</source>
        <translation>複数ファイルを1つのテキストファイルに結合します</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="164" />
        <source>Combine files of the formats below into one text file in any order. DOCX, PDF, and XLSX require the respective libraries to be installed.</source>
        <translation>以下の形式のファイルを任意の順序で結合して1つのテキストファイルを作成します。DOCX・PDF・XLSXは対応ライブラリがインストールされている場合のみ利用できます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="167" />
        <source>&lt;b&gt;Add files&lt;/b&gt; — Click &lt;code&gt;[📄 Add Files]&lt;/code&gt; or drag and drop files onto the list. Unsupported formats are filtered out automatically.</source>
        <translation>&lt;b&gt;ファイル追加&lt;/b&gt; — &lt;code&gt;[📄 ファイル追加]&lt;/code&gt;ボタンまたはドラッグ＆ドロップでリストに追加します。未対応の形式は自動的に除外されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="168" />
        <source>&lt;b&gt;Set order&lt;/b&gt; — Drag items in the list or use &lt;code&gt;[Up]&lt;/code&gt; / &lt;code&gt;[Down]&lt;/code&gt; to set the merge order.</source>
        <translation>&lt;b&gt;順序調整&lt;/b&gt; — リスト内でドラッグするか&lt;code&gt;[上へ]&lt;/code&gt;/&lt;code&gt;[下へ]&lt;/code&gt;で結合順序を設定します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="169" />
        <source>&lt;b&gt;Set encoding&lt;/b&gt; — Select the &lt;b&gt;read encoding&lt;/b&gt; for each file via the combo box, and choose the &lt;b&gt;save encoding&lt;/b&gt; in the 'Save Settings' panel.</source>
        <translation>&lt;b&gt;エンコード設定&lt;/b&gt; — 各ファイルの&lt;b&gt;読み込みエンコード&lt;/b&gt;をコンボボックスで選択し、右の「保存設定」パネルで&lt;b&gt;保存エンコード&lt;/b&gt;を選択します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="170" />
        <source>&lt;b&gt;File separator&lt;/b&gt; (optional) — Enable 'Insert File Separator' to automatically insert a divider line with the filename between each file.</source>
        <translation>&lt;b&gt;ファイル区切り線&lt;/b&gt;（任意）— 「ファイル区切り線を挿入」をオンにすると、各ファイル間にファイル名入りの区切り線が自動挿入されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="171" />
        <source>&lt;b&gt;Set save path&lt;/b&gt; (optional) — Click &lt;code&gt;[Set Path]&lt;/code&gt; to pre-select a save location. If not set, a save dialog will appear when you run the merge.</source>
        <translation>&lt;b&gt;保存先指定&lt;/b&gt;（任意）— &lt;code&gt;[パス指定]&lt;/code&gt;で保存先を設定すると実行時に自動保存されます。未設定の場合は保存ダイアログが表示されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="172" />
        <source>&lt;b&gt;&lt;code&gt;[▶ Merge &amp; Save]&lt;/code&gt;&lt;/b&gt; — Click to merge. The completion message shows a per-file encoding summary.</source>
        <translation>&lt;b&gt;&lt;code&gt;[▶ 結合・保存]&lt;/code&gt;&lt;/b&gt; — クリックして結合を実行します。完了メッセージでファイルごとのエンコード概要を確認できます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="174" />
        <source>&lt;b&gt;Auto encoding detection&lt;/b&gt; — If chardet is installed, encoding is detected automatically when files are added. If accuracy is low, select manually.</source>
        <translation>&lt;b&gt;エンコード自動検出&lt;/b&gt; — chardetがインストールされていると、ファイル追加時にエンコードを自動検出します。精度が低い場合はコンボボックスで手動選択してください。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="175" />
        <source>&lt;b&gt;Save encoding guide&lt;/b&gt; — UTF-8: general use / UTF-8-BOM: prevents garbled text in Excel / EUC-KR·CP949: legacy Korean apps / UTF-16: special use / &lt;b&gt;Shift-JIS·GBK·Big5&lt;/b&gt;: Japanese / Chinese (Simplified·Traditional) legacy systems</source>
        <translation>&lt;b&gt;保存エンコード選択の目安&lt;/b&gt; — UTF-8：汎用推奨 / UTF-8-BOM：Excelで文字化けしない / EUC-KR・CP949：韓国語レガシーアプリ向け / UTF-16：特殊用途 / &lt;b&gt;Shift-JIS・GBK・Big5&lt;/b&gt;：日本語・中国語（簡体字・繁体字）レガシーシステム互換</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="176" />
        <source>&lt;b&gt;Separator format&lt;/b&gt; — When enabled, the following line is inserted before each file: &lt;code&gt;───── ▶ filename.txt ──────&lt;/code&gt;</source>
        <translation>&lt;b&gt;区切り線の形式&lt;/b&gt; — オンにすると各ファイルの前に &lt;code&gt;───── ▶ ファイル名.txt ──────&lt;/code&gt; 形式の行が挿入されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="177" />
        <source>If a file fails to read, it is skipped and the rest are merged normally. Errors are shown in the completion message.</source>
        <translation>ファイルの読み込みに失敗した場合、そのファイルのみスキップして残りは正常に結合されます。エラー内容は完了メッセージに表示されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="178" />
        <source>&lt;code&gt;[Undo]&lt;/code&gt; deletes the merged output file. &lt;b&gt;Original files are never modified.&lt;/b&gt;</source>
        <translation>&lt;code&gt;[元に戻す]&lt;/code&gt;ボタンは結合済み出力ファイルを削除します。&lt;b&gt;元のファイルは一切変更されません。&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="182" />
        <source>Text Converter</source>
        <translation>Text Converter</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="183" />
        <source>Convert between TXT and EPUB formats</source>
        <translation>TXT ↔ EPUB 形式を変換します</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="184" />
        <source>Convert TXT files into EPUB e-books, or extract text from EPUB files. Multiple files are converted automatically in sequence.</source>
        <translation>TXTファイルをEPUB電子書籍に変換したり、EPUBからテキストを抽出したりできます。複数ファイルを順番に自動一括変換します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="186" />
        <source>Select &lt;b&gt;[TXT → EPUB]&lt;/b&gt; or &lt;b&gt;[EPUB → TXT]&lt;/b&gt; at the top first.</source>
        <translation>上部の&lt;b&gt;[TXT → EPUB]&lt;/b&gt;または&lt;b&gt;[EPUB → TXT]&lt;/b&gt;タブを先に選択してください。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="187" />
        <source>&lt;b&gt;Add files&lt;/b&gt; — Click &lt;code&gt;[📄 Add Files]&lt;/code&gt; or drag and drop.</source>
        <translation>&lt;b&gt;ファイル追加&lt;/b&gt; — &lt;code&gt;[📄 ファイル追加]&lt;/code&gt;またはドラッグ＆ドロップで読み込みます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="188" />
        <source>&lt;b&gt;TXT → EPUB settings&lt;/b&gt; — Enter &lt;b&gt;title, author, and language&lt;/b&gt; in the 'Book Info' panel and choose a &lt;b&gt;chapter splitting method&lt;/b&gt;.</source>
        <translation>&lt;b&gt;TXT → EPUB 設定&lt;/b&gt; — 「書籍情報」パネルで&lt;b&gt;タイトル・著者・言語&lt;/b&gt;を入力し、&lt;b&gt;章の分割方式&lt;/b&gt;を選択します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="189" />
        <source>&lt;b&gt;EPUB → TXT settings&lt;/b&gt; — Configure chapter separator, title inclusion, blank line cleanup, and save encoding in the 'Conversion Options' panel.</source>
        <translation>&lt;b&gt;EPUB → TXT 設定&lt;/b&gt; — 「変換オプション」パネルで章区切り挿入・章タイトル含有・連続空行の整理・保存エンコードを設定します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="190" />
        <source>&lt;b&gt;Output folder&lt;/b&gt; (optional) — The default output folder is set in ⚙ Settings (default: &lt;code&gt;Output/&lt;/code&gt;). The folder opens automatically after saving.</source>
        <translation>&lt;b&gt;出力フォルダ指定&lt;/b&gt;（任意）— デフォルト出力フォルダは⚙設定で指定したフォルダ（初期値：&lt;code&gt;Output/&lt;/code&gt;）です。保存完了後に出力フォルダが自動的に開きます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="191" />
        <source>&lt;b&gt;&lt;code&gt;[▶ Start Conversion]&lt;/code&gt;&lt;/b&gt; — The progress bar shows the status of each file.</source>
        <translation>&lt;b&gt;&lt;code&gt;[▶ 変換開始]&lt;/code&gt;&lt;/b&gt; — 複数ファイルの場合、プログレスバーで各ファイルの変換状況を確認できます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="193" />
        <source>TXT → EPUB Chapter Splitting</source>
        <translation>TXT → EPUB 章の分割方式</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="194" />
        <source>&lt;b&gt;Divider-based&lt;/b&gt; — Lines made of repeating symbols like &lt;code&gt;===&lt;/code&gt;, &lt;code&gt;---&lt;/code&gt;, or &lt;code&gt;★★★&lt;/code&gt; are treated as chapter boundaries.&lt;br&gt;&lt;br&gt;&lt;b&gt;3+ blank lines&lt;/b&gt; — Sections separated by 3 or more consecutive blank lines are treated as chapters.&lt;br&gt;&lt;br&gt;&lt;b&gt;Single chapter&lt;/b&gt; — The entire file is treated as one chapter.</source>
        <translation>&lt;b&gt;区切り線基準&lt;/b&gt; — &lt;code&gt;===&lt;/code&gt;、&lt;code&gt;---&lt;/code&gt;、&lt;code&gt;★★★&lt;/code&gt;などの反復記号で構成される行を章の境界として認識します。&lt;br&gt;&lt;br&gt;&lt;b&gt;空行3行以上基準&lt;/b&gt; — 連続3行以上の空白区間を章の境界として認識します。&lt;br&gt;&lt;br&gt;&lt;b&gt;全体を1章として処理&lt;/b&gt; — ファイル全体を1つの章として扱います。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="195" />
        <source>EPUB → TXT Conversion Options</source>
        <translation>EPUB → TXT 変換オプション</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="196" />
        <source>&lt;b&gt;Add chapter separator&lt;/b&gt; — Inserts a divider at each chapter boundary (default: on).&lt;br&gt;&lt;b&gt;Include chapter titles&lt;/b&gt; — Displays chapter titles from the EPUB below the divider (default: on).&lt;br&gt;&lt;b&gt;Clean up blank lines&lt;/b&gt; — Removes excessive blank lines generated during extraction (default: on).&lt;br&gt;&lt;b&gt;Save encoding&lt;/b&gt; — Choose the encoding for the output TXT file (default: UTF-8).</source>
        <translation>&lt;b&gt;章区切り線を追加&lt;/b&gt; — 章の境界に区切り線を挿入します（デフォルト：オン）。&lt;br&gt;&lt;b&gt;章タイトルを含む&lt;/b&gt; — EPUBに保存された章タイトルを区切り線の下に表示します（デフォルト：オン）。&lt;br&gt;&lt;b&gt;連続空行の整理&lt;/b&gt; — 抽出時に生じる過剰な空行を整理します（デフォルト：オン）。&lt;br&gt;&lt;b&gt;保存エンコード&lt;/b&gt; — 出力TXTファイルのエンコードを選択します（デフォルト：UTF-8）。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="197" />
        <source>Setting an output folder keeps results separate from your originals, making it easy to collect all converted files in one place.</source>
        <translation>出力フォルダを指定すると、元のフォルダを変更せずに変換結果だけ一か所にまとめられます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="198" />
        <source>Do not close the window while conversion is in progress — it may interrupt the process.</source>
        <translation>変換中はウィンドウを閉じないでください。変換が中断される場合があります。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="202" />
        <source>Tag Editor</source>
        <translation>Tag Editor</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="203" />
        <source>Add or remove tags from file names in bulk</source>
        <translation>ファイル名のタグを一括追加・削除します</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="204" />
        <source>Batch-add or batch-remove bracket tags like &lt;code&gt;[Draft]&lt;/code&gt; or &lt;code&gt;[Final]&lt;/code&gt; from file names, and clean up leading zeros all at once.</source>
        <translation>ファイル名の&lt;code&gt;[一時]&lt;/code&gt;・&lt;code&gt;[最終]&lt;/code&gt;などの角括弧タグを一括処理し、先頭の不要な0も一度にまとめて整理できます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="206" />
        <source>Choose &lt;b&gt;[Remove Tags]&lt;/b&gt;, &lt;b&gt;[Add Tags]&lt;/b&gt;, or &lt;b&gt;[Remove Leading Zeros]&lt;/b&gt; from the top tab first.</source>
        <translation>作業の種類に応じて上部タブから&lt;b&gt;[タグ削除]&lt;/b&gt;/&lt;b&gt;[タグ追加]&lt;/b&gt;/&lt;b&gt;[先頭0削除]&lt;/b&gt;を選択してください。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="207" />
        <source>&lt;b&gt;Add files or folders&lt;/b&gt; — Use &lt;code&gt;[📄 Add Files]&lt;/code&gt; / &lt;code&gt;[📂 Add Folder]&lt;/code&gt; or drag and drop. Adding a folder reads files recursively based on the 'Include subfolders' option.</source>
        <translation>&lt;b&gt;ファイル・フォルダ追加&lt;/b&gt; — &lt;code&gt;[📄 ファイル追加]&lt;/code&gt;/&lt;code&gt;[📂 フォルダ追加]&lt;/code&gt;またはドラッグ＆ドロップで対象を読み込みます。フォルダを追加すると「サブフォルダを含む」オプションに従って再帰的にファイルを読み込みます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="208" />
        <source>&lt;b&gt;Filter settings&lt;/b&gt; — Specify target extensions in the 'Filter' panel (comma-separated). Enable 'All extensions' to process all files regardless of type.</source>
        <translation>&lt;b&gt;フィルター設定&lt;/b&gt; — 左下の「フィルター設定」パネルで対象拡張子を指定します（カンマ区切り）。「すべての拡張子を対象」をオンにすると拡張子に関わらず全ファイルを処理します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="209" />
        <source>&lt;b&gt;Configure options&lt;/b&gt; — Set mode-specific options in the right panel.</source>
        <translation>&lt;b&gt;オプション設定&lt;/b&gt; — 右パネルで各モードのオプションを設定します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="210" />
        <source>&lt;b&gt;Preview&lt;/b&gt; — Click &lt;code&gt;[Preview]&lt;/code&gt; to see the 'Before → After' table. &lt;b&gt;Always verify before applying.&lt;/b&gt;</source>
        <translation>&lt;b&gt;プレビュー確認&lt;/b&gt; — &lt;code&gt;[プレビュー]&lt;/code&gt;をクリックして「元のファイル名 → 変更後のファイル名」の表を確認します。&lt;b&gt;必ず確認してから適用してください。&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="211" />
        <source>&lt;b&gt;Apply&lt;/b&gt; — Click &lt;code&gt;[Apply]&lt;/code&gt; if the results look correct.</source>
        <translation>&lt;b&gt;適用&lt;/b&gt; — 結果が正しければ&lt;code&gt;[適用]&lt;/code&gt;をクリックします。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="213" />
        <source>Remove Tags</source>
        <translation>タグ削除</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="214" />
        <source>Enter a specific tag in the tag field to remove only that tag. &lt;b&gt;Leave the field empty to remove all &lt;code&gt;[ ]&lt;/code&gt; bracket tags.&lt;/b&gt;&lt;br&gt;&lt;br&gt;Example: entering &lt;code&gt;Final&lt;/code&gt; removes only &lt;code&gt;[Final]&lt;/code&gt;, leaving other tags intact.</source>
        <translation>タグ入力欄に特定のタグを入力するとそのタグのみ削除します。&lt;b&gt;入力欄を空にすると、ファイル名のすべての&lt;code&gt;[ ]&lt;/code&gt;形式タグを削除します。&lt;/b&gt;&lt;br&gt;&lt;br&gt;例）&lt;code&gt;最終&lt;/code&gt;と入力 → &lt;code&gt;[最終]&lt;/code&gt;のみ削除、他のタグはそのまま</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="215" />
        <source>Add Tags</source>
        <translation>タグ追加</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="216" />
        <source>Choose the tag to add and its position (&lt;b&gt;front&lt;/b&gt; or &lt;b&gt;back&lt;/b&gt; of the filename) in the right panel. If the tag already exists, it will not be added again.</source>
        <translation>右パネルで追加するタグと挿入位置（ファイル名の&lt;b&gt;前&lt;/b&gt;/&lt;b&gt;後&lt;/b&gt;）を選択します。同じタグが既に存在する場合は重複追加されません。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="217" />
        <source>Remove Leading Zeros</source>
        <translation>先頭0削除</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="218" />
        <source>Automatically removes leading zeros from file names (001 → 1, 007 → 7). &lt;b&gt;Numbers connected by hyphens, such as dates, are automatically protected.&lt;/b&gt;</source>
        <translation>ファイル名先頭の不要な0を自動削除します（001 → 1、007 → 7）。&lt;b&gt;ハイフンでつながれた日付形式の数字は自動的に保護されます。&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="219" />
        <source>Meeting notes 001.docx</source>
        <translation>会議録 001.docx</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="219" />
        <source>Meeting notes 1.docx</source>
        <translation>会議録 1.docx</translation>
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
        <translation>2024-01-01 日記.txt  ← 保護、変更なし</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="222" />
        <source>&lt;b&gt;File renaming can be undone once with [Undo] immediately after applying.&lt;/b&gt; However, the undo data is lost if you run another task or close the window. Always verify with &lt;code&gt;[Preview]&lt;/code&gt; before clicking &lt;code&gt;[Apply]&lt;/code&gt;.</source>
        <translation>&lt;b&gt;ファイル名変更後、[元に戻す]で一度だけ復元できます。&lt;/b&gt;ただし、新しい作業を実行したりウィンドウを閉じると復元データが消えます。&lt;code&gt;[プレビュー]&lt;/code&gt;で必ず確認してから&lt;code&gt;[適用]&lt;/code&gt;してください。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="226" />
        <source>Batch Renamer</source>
        <translation>Batch Renamer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="227" />
        <source>Rename folders and files in bulk</source>
        <translation>フォルダ・ファイルを一括リネームします</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="228" />
        <source>Rename subfolders or files using pattern-based rules. Supports 'Smart Extract' (auto-detect) and 'Sequential Number' (manual) modes.</source>
        <translation>サブフォルダまたはファイルをパターンに基づいて一括でリネームします。番号を自動認識する「スマート抽出」と番号を直接指定する「連番」の2方式に対応しています。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="230" />
        <source>Select &lt;b&gt;[Folder Rename]&lt;/b&gt; or &lt;b&gt;[File Rename]&lt;/b&gt; from the top tab first.</source>
        <translation>上部タブから&lt;b&gt;[フォルダ名変更]&lt;/b&gt;または&lt;b&gt;[ファイル名変更]&lt;/b&gt;を先に選択してください。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="231" />
        <source>&lt;b&gt;Select target folder&lt;/b&gt; — Use &lt;code&gt;[📂 Select Folder]&lt;/code&gt; or drag and drop to specify the &lt;b&gt;parent folder&lt;/b&gt;. The folder itself is not changed — only its &lt;b&gt;contents&lt;/b&gt; are renamed.</source>
        <translation>&lt;b&gt;対象フォルダ指定&lt;/b&gt; — &lt;code&gt;[📂 フォルダ選択]&lt;/code&gt;またはドラッグ＆ドロップで&lt;b&gt;上位フォルダ&lt;/b&gt;を指定します。指定したフォルダ自体は変更されず、&lt;b&gt;その中の下位項目のみ&lt;/b&gt;名前が変わります。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="232" />
        <source>&lt;b&gt;Select method&lt;/b&gt; — Choose 'Smart Extract' or 'Sequential Number' in the right panel.</source>
        <translation>&lt;b&gt;方式選択&lt;/b&gt; — 右パネルで「スマート抽出」または「連番」を選択します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="233" />
        <source>&lt;b&gt;Preview&lt;/b&gt; — Click &lt;code&gt;[Preview]&lt;/code&gt; to review changes. Conflicts are highlighted in the table.</source>
        <translation>&lt;b&gt;プレビュー確認&lt;/b&gt; — &lt;code&gt;[プレビュー]&lt;/code&gt;をクリックして変更結果を確認します。名前が競合する場合は表で警告が表示されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="234" />
        <source>&lt;b&gt;Rename&lt;/b&gt; — Click &lt;code&gt;[Rename]&lt;/code&gt;. You can undo once with &lt;code&gt;[Undo]&lt;/code&gt; immediately after.</source>
        <translation>&lt;b&gt;名前変更実行&lt;/b&gt; — &lt;code&gt;[名前変更実行]&lt;/code&gt;をクリックします。実行直後に&lt;code&gt;[元に戻す]&lt;/code&gt;で一度だけ復元できます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="236" />
        <source>🔍 Smart Extract</source>
        <translation>🔍 スマート抽出</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="237" />
        <source>Automatically extracts numbers from existing names and reconstructs them.&lt;br&gt;&lt;br&gt;&lt;b&gt;Common prefix handling&lt;/b&gt; — Auto-detect / Manual entry / Keep as-is.&lt;br&gt;&lt;b&gt;Prefix · Suffix&lt;/b&gt; — Text to add before or after the reconstructed name.</source>
        <translation>既存の名前から番号を自動抽出して再構成します。&lt;br&gt;&lt;br&gt;&lt;b&gt;共通接頭辞の処理&lt;/b&gt; — 自動検出 / 手動指定 / そのまま維持。&lt;br&gt;&lt;b&gt;接頭辞・接尾辞&lt;/b&gt; — 再構成された名前の前後に追加するテキストを入力します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="238" />
        <source>🔢 Sequential Number</source>
        <translation>🔢 連番</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="239" />
        <source>Assigns numbers in sequence from first to last. All options are set manually.&lt;br&gt;&lt;br&gt;&lt;b&gt;Start number&lt;/b&gt; — Choose 00 or 01. &lt;b&gt;Digits&lt;/b&gt; — Auto or fixed 2/3/4. &lt;b&gt;Prefix · Suffix&lt;/b&gt; — Text around the number. &lt;b&gt;Name preservation&lt;/b&gt; — 'Number only' or 'Number + original name'. &lt;b&gt;Number reset&lt;/b&gt; — 'Continuous' or 'Reset per group'.</source>
        <translation>最初から最後まで順番に番号を付けます。すべてのオプションを手動で設定します。&lt;br&gt;&lt;br&gt;&lt;b&gt;開始番号&lt;/b&gt; — 00または01から選択。&lt;b&gt;桁数&lt;/b&gt; — 自動または2・3・4桁固定。&lt;b&gt;接頭辞・接尾辞&lt;/b&gt; — 番号の前後に付けるテキスト。&lt;b&gt;名前の保持&lt;/b&gt; — 「番号のみ」または「番号+元の名前」。&lt;b&gt;番号リセット&lt;/b&gt; — 「全体連番」または「グループごとにリセット」。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="240" />
        <source>File extensions are always preserved automatically.</source>
        <translation>ファイル名変更では拡張子が常に自動保持されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="241" />
        <source>Dragging a folder recursively scans subfolders and builds groups automatically.</source>
        <translation>フォルダをドラッグすると、サブフォルダまで再帰的にスキャンしてグループを自動構成します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="242" />
        <source>Explorer windows open to the target folder are automatically closed before renaming and reopened when done.</source>
        <translation>名前変更の実行前に対象フォルダを開いているエクスプローラーウィンドウは自動的に閉じられ、完了後に自動で再度開かれます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="243" />
        <source>&lt;b&gt;Renaming takes effect immediately.&lt;/b&gt; You can undo once with &lt;code&gt;[Undo]&lt;/code&gt;, but the data is lost when you run another task or close the window.</source>
        <translation>&lt;b&gt;名前変更は即時に適用されます。&lt;/b&gt;実行直後は&lt;code&gt;[元に戻す]&lt;/code&gt;で復元できますが、新しい作業を実行したりウィンドウを閉じると復元データが消えます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="244" />
        <source>The specified parent folder itself is not modified. Only its contents are renamed.</source>
        <translation>指定した上位フォルダ自体は変更されません。下位項目のみが対象です。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="248" />
        <source>Text Fixer</source>
        <translation>Text Fixer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="249" />
        <source>Repair line breaks in OCR and e-book text</source>
        <translation>OCR・電子書籍テキストの改行を校正します</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="250" />
        <source>Text extracted from PDFs or EPUBs often has forced line breaks at page width. Text Fixer intelligently restores paragraph structure.</source>
        <translation>PDFやEPUBから抽出したテキストはページ幅で強制改行される問題があります。Text Fixerはこれを自動復元して段落構造を整理します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="252" />
        <source>&lt;b&gt;Input methods&lt;/b&gt; — Drag a .txt file onto the drop zone, use &lt;code&gt;[📂 Open File]&lt;/code&gt;, or paste text directly into the left 'Original Text' pane.</source>
        <translation>&lt;b&gt;テキスト入力方法&lt;/b&gt; — .txtファイルをドロップゾーンにドラッグ、&lt;code&gt;[📂 ファイルを開く]&lt;/code&gt;、または左の「元のテキスト」欄に直接貼り付け。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="253" />
        <source>&lt;b&gt;Load text&lt;/b&gt; — Open a file or paste text into the left pane.</source>
        <translation>&lt;b&gt;テキスト入力&lt;/b&gt; — ファイルを読み込むか、左のテキスト欄に貼り付けます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="254" />
        <source>&lt;b&gt;Choose options&lt;/b&gt; — Combine the four options as needed. Start with &lt;b&gt;① + ④&lt;/b&gt; for most cases.</source>
        <translation>&lt;b&gt;オプション選択&lt;/b&gt; — 4つのオプションを必要に応じて組み合わせます。最初は&lt;b&gt;① + ④&lt;/b&gt;の組み合わせから始めてみてください。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="255" />
        <source>&lt;b&gt;&lt;code&gt;[✦ Fix]&lt;/code&gt;&lt;/b&gt; — Compare the left (original) and right (result) panes side by side.</source>
        <translation>&lt;b&gt;&lt;code&gt;[✦ 修正実行]&lt;/code&gt;&lt;/b&gt; — 左（元のテキスト）と右（結果）を並べて比較しながら確認してください。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="256" />
        <source>&lt;b&gt;Save&lt;/b&gt; — Click &lt;code&gt;[Save ▼]&lt;/code&gt; if satisfied. If not, use &lt;code&gt;[Undo]&lt;/code&gt; to restore the original and retry with different options.</source>
        <translation>&lt;b&gt;保存&lt;/b&gt; — 結果が良ければ&lt;code&gt;[保存 ▼]&lt;/code&gt;をクリックします。気に入らない場合は&lt;code&gt;[元に戻す]&lt;/code&gt;で復元してオプションを変えて再試行してください。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="258" />
        <source>① Merge Line Breaks (blank-line basis)</source>
        <translation>① 改行結合（空行基準）</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="259" />
        <source>Splits text into paragraphs by blank lines, then merges forced line breaks within each paragraph. &lt;b&gt;Not merged&lt;/b&gt; — Lines ending with period, exclamation, question mark, or quote; and divider lines like &lt;code&gt;───&lt;/code&gt;, &lt;code&gt;===&lt;/code&gt;, &lt;code&gt;★★★&lt;/code&gt;. This is the core option for fixing PDF/EPUB text. Enable it first in most cases.</source>
        <translation>空行で段落を区切り、段落内で強制的に折り返された行を1つにつなげます。&lt;b&gt;つなげない場合&lt;/b&gt; — 句点・感嘆符・疑問符・引用符などで終わる行、および&lt;code&gt;───&lt;/code&gt;・&lt;code&gt;===&lt;/code&gt;・&lt;code&gt;★★★&lt;/code&gt;のような区切り線はつなげません。PDF・EPUBテキスト校正の核心オプションです。ほとんどの場合、最初にオンにしてください。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="260" />
        <source>② Auto Paragraph Split (max N chars)</source>
        <translation>② 自動段落分割（最大N文字）</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="261" />
        <source>After merging, splits overly long lines at sentence boundaries based on a character limit. Short sentences are grouped together within the limit. Default: 100 chars. Try 150-200 for long-sentence manuscripts.</source>
        <translation>①で結合後に長くなりすぎた行を文章境界でN文字基準に分割します。短い文章同士はN文字以内で自動的にまとめられます。デフォルト100文字。長い文が続く場合は150〜200文字に増やしてみてください。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="262" />
        <source>③ Insert Blank Line Between Sentences</source>
        <translation>③ 文ごとに空行を挿入</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="263" />
        <source>Inserts a blank line after lines ending with period/quote, or before dialogue. Useful for improving readability in dialogue-heavy text.</source>
        <translation>句点・引用符で終わる行の後、またはセリフの前に空行を自動挿入します。会話が多いテキストで段落の読みやすさを高めるときに使います。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="264" />
        <source>④ Reduce Excessive Blank Lines (max N lines)</source>
        <translation>④ 過剰な空行を削減（最大N行）</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="265" />
        <source>Collapses consecutive blank lines to a maximum of N. Default 1 is recommended. Use 2 for multi-section documents.</source>
        <translation>連続する空行を最大N行に削減します。デフォルト1行推奨。複数セクションがある文書は2行に設定してください。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="267" />
        <source>&lt;b&gt;Recommended combinations&lt;/b&gt; — PDF/EPUB text: &lt;b&gt;① + ④&lt;/b&gt; / Dialogue-heavy text: &lt;b&gt;① + ③&lt;/b&gt; / OCR output with long paragraphs: &lt;b&gt;① + ② + ④&lt;/b&gt;</source>
        <translation>&lt;b&gt;推奨の組み合わせ&lt;/b&gt; — PDF・EPUBテキスト校正：&lt;b&gt;① + ④&lt;/b&gt; / 会話中心のテキスト：&lt;b&gt;① + ③&lt;/b&gt; / OCR結果・長い段落の整理：&lt;b&gt;① + ② + ④&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="268" />
        <source>&lt;b&gt;Save options&lt;/b&gt; — &lt;b&gt;Save as [Fixed] beside original&lt;/b&gt;: keeps original, saves corrected version as &lt;code&gt;[Fixed]filename.txt&lt;/code&gt; / &lt;b&gt;Save As&lt;/b&gt;: choose location and name / &lt;b&gt;Undo&lt;/b&gt;: restores the pre-fix text in the left pane (available once after running Fix)</source>
        <translation>&lt;b&gt;保存方式&lt;/b&gt; — &lt;b&gt;元の場所に[Fixed]タグ付きで保存&lt;/b&gt;：元のファイルはそのまま、校正版を&lt;code&gt;[Fixed]ファイル名.txt&lt;/code&gt;として保存 / &lt;b&gt;名前を付けて保存&lt;/b&gt;：場所とファイル名を直接指定 / &lt;b&gt;元に戻す&lt;/b&gt;：修正前の元のテキストを左ペインに復元（修正実行後1回のみ可能）</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="269" />
        <source>🟡 &lt;b&gt;Yellow lines&lt;/b&gt; = lines merged from multiple / 🟠 &lt;b&gt;Orange lines&lt;/b&gt; = blank line removed. Highlighting is skipped for files over 3,000 lines.</source>
        <translation>🟡 &lt;b&gt;黄色の行&lt;/b&gt; = 複数行が結合された部分 / 🟠 &lt;b&gt;オレンジの行&lt;/b&gt; = 空行が削除された位置。3,000行以上の大容量ファイルはハイライトが省略されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="270" />
        <source>The status bar at the bottom shows &lt;b&gt;merge count, blank lines removed, original line count, and final line count&lt;/b&gt;.</source>
        <translation>下部の統計バーで&lt;b&gt;結合回数・空行削除数・元の行数・最終行数&lt;/b&gt;を確認できます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="271" />
        <source>Press &lt;b&gt;Ctrl+F&lt;/b&gt; to search within the source and result text. Enter jumps to the next match, Shift+Enter to the previous.</source>
        <translation>&lt;b&gt;Ctrl+F&lt;/b&gt;で原文・修正文のテキスト検索ができます。Enterで次へ、Shift+Enterで前へ移動します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="272" />
        <source>Files are always saved as &lt;b&gt;UTF-8&lt;/b&gt;. Convert the encoding separately if you need to preserve the original (e.g. EUC-KR).</source>
        <translation>保存は常に&lt;b&gt;UTF-8&lt;/b&gt;エンコードで行われます。元のエンコード（EUC-KRなど）を維持する必要がある場合は別途変換してください。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="274" />
        <source>&lt;b&gt;Partially corrupted files&lt;/b&gt; — Files with damaged bytes can still be opened. Corrupted characters are shown as &lt;code&gt;�&lt;/code&gt; (U+FFFD), and the status bar shows a &lt;b&gt;⚠&lt;/b&gt; icon with a 'Partial encoding failure' warning.</source>
        <translation>&lt;b&gt;部分的に破損したファイルの処理&lt;/b&gt; — 一部のバイトが破損したファイルも開けます。破損した文字は&lt;code&gt;�&lt;/code&gt;（U+FFFD）で表示され、ステータスバーに&lt;b&gt;⚠&lt;/b&gt;アイコンと「部分エンコーディング失敗」の警告が表示されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="275" />
        <source>Text Fixer is optimized for &lt;b&gt;detailed inspection of a single file&lt;/b&gt;. Open corrupted files to see exactly where the damage is, edit those spots manually, or decide whether to re-acquire the original.</source>
        <translation>Text Fixerは&lt;b&gt;単一ファイルの精密レビュー&lt;/b&gt;に最適化されています。破損ファイルを開いて壊れた位置を直接確認し、その箇所を手動編集したり、原本の再取得を判断できます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="276" />
        <source>Files with tens of thousands of corrupted characters rarely recover well. Re-downloading from the source is usually better. Bulk Fixer automatically skips such files to protect the originals.</source>
        <translation>数万文字以上の大量破損があるファイルは、補正しても品質回復が困難です。まず原本元からの再ダウンロードを検討してください。Bulk Fixerではこのようなファイルを自動スキップして原本を保護します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="280" />
        <source>Bulk Fixer</source>
        <translation>Bulk Fixer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="281" />
        <source>Batch-correct line breaks across multiple TXT files</source>
        <translation>複数のTXTファイルの改行を一括補正します</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="282" />
        <source>Applies the Text Fixer correction engine to many files at once. Ideal for cleaning up batches of TXT files extracted from OCR or e-books.</source>
        <translation>Text Fixerの補正エンジンを複数ファイルに一括適用します。OCRや電子書籍から抽出したTXTファイルをまとめて整理する際に使用します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="284" />
        <source>&lt;b&gt;Add files&lt;/b&gt; — Use &lt;code&gt;[📄 Add files]&lt;/code&gt; or &lt;code&gt;[📂 Add folder]&lt;/code&gt; to load TXT files. You can also drag and drop folders directly onto the file list to recursively collect &lt;code&gt;.txt&lt;/code&gt; files.</source>
        <translation>&lt;b&gt;ファイル追加&lt;/b&gt; — &lt;code&gt;[📄 ファイル追加]&lt;/code&gt;または&lt;code&gt;[📂 フォルダ追加]&lt;/code&gt;でTXTファイルを読み込みます。ファイル一覧にフォルダを直接ドラッグ＆ドロップしても、サブフォルダの&lt;code&gt;.txt&lt;/code&gt;ファイルが再帰的に収集されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="285" />
        <source>&lt;b&gt;Set options&lt;/b&gt; — Choose the merge mode (Auto / Korean / English) and correction options in the right panel. Use the &lt;b&gt;Preset&lt;/b&gt; dropdown to quickly apply "General document" or "Book / Novel" settings.</source>
        <translation>&lt;b&gt;オプション選択&lt;/b&gt; — 右パネルで結合モード（自動/韓国語/英語）と4つの補正オプションを設定します。&lt;b&gt;プリセット&lt;/b&gt;から「一般文書」または「書籍・小説」を選ぶとオプションが一括設定されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="286" />
        <source>&lt;b&gt;Save settings&lt;/b&gt; — Specify an output folder, or leave it empty to save as &lt;code&gt;[Fixed]filename.txt&lt;/code&gt; beside each original file. Enable &lt;b&gt;Preserve folder structure&lt;/b&gt; to recreate the original subfolder hierarchy inside the output folder.</source>
        <translation>&lt;b&gt;保存設定&lt;/b&gt; — 出力フォルダを指定するか、空欄のままにすると元ファイルと同じ場所に&lt;code&gt;[Fixed]ファイル名.txt&lt;/code&gt;として保存されます。&lt;b&gt;フォルダ構造を維持&lt;/b&gt;にチェックを入れると、出力フォルダ内に元のサブフォルダ構造が再現されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="287" />
        <source>&lt;b&gt;Click &lt;code&gt;[▶ Start batch fix]&lt;/code&gt;&lt;/b&gt; — Progress is shown during processing; a summary of successes and failures is displayed on completion.</source>
        <translation>&lt;b&gt;&lt;code&gt;[▶ 一括補正開始]&lt;/code&gt;をクリック&lt;/b&gt; — 処理中は進捗が表示され、完了後に成功・失敗ファイル数が通知されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="288" />
        <source>Click any file in the list to preview the corrected result in the preview panel on the right.</source>
        <translation>ファイル一覧の項目をクリックすると、右のプレビューパネルで補正結果を確認できます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="289" />
        <source>The default output folder is &lt;code&gt;Output/&lt;/code&gt;. You can change it globally in ⚙ Settings or per-tab individually. The folder opens automatically after saving.</source>
        <translation>デフォルトの出力フォルダは&lt;code&gt;Output/&lt;/code&gt;です。⚙設定でグローバルに変更するか、各タブで個別に指定できます。保存完了後に自動で開きます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="290" />
        <source>Only TXT files are supported. Convert DOCX, PDF, etc. to TXT with Text Converter first.</source>
        <translation>TXTファイルのみ対応です。DOCX・PDFなどは先にText ConverterでTXTに変換してください。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="292" />
        <source>&lt;b&gt;Automatic corruption tiering&lt;/b&gt; — Bulk Fixer classifies partially corrupted files into three tiers based on damage severity:&lt;br&gt;• &lt;b&gt;Tier 1&lt;/b&gt; (1–500 damaged chars): Fixed + report generated&lt;br&gt;• &lt;b&gt;Tier 2&lt;/b&gt; (501–5,000 damaged chars): Fixed + report generated (review recommended)&lt;br&gt;• &lt;b&gt;Tier 3&lt;/b&gt; (5,001+ damaged chars): &lt;b&gt;Automatically skipped (original preserved)&lt;/b&gt; + report only</source>
        <translation>&lt;b&gt;エンコーディング破損ファイルの自動分類&lt;/b&gt; — Bulk Fixerは部分破損ファイルを検出すると、破損の程度に応じて3段階に分けて処理します：&lt;br&gt;• &lt;b&gt;Tier 1&lt;/b&gt;（1〜500文字破損）：補正後にレポート生成&lt;br&gt;• &lt;b&gt;Tier 2&lt;/b&gt;（501〜5,000文字破損）：補正後にレポート生成（レビュー推奨）&lt;br&gt;• &lt;b&gt;Tier 3&lt;/b&gt;（5,001文字以上）：&lt;b&gt;自動スキップ（原本保護）&lt;/b&gt; + レポートのみ生成</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="293" />
        <source>Reports are created next to the fixed output as &lt;code&gt;{original_filename}.encoding_report.txt&lt;/code&gt;, detailing damaged line/column positions for up to 5,000 entries.</source>
        <translation>レポートファイルは&lt;code&gt;{元ファイル名}.encoding_report.txt&lt;/code&gt;の形で補正版の隣に生成されます。どの行・どの列が破損したかを最大5,000件まで詳細記録します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="294" />
        <source>Files skipped as Tier 3 should be &lt;b&gt;individually reviewed in Text Fixer&lt;/b&gt;. Heavy corruption usually means wrong encoding detection or a corrupted source, so re-acquiring the original is often better than forcing correction.</source>
        <translation>Tier 3でスキップされたファイルは&lt;b&gt;Text Fixerで個別にレビュー&lt;/b&gt;してください。大量破損はエンコーディング誤検出か原本ファイル自体の問題である可能性が高く、一括補正よりも原本の再取得が良策です。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="298" />
        <source>Shortcuts &amp; Tips</source>
        <translation>ショートカット &amp; Tips</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="299" />
        <source>Use keyboard shortcuts to navigate quickly. All shortcuts can be customized in Settings.</source>
        <translation>キーボードショートカットで素早く操作できます。設定画面でカスタマイズ可能です。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="301" />
        <source>Go to Text Merger</source>
        <translation>Text Mergerへ移動</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="302" />
        <source>Go to Text Converter</source>
        <translation>Text Converterへ移動</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="303" />
        <source>Go to Tag Editor</source>
        <translation>Tag Editorへ移動</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="304" />
        <source>Go to Batch Renamer</source>
        <translation>Batch Renamerへ移動</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="305" />
        <source>Go to Text Fixer</source>
        <translation>Text Fixerへ移動</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="306" />
        <source>Go to Bulk Fixer</source>
        <translation>Bulk Fixerへ移動</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="307" />
        <source>Search text in Text Fixer</source>
        <translation>Text Fixerでテキスト検索</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="308" />
        <source>⚙ button (top right)</source>
        <translation>⚙ ボタン(右上)</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="308" />
        <source>Open Settings — change theme, language, and shortcuts</source>
        <translation>設定を開く — テーマ・言語・ショートカットを変更可能</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="309" />
        <source>Settings (theme, language, shortcuts) are saved automatically on exit and restored on next launch.</source>
        <translation>設定（テーマ・言語・ショートカット）は終了時に自動保存され、次回起動時に復元されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="310" />
        <source>&lt;b&gt;Drag and drop&lt;/b&gt; is supported in all tabs. Dropping a folder adds all supported files inside it at once.</source>
        <translation>すべてのタブで&lt;b&gt;ドラッグ＆ドロップ&lt;/b&gt;でファイルを読み込めます。フォルダをドロップすると対応ファイルが一括追加されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="311" />
        <source>🔋 &lt;b&gt;Sleep Prevention&lt;/b&gt; — While Text Merger, Text Converter, Text Fixer, or Bulk Fixer is running, Windows sleep mode is automatically blocked. It is released immediately when the task completes or an error occurs. Screen lock is unaffected.</source>
        <translation>🔋 &lt;b&gt;スリープ防止&lt;/b&gt; — Text Merger・Text Converter・Text Fixer・Bulk Fixerでタスク実行中はWindowsのスリープが自動でブロックされます。完了またはエラー発生時に即座に解除されます。画面ロックはスリープとは無関係で、処理中も通常どおり動作します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="315" />
        <source>File creation notice</source>
        <translation>生成ファイル案内</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="316" />
        <source>Files and folders created automatically during use</source>
        <translation>プログラム使用中に自動生成されるファイルとフォルダ</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="317" />
        <source>File Nexus Suite automatically creates the following items in the program folder for settings storage, default output, and error logging.</source>
        <translation>File Nexus Suiteは設定保存、デフォルト出力、エラー記録のため、実行ファイルと同じフォルダに以下を自動生成します。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="319" />
        <source>&lt;b&gt;FileNexusSuite.json&lt;/b&gt; — Stores your theme, language, shortcuts, and tab settings. Saved on exit, restored on next launch.</source>
        <translation>&lt;b&gt;FileNexusSuite.json&lt;/b&gt; — テーマ・言語・ショートカット・各タブ設定を保存する環境設定ファイルです。終了時に自動保存され、次回起動時に復元されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="320" />
        <source>&lt;b&gt;Output/&lt;/b&gt; — Default output folder for Text Converter, Bulk Fixer, and Text Fixer. Created automatically on first launch. Change the location globally in ⚙ Settings; the folder opens automatically after saving.</source>
        <translation>&lt;b&gt;Output/&lt;/b&gt; — Text Converter、Bulk Fixer、Text Fixerのデフォルト出力フォルダです。初回起動時に自動生成されます。⚙設定で場所をグローバルに変更でき、保存完了時に自動で開きます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="321" />
        <source>&lt;b&gt;logs/crash_*.log&lt;/b&gt; — Crash logs generated when an unexpected error occurs. Only the 3 most recent logs are kept; older ones are deleted automatically.</source>
        <translation>&lt;b&gt;logs/crash_*.log&lt;/b&gt; — 予期しないエラー発生時に自動生成されるクラッシュログです。最新3件のみ保持され、古いファイルは自動削除されます。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="322" />
        <source>&lt;b&gt;_internal/&lt;/b&gt; — Created automatically in folder-style exe builds. Contains the Python runtime. &lt;b&gt;Deleting it will prevent the program from running.&lt;/b&gt;</source>
        <translation>&lt;b&gt;_internal/&lt;/b&gt; — フォルダ形式のexeビルド時に自動生成されるPythonランタイムフォルダです。&lt;b&gt;削除するとプログラムが起動できなくなります。&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="323" />
        <source>You can safely delete any of these files or folders. Required items will be recreated automatically on the next launch.</source>
        <translation>これらのファイルやフォルダは直接削除しても問題ありません。次回起動時に必要なものは自動的に再生成されます。</translation>
    </message>
<message>
        <location filename="../fns_help.py" line="132" />
        <source>💡  Help — File Nexus Suite v%1</source>
        <translation>💡  ヘルプ — File Nexus Suite v%1</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="532" />
        <source>💡  Help</source>
        <translation>💡  ヘルプ</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="582" />
        <source>Close</source>
        <translation>閉じる</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="601" />
        <source>About</source>
        <translation>概要</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="144" />
        <source>File Nexus Suite is an integrated file utility for managing text, e-books, and media files. Text merging, EPUB conversion, file-name tag editing, batch renaming, line-break correction, and bulk fixing — six core features, all in one window.</source>
        <translation>File Nexus Suite はテキスト・電子書籍・メディアファイル作業に特化した統合ファイルツールです。テキスト結合、EPUB変換、ファイル名タグ編集、一括リネーム、改行校正、一括補正 — 6つの主要機能が1つのウィンドウにまとまっています。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="162" />
        <source>Text Merger</source>
        <translation>Text Merger</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="452" />
        <source>Native support</source>
        <translation>標準対応</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="453" />
        <source>Library required</source>
        <translation>ライブラリ要インストール</translation>
    </message>
</context></TS>