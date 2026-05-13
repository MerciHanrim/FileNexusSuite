<?xml version='1.0' encoding='utf-8'?>
<TS version="2.1" language="zh_CN" sourcelanguage="en">
<context><name>HelpDialog</name><message>
        <location filename="../fns_help.py" line="163" />
        <source>Merge multiple files into a single text file</source>
        <translation>将多个文件合并为一个文本文件</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="164" />
        <source>Combine files of the formats below into one text file in any order. DOCX, PDF, and XLSX require the respective libraries to be installed.</source>
        <translation>将以下格式的文件按您选择的顺序合并为一个文本文件。DOCX、PDF、XLSX需安装对应库后才能提取文本。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="167" />
        <source>&lt;b&gt;Add files&lt;/b&gt; — Click &lt;code&gt;[📄 Add Files]&lt;/code&gt; or drag and drop files onto the list. Unsupported formats are filtered out automatically.</source>
        <translation>&lt;b&gt;添加文件&lt;/b&gt; — 点击&lt;code&gt;[📄 添加文件]&lt;/code&gt;或将文件拖放到列表中。不支持的格式会自动过滤。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="168" />
        <source>&lt;b&gt;Set order&lt;/b&gt; — Drag items in the list or use &lt;code&gt;[Up]&lt;/code&gt; / &lt;code&gt;[Down]&lt;/code&gt; to set the merge order.</source>
        <translation>&lt;b&gt;调整顺序&lt;/b&gt; — 在列表中拖动或使用&lt;code&gt;[上移]&lt;/code&gt;/&lt;code&gt;[下移]&lt;/code&gt;设置合并顺序。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="169" />
        <source>&lt;b&gt;Set encoding&lt;/b&gt; — Select the &lt;b&gt;read encoding&lt;/b&gt; for each file via the combo box, and choose the &lt;b&gt;save encoding&lt;/b&gt; in the 'Save Settings' panel.</source>
        <translation>&lt;b&gt;设置编码&lt;/b&gt; — 从每个文件右侧的下拉框中选择&lt;b&gt;读取编码&lt;/b&gt;，在右侧「保存设置」面板中选择&lt;b&gt;保存编码&lt;/b&gt;。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="170" />
        <source>&lt;b&gt;File separator&lt;/b&gt; (optional) — Enable 'Insert File Separator' to automatically insert a divider line with the filename between each file.</source>
        <translation>&lt;b&gt;文件分隔线&lt;/b&gt;（可选）— 勾选「插入文件分隔线」后，合并时会在每个文件之间自动插入含文件名的分隔线。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="171" />
        <source>&lt;b&gt;Set save path&lt;/b&gt; (optional) — Click &lt;code&gt;[Set Path]&lt;/code&gt; to pre-select a save location. If not set, a save dialog will appear when you run the merge.</source>
        <translation>&lt;b&gt;指定保存路径&lt;/b&gt;（可选）— 点击&lt;code&gt;[指定路径]&lt;/code&gt;预先设置保存位置，执行时自动保存。未设置则在执行时弹出保存对话框。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="172" />
        <source>&lt;b&gt;&lt;code&gt;[▶ Merge &amp; Save]&lt;/code&gt;&lt;/b&gt; — Click to merge. The completion message shows a per-file encoding summary.</source>
        <translation>&lt;b&gt;&lt;code&gt;[▶ 合并保存]&lt;/code&gt;&lt;/b&gt; — 点击执行合并。完成消息中可查看各文件的编码摘要。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="174" />
        <source>&lt;b&gt;Auto encoding detection&lt;/b&gt; — If chardet is installed, encoding is detected automatically when files are added. If accuracy is low, select manually.</source>
        <translation>&lt;b&gt;编码自动检测&lt;/b&gt; — 安装chardet后，添加文件时将自动检测编码。准确度低时请从下拉框手动选择。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="175" />
        <source>&lt;b&gt;Save encoding guide&lt;/b&gt; — UTF-8: general use / UTF-8-BOM: prevents garbled text in Excel / EUC-KR·CP949: legacy Korean apps / UTF-16: special use / &lt;b&gt;Shift-JIS·GBK·Big5&lt;/b&gt;: Japanese / Chinese (Simplified·Traditional) legacy systems</source>
        <translation>&lt;b&gt;保存编码选择参考&lt;/b&gt; — UTF-8：通用推荐 / UTF-8-BOM：Excel中不乱码 / EUC-KR·CP949：韩语旧版程序兼容 / UTF-16：特殊用途 / &lt;b&gt;Shift-JIS·GBK·Big5&lt;/b&gt;：日文·中文（简体·繁体）旧版系统兼容</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="176" />
        <source>&lt;b&gt;Separator format&lt;/b&gt; — When enabled, the following line is inserted before each file: &lt;code&gt;───── ▶ filename.txt ──────&lt;/code&gt;</source>
        <translation>&lt;b&gt;分隔线格式&lt;/b&gt; — 启用后，每个文件前插入 &lt;code&gt;───── ▶ 文件名.txt ──────&lt;/code&gt; 格式的行。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="177" />
        <source>If a file fails to read, it is skipped and the rest are merged normally. Errors are shown in the completion message.</source>
        <translation>读取文件时若出现错误，仅跳过该文件，其余文件正常合并。错误内容显示在完成消息中。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="178" />
        <source>&lt;code&gt;[Undo]&lt;/code&gt; deletes the merged output file. &lt;b&gt;Original files are never modified.&lt;/b&gt;</source>
        <translation>&lt;code&gt;[撤销]&lt;/code&gt;按钮将删除合并的输出文件。&lt;b&gt;原始文件不会有任何修改。&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="182" />
        <source>Text Converter</source>
        <translation>Text Converter</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="183" />
        <source>Convert between TXT and EPUB formats</source>
        <translation>在TXT和EPUB格式之间转换</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="184" />
        <source>Convert TXT files into EPUB e-books, or extract text from EPUB files. Multiple files are converted automatically in sequence.</source>
        <translation>将TXT文件转换为EPUB电子书，或从EPUB中提取文本。添加多个文件后将按顺序自动批量转换。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="186" />
        <source>Select &lt;b&gt;[TXT → EPUB]&lt;/b&gt; or &lt;b&gt;[EPUB → TXT]&lt;/b&gt; at the top first.</source>
        <translation>请先选择顶部的&lt;b&gt;[TXT → EPUB]&lt;/b&gt;或&lt;b&gt;[EPUB → TXT]&lt;/b&gt;选项卡。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="187" />
        <source>&lt;b&gt;Add files&lt;/b&gt; — Click &lt;code&gt;[📄 Add Files]&lt;/code&gt; or drag and drop.</source>
        <translation>&lt;b&gt;添加文件&lt;/b&gt; — 点击&lt;code&gt;[📄 添加文件]&lt;/code&gt;或拖放。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="188" />
        <source>&lt;b&gt;TXT → EPUB settings&lt;/b&gt; — Enter &lt;b&gt;title, author, and language&lt;/b&gt; in the 'Book Info' panel and choose a &lt;b&gt;chapter splitting method&lt;/b&gt;.</source>
        <translation>&lt;b&gt;TXT → EPUB 设置&lt;/b&gt; — 在右侧「书籍信息」面板中输入&lt;b&gt;书名、作者、语言&lt;/b&gt;，并选择&lt;b&gt;章节分割方式&lt;/b&gt;。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="189" />
        <source>&lt;b&gt;EPUB → TXT settings&lt;/b&gt; — Configure chapter separator, title inclusion, blank line cleanup, and save encoding in the 'Conversion Options' panel.</source>
        <translation>&lt;b&gt;EPUB → TXT 设置&lt;/b&gt; — 在右侧「转换选项」面板中设置章节分隔线插入、章节标题包含、连续空行整理及保存编码。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="190" />
        <source>&lt;b&gt;Output folder&lt;/b&gt; (optional) — The default output folder is set in ⚙ Settings (default: &lt;code&gt;Output/&lt;/code&gt;). The folder opens automatically after saving.</source>
        <translation>&lt;b&gt;输出文件夹&lt;/b&gt;（可选）— 默认输出文件夹由⚙设置中的全局配置决定（默认：&lt;code&gt;Output/&lt;/code&gt;）。保存完成后输出文件夹会自动打开。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="191" />
        <source>&lt;b&gt;&lt;code&gt;[▶ Start Conversion]&lt;/code&gt;&lt;/b&gt; — The progress bar shows the status of each file.</source>
        <translation>&lt;b&gt;&lt;code&gt;[▶ 开始转换]&lt;/code&gt;&lt;/b&gt; — 多文件时进度条显示各文件的转换状态。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="193" />
        <source>TXT → EPUB Chapter Splitting</source>
        <translation>TXT → EPUB 章节分割方式</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="194" />
        <source>&lt;b&gt;Divider-based&lt;/b&gt; — Lines made of repeating symbols like &lt;code&gt;===&lt;/code&gt;, &lt;code&gt;---&lt;/code&gt;, or &lt;code&gt;★★★&lt;/code&gt; are treated as chapter boundaries.&lt;br&gt;&lt;br&gt;&lt;b&gt;3+ blank lines&lt;/b&gt; — Sections separated by 3 or more consecutive blank lines are treated as chapters.&lt;br&gt;&lt;br&gt;&lt;b&gt;Single chapter&lt;/b&gt; — The entire file is treated as one chapter.</source>
        <translation>&lt;b&gt;分隔线基准&lt;/b&gt; — 由&lt;code&gt;===&lt;/code&gt;、&lt;code&gt;---&lt;/code&gt;、&lt;code&gt;★★★&lt;/code&gt;等重复符号构成的行被识别为章节边界。&lt;br&gt;&lt;br&gt;&lt;b&gt;连续3行以上空行&lt;/b&gt; — 连续3行以上的空白段落被识别为章节边界。&lt;br&gt;&lt;br&gt;&lt;b&gt;全部作为一个章节&lt;/b&gt; — 将整个文件作为一个章节处理。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="195" />
        <source>EPUB → TXT Conversion Options</source>
        <translation>EPUB → TXT 转换选项</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="196" />
        <source>&lt;b&gt;Add chapter separator&lt;/b&gt; — Inserts a divider at each chapter boundary (default: on).&lt;br&gt;&lt;b&gt;Include chapter titles&lt;/b&gt; — Displays chapter titles from the EPUB below the divider (default: on).&lt;br&gt;&lt;b&gt;Clean up blank lines&lt;/b&gt; — Removes excessive blank lines generated during extraction (default: on).&lt;br&gt;&lt;b&gt;Save encoding&lt;/b&gt; — Choose the encoding for the output TXT file (default: UTF-8).</source>
        <translation>&lt;b&gt;添加章节分隔线&lt;/b&gt; — 在章节边界插入分隔线（默认：开启）。&lt;br&gt;&lt;b&gt;包含章节标题&lt;/b&gt; — 在分隔线下方显示EPUB中保存的章节标题（默认：开启）。&lt;br&gt;&lt;b&gt;整理连续空行&lt;/b&gt; — 整理提取过程中产生的多余空行（默认：开启）。&lt;br&gt;&lt;b&gt;保存编码&lt;/b&gt; — 选择输出TXT文件的编码（默认：UTF-8）。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="197" />
        <source>Setting an output folder keeps results separate from your originals, making it easy to collect all converted files in one place.</source>
        <translation>指定输出文件夹后，可在不修改原文件的情况下将转换结果集中保存在一处。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="198" />
        <source>Do not close the window while conversion is in progress — it may interrupt the process.</source>
        <translation>转换过程中请勿关闭窗口，否则可能中断转换。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="202" />
        <source>Tag Editor</source>
        <translation>Tag Editor</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="203" />
        <source>Add or remove tags from file names in bulk</source>
        <translation>批量添加或删除文件名中的标签</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="204" />
        <source>Batch-add or batch-remove bracket tags like &lt;code&gt;[Draft]&lt;/code&gt; or &lt;code&gt;[Final]&lt;/code&gt; from file names, and clean up leading zeros all at once.</source>
        <translation>批量添加或删除文件名中的&lt;code&gt;[临时]&lt;/code&gt;、&lt;code&gt;[最终]&lt;/code&gt;等括号标签，同时一次性整理多余的前导0。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="206" />
        <source>Choose &lt;b&gt;[Remove Tags]&lt;/b&gt;, &lt;b&gt;[Add Tags]&lt;/b&gt;, or &lt;b&gt;[Remove Leading Zeros]&lt;/b&gt; from the top tab first.</source>
        <translation>请根据操作类型从顶部选项卡选择&lt;b&gt;[删除标签]&lt;/b&gt;/&lt;b&gt;[添加标签]&lt;/b&gt;/&lt;b&gt;[删除前导零]&lt;/b&gt;。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="207" />
        <source>&lt;b&gt;Add files or folders&lt;/b&gt; — Use &lt;code&gt;[📄 Add Files]&lt;/code&gt; / &lt;code&gt;[📂 Add Folder]&lt;/code&gt; or drag and drop. Adding a folder reads files recursively based on the 'Include subfolders' option.</source>
        <translation>&lt;b&gt;添加文件或文件夹&lt;/b&gt; — 使用&lt;code&gt;[📄 添加文件]&lt;/code&gt;/&lt;code&gt;[📂 添加文件夹]&lt;/code&gt;或拖放添加目标。添加文件夹时，根据「包含子文件夹」选项递归读取文件。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="208" />
        <source>&lt;b&gt;Filter settings&lt;/b&gt; — Specify target extensions in the 'Filter' panel (comma-separated). Enable 'All extensions' to process all files regardless of type.</source>
        <translation>&lt;b&gt;筛选器设置&lt;/b&gt; — 在左下角「筛选器设置」面板中指定目标扩展名（逗号分隔）。勾选「所有扩展名」则不限类型处理所有文件。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="209" />
        <source>&lt;b&gt;Configure options&lt;/b&gt; — Set mode-specific options in the right panel.</source>
        <translation>&lt;b&gt;选项设置&lt;/b&gt; — 在右侧面板中设置各模式的选项。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="210" />
        <source>&lt;b&gt;Preview&lt;/b&gt; — Click &lt;code&gt;[Preview]&lt;/code&gt; to see the 'Before → After' table. &lt;b&gt;Always verify before applying.&lt;/b&gt;</source>
        <translation>&lt;b&gt;预览确认&lt;/b&gt; — 点击&lt;code&gt;[预览]&lt;/code&gt;查看「原文件名 → 修改后文件名」的对照表。&lt;b&gt;请务必确认后再应用。&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="211" />
        <source>&lt;b&gt;Apply&lt;/b&gt; — Click &lt;code&gt;[Apply]&lt;/code&gt; if the results look correct.</source>
        <translation>&lt;b&gt;应用&lt;/b&gt; — 结果正确后点击&lt;code&gt;[应用]&lt;/code&gt;。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="213" />
        <source>Remove Tags</source>
        <translation>删除标签</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="214" />
        <source>Enter a specific tag in the tag field to remove only that tag. &lt;b&gt;Leave the field empty to remove all &lt;code&gt;[ ]&lt;/code&gt; bracket tags.&lt;/b&gt;&lt;br&gt;&lt;br&gt;Example: entering &lt;code&gt;Final&lt;/code&gt; removes only &lt;code&gt;[Final]&lt;/code&gt;, leaving other tags intact.</source>
        <translation>在标签输入栏中输入特定标签，则仅删除该标签。&lt;b&gt;留空则删除文件名中所有&lt;code&gt;[ ]&lt;/code&gt;格式的标签。&lt;/b&gt;&lt;br&gt;&lt;br&gt;示例：输入&lt;code&gt;最终&lt;/code&gt; → 仅删除&lt;code&gt;[最终]&lt;/code&gt;，其余标签保留</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="215" />
        <source>Add Tags</source>
        <translation>添加标签</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="216" />
        <source>Choose the tag to add and its position (&lt;b&gt;front&lt;/b&gt; or &lt;b&gt;back&lt;/b&gt; of the filename) in the right panel. If the tag already exists, it will not be added again.</source>
        <translation>在右侧面板中选择要添加的标签和插入位置（文件名&lt;b&gt;前&lt;/b&gt;/&lt;b&gt;后&lt;/b&gt;）。若已存在相同标签，则不会重复添加。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="217" />
        <source>Remove Leading Zeros</source>
        <translation>删除前导零</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="218" />
        <source>Automatically removes leading zeros from file names (001 → 1, 007 → 7). &lt;b&gt;Numbers connected by hyphens, such as dates, are automatically protected.&lt;/b&gt;</source>
        <translation>自动删除文件名前端多余的0（001 → 1，007 → 7）。&lt;b&gt;由连字符连接的日期格式数字将自动受到保护。&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="219" />
        <source>Meeting notes 001.docx</source>
        <translation>会议记录 001.docx</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="219" />
        <source>Meeting notes 1.docx</source>
        <translation>会议记录 1.docx</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="220" />
        <source>Lecture 007 final.pdf</source>
        <translation>讲义资料 007 最终版.pdf</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="220" />
        <source>Lecture 7 final.pdf</source>
        <translation>讲义资料 7 最终版.pdf</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="221" />
        <source>2024-01-01 diary.txt</source>
        <translation>2024-01-01 日记.txt</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="221" />
        <source>2024-01-01 diary.txt  ← protected, no change</source>
        <translation>2024-01-01 日记.txt  ← 受保护，无变化</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="222" />
        <source>&lt;b&gt;File renaming can be undone once with [Undo] immediately after applying.&lt;/b&gt; However, the undo data is lost if you run another task or close the window. Always verify with &lt;code&gt;[Preview]&lt;/code&gt; before clicking &lt;code&gt;[Apply]&lt;/code&gt;.</source>
        <translation>&lt;b&gt;文件名修改后可立即使用[撤销]恢复一次。&lt;/b&gt;但执行新任务或关闭窗口后恢复数据将丢失。请务必先通过&lt;code&gt;[预览]&lt;/code&gt;确认后再点击&lt;code&gt;[应用]&lt;/code&gt;。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="226" />
        <source>Batch Renamer</source>
        <translation>Batch Renamer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="227" />
        <source>Rename folders and files in bulk</source>
        <translation>批量重命名文件夹和文件</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="228" />
        <source>Rename subfolders or files using pattern-based rules. Supports 'Smart Extract' (auto-detect) and 'Sequential Number' (manual) modes.</source>
        <translation>使用基于模式的规则批量重命名子文件夹或文件。支持自动识别编号的「智能提取」和手动指定编号的「顺序编号」两种方式。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="230" />
        <source>Select &lt;b&gt;[Folder Rename]&lt;/b&gt; or &lt;b&gt;[File Rename]&lt;/b&gt; from the top tab first.</source>
        <translation>请先从顶部选项卡选择&lt;b&gt;[文件夹重命名]&lt;/b&gt;或&lt;b&gt;[文件重命名]&lt;/b&gt;。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="231" />
        <source>&lt;b&gt;Select target folder&lt;/b&gt; — Use &lt;code&gt;[📂 Select Folder]&lt;/code&gt; or drag and drop to specify the &lt;b&gt;parent folder&lt;/b&gt;. The folder itself is not changed — only its &lt;b&gt;contents&lt;/b&gt; are renamed.</source>
        <translation>&lt;b&gt;指定目标文件夹&lt;/b&gt; — 使用&lt;code&gt;[📂 选择文件夹]&lt;/code&gt;或拖放指定&lt;b&gt;上级文件夹&lt;/b&gt;。指定的文件夹本身不会改变，只有&lt;b&gt;其内部的下级项目&lt;/b&gt;才会被重命名。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="232" />
        <source>&lt;b&gt;Select method&lt;/b&gt; — Choose 'Smart Extract' or 'Sequential Number' in the right panel.</source>
        <translation>&lt;b&gt;选择方式&lt;/b&gt; — 在右侧面板选择「智能提取」或「顺序编号」。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="233" />
        <source>&lt;b&gt;Preview&lt;/b&gt; — Click &lt;code&gt;[Preview]&lt;/code&gt; to review changes. Conflicts are highlighted in the table.</source>
        <translation>&lt;b&gt;预览确认&lt;/b&gt; — 点击&lt;code&gt;[预览]&lt;/code&gt;查看修改结果。名称冲突时表格中会显示警告。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="234" />
        <source>&lt;b&gt;Rename&lt;/b&gt; — Click &lt;code&gt;[Rename]&lt;/code&gt;. You can undo once with &lt;code&gt;[Undo]&lt;/code&gt; immediately after.</source>
        <translation>&lt;b&gt;执行重命名&lt;/b&gt; — 点击&lt;code&gt;[执行重命名]&lt;/code&gt;。执行后可立即使用&lt;code&gt;[撤销]&lt;/code&gt;恢复一次。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="236" />
        <source>🔍 Smart Extract</source>
        <translation>🔍 智能提取</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="237" />
        <source>Automatically extracts numbers from existing names and reconstructs them.&lt;br&gt;&lt;br&gt;&lt;b&gt;Common prefix handling&lt;/b&gt; — Auto-detect / Manual entry / Keep as-is.&lt;br&gt;&lt;b&gt;Prefix · Suffix&lt;/b&gt; — Text to add before or after the reconstructed name.</source>
        <translation>自动从现有名称中提取编号并重新构建。&lt;br&gt;&lt;br&gt;&lt;b&gt;公共前缀处理&lt;/b&gt; — 自动检测 / 手动指定 / 保留不变。&lt;br&gt;&lt;b&gt;前缀·后缀&lt;/b&gt; — 输入在重构名称前后添加的文本。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="238" />
        <source>🔢 Sequential Number</source>
        <translation>🔢 顺序编号</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="239" />
        <source>Assigns numbers in sequence from first to last. All options are set manually.&lt;br&gt;&lt;br&gt;&lt;b&gt;Start number&lt;/b&gt; — Choose 00 or 01. &lt;b&gt;Digits&lt;/b&gt; — Auto or fixed 2/3/4. &lt;b&gt;Prefix · Suffix&lt;/b&gt; — Text around the number. &lt;b&gt;Name preservation&lt;/b&gt; — 'Number only' or 'Number + original name'. &lt;b&gt;Number reset&lt;/b&gt; — 'Continuous' or 'Reset per group'.</source>
        <translation>从头到尾按顺序分配编号。所有选项均手动指定。&lt;br&gt;&lt;br&gt;&lt;b&gt;起始编号&lt;/b&gt; — 选择从00或01开始。&lt;b&gt;位数&lt;/b&gt; — 自动或固定2/3/4位。&lt;b&gt;前缀·后缀&lt;/b&gt; — 编号前后添加的文本。&lt;b&gt;名称保留&lt;/b&gt; — 「仅编号」或「编号+原名称」。&lt;b&gt;编号重置&lt;/b&gt; — 「全局连续」或「每组重置」。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="240" />
        <source>File extensions are always preserved automatically.</source>
        <translation>文件重命名时扩展名始终自动保留。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="241" />
        <source>Dragging a folder recursively scans subfolders and builds groups automatically.</source>
        <translation>拖放文件夹时会递归扫描子文件夹并自动构建分组。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="242" />
        <source>Explorer windows open to the target folder are automatically closed before renaming and reopened when done.</source>
        <translation>执行重命名前，打开目标文件夹的资源管理器窗口会自动关闭，完成后自动重新打开。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="243" />
        <source>&lt;b&gt;Renaming takes effect immediately.&lt;/b&gt; You can undo once with &lt;code&gt;[Undo]&lt;/code&gt;, but the data is lost when you run another task or close the window.</source>
        <translation>&lt;b&gt;重命名会立即生效。&lt;/b&gt;执行后可用&lt;code&gt;[撤销]&lt;/code&gt;恢复，但执行新任务或关闭窗口后恢复数据将丢失。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="244" />
        <source>The specified parent folder itself is not modified. Only its contents are renamed.</source>
        <translation>指定的上级文件夹本身不会被修改，仅对其下级项目进行操作。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="248" />
        <source>Text Fixer</source>
        <translation>Text Fixer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="249" />
        <source>Repair line breaks in OCR and e-book text</source>
        <translation>修复OCR和电子书文本的换行问题</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="250" />
        <source>Text extracted from PDFs or EPUBs often has forced line breaks at page width. Text Fixer intelligently restores paragraph structure.</source>
        <translation>从PDF或EPUB提取的文本常因页面宽度出现强制换行。Text Fixer可智能还原段落结构。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="252" />
        <source>&lt;b&gt;Input methods&lt;/b&gt; — Drag a .txt file onto the drop zone, use &lt;code&gt;[📂 Open File]&lt;/code&gt;, or paste text directly into the left 'Original Text' pane.</source>
        <translation>&lt;b&gt;文本输入方法&lt;/b&gt; — 将.txt文件拖到放置区，使用&lt;code&gt;[📂 打开文件]&lt;/code&gt;，或直接在左侧「原始文本」区域粘贴。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="253" />
        <source>&lt;b&gt;Load text&lt;/b&gt; — Open a file or paste text into the left pane.</source>
        <translation>&lt;b&gt;输入文本&lt;/b&gt; — 打开文件或将文本粘贴到左侧区域。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="254" />
        <source>&lt;b&gt;Choose options&lt;/b&gt; — Combine the four options as needed. Start with &lt;b&gt;① + ④&lt;/b&gt; for most cases.</source>
        <translation>&lt;b&gt;选择选项&lt;/b&gt; — 根据需要组合四个选项。大多数情况下先从&lt;b&gt;① + ④&lt;/b&gt;开始尝试。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="255" />
        <source>&lt;b&gt;&lt;code&gt;[✦ Fix]&lt;/code&gt;&lt;/b&gt; — Compare the left (original) and right (result) panes side by side.</source>
        <translation>&lt;b&gt;&lt;code&gt;[✦ 执行修复]&lt;/code&gt;&lt;/b&gt; — 左侧（原始）与右侧（结果）并排比较，确认修复效果。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="256" />
        <source>&lt;b&gt;Save&lt;/b&gt; — Click &lt;code&gt;[Save ▼]&lt;/code&gt; if satisfied. If not, use &lt;code&gt;[Undo]&lt;/code&gt; to restore the original and retry with different options.</source>
        <translation>&lt;b&gt;保存&lt;/b&gt; — 满意后点击&lt;code&gt;[保存 ▼]&lt;/code&gt;。不满意则使用&lt;code&gt;[撤销]&lt;/code&gt;还原，更换选项后重新尝试。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="258" />
        <source>① Merge Line Breaks (blank-line basis)</source>
        <translation>① 合并换行（以空行为基准）</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="259" />
        <source>Splits text into paragraphs by blank lines, then merges forced line breaks within each paragraph. &lt;b&gt;Not merged&lt;/b&gt; — Lines ending with period, exclamation, question mark, or quote; and divider lines like &lt;code&gt;───&lt;/code&gt;, &lt;code&gt;===&lt;/code&gt;, &lt;code&gt;★★★&lt;/code&gt;. This is the core option for fixing PDF/EPUB text. Enable it first in most cases.</source>
        <translation>以空行划分段落，然后合并段落内被强制折断的行。&lt;b&gt;不合并的情况&lt;/b&gt; — 以句号、感叹号、问号、引号结尾的行，以及&lt;code&gt;───&lt;/code&gt;、&lt;code&gt;===&lt;/code&gt;、&lt;code&gt;★★★&lt;/code&gt;等分隔线不参与合并。这是修复PDF/EPUB文本的核心选项，大多数情况下请先开启。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="260" />
        <source>② Auto Paragraph Split (max N chars)</source>
        <translation>② 自动段落分割（最多N字）</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="261" />
        <source>After merging, splits overly long lines at sentence boundaries based on a character limit. Short sentences are grouped together within the limit. Default: 100 chars. Try 150-200 for long-sentence manuscripts.</source>
        <translation>①合并后过长的行在句子边界按N字标准分割。较短的句子在N字范围内自动组合。默认100字。句子较长时可尝试调整为150~200字。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="262" />
        <source>③ Insert Blank Line Between Sentences</source>
        <translation>③ 在句子之间插入空行</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="263" />
        <source>Inserts a blank line after lines ending with period/quote, or before dialogue. Useful for improving readability in dialogue-heavy text.</source>
        <translation>在以句号/引号结尾的行后，或对话前自动插入空行。适用于提高对话较多的文本的可读性。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="264" />
        <source>④ Reduce Excessive Blank Lines (max N lines)</source>
        <translation>④ 减少过多空行（最多N行）</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="265" />
        <source>Collapses consecutive blank lines to a maximum of N. Default 1 is recommended. Use 2 for multi-section documents.</source>
        <translation>将连续空行压缩为最多N行。默认1行。多节结构的文档建议设为2行。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="267" />
        <source>&lt;b&gt;Recommended combinations&lt;/b&gt; — PDF/EPUB text: &lt;b&gt;① + ④&lt;/b&gt; / Dialogue-heavy text: &lt;b&gt;① + ③&lt;/b&gt; / OCR output with long paragraphs: &lt;b&gt;① + ② + ④&lt;/b&gt;</source>
        <translation>&lt;b&gt;推荐组合&lt;/b&gt; — PDF/EPUB文本修复：&lt;b&gt;① + ④&lt;/b&gt; / 对话为主的文本：&lt;b&gt;① + ③&lt;/b&gt; / OCR结果·长段落整理：&lt;b&gt;① + ② + ④&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="268" />
        <source>&lt;b&gt;Save options&lt;/b&gt; — &lt;b&gt;Save as [Fixed] beside original&lt;/b&gt;: keeps original, saves corrected version as &lt;code&gt;[Fixed]filename.txt&lt;/code&gt; / &lt;b&gt;Save As&lt;/b&gt;: choose location and name / &lt;b&gt;Undo&lt;/b&gt;: restores the pre-fix text in the left pane (available once after running Fix)</source>
        <translation>&lt;b&gt;保存方式&lt;/b&gt; — &lt;b&gt;在原位置以[Fixed]标签保存&lt;/b&gt;：保留原文件，修复版另存为&lt;code&gt;[Fixed]文件名.txt&lt;/code&gt; / &lt;b&gt;另存为&lt;/b&gt;：手动指定位置和文件名 / &lt;b&gt;撤销&lt;/b&gt;：将修复前的原始文本还原到左侧窗格（执行修复后可使用一次）</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="269" />
        <source>🟡 &lt;b&gt;Yellow lines&lt;/b&gt; = lines merged from multiple / 🟠 &lt;b&gt;Orange lines&lt;/b&gt; = blank line removed. Highlighting is skipped for files over 3,000 lines.</source>
        <translation>🟡 &lt;b&gt;黄色行&lt;/b&gt; = 多行合并为一行 / 🟠 &lt;b&gt;橙色行&lt;/b&gt; = 空行被删除的位置。超过3,000行的大文件将跳过高亮显示。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="270" />
        <source>The status bar at the bottom shows &lt;b&gt;merge count, blank lines removed, original line count, and final line count&lt;/b&gt;.</source>
        <translation>底部统计栏显示&lt;b&gt;合并次数、空行删除数、原始行数、最终行数&lt;/b&gt;。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="271" />
        <source>Press &lt;b&gt;Ctrl+F&lt;/b&gt; to search within the source and result text. Enter jumps to the next match, Shift+Enter to the previous.</source>
        <translation>按&lt;b&gt;Ctrl+F&lt;/b&gt;可在原文和修改后的文本中搜索关键词。Enter跳到下一个，Shift+Enter跳到上一个。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="272" />
        <source>Files are always saved as &lt;b&gt;UTF-8&lt;/b&gt;. Convert the encoding separately if you need to preserve the original (e.g. EUC-KR).</source>
        <translation>文件始终以&lt;b&gt;UTF-8&lt;/b&gt;编码保存。如需保留原始编码（如EUC-KR），请另行转换。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="274" />
        <source>&lt;b&gt;Partially corrupted files&lt;/b&gt; — Files with damaged bytes can still be opened. Corrupted characters are shown as &lt;code&gt;�&lt;/code&gt; (U+FFFD), and the status bar shows a &lt;b&gt;⚠&lt;/b&gt; icon with a 'Partial encoding failure' warning.</source>
        <translation>&lt;b&gt;部分损坏文件的处理&lt;/b&gt; — 部分字节损坏的文件也可以打开。损坏的字符显示为&lt;code&gt;�&lt;/code&gt;（U+FFFD），状态栏会显示&lt;b&gt;⚠&lt;/b&gt;图标和"部分编码失败"警告。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="275" />
        <source>Text Fixer is optimized for &lt;b&gt;detailed inspection of a single file&lt;/b&gt;. Open corrupted files to see exactly where the damage is, edit those spots manually, or decide whether to re-acquire the original.</source>
        <translation>Text Fixer 针对&lt;b&gt;单个文件的精细审核&lt;/b&gt;进行了优化。打开损坏文件可直接查看损坏位置，手动编辑该段，或判断是否需要重新获取原件。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="276" />
        <source>Files with tens of thousands of corrupted characters rarely recover well. Re-downloading from the source is usually better. Bulk Fixer automatically skips such files to protect the originals.</source>
        <translation>数万字符以上的大量损坏文件难以通过校正恢复质量。建议优先考虑从原来源重新下载。Bulk Fixer 会自动跳过此类文件以保护原件。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="280" />
        <source>Bulk Fixer</source>
        <translation>Bulk Fixer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="281" />
        <source>Batch-correct line breaks across multiple TXT files</source>
        <translation>批量校正多个TXT文件的换行</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="282" />
        <source>Applies the Text Fixer correction engine to many files at once. Ideal for cleaning up batches of TXT files extracted from OCR or e-books.</source>
        <translation>将Text Fixer的校正引擎批量应用于多个文件。适用于一次性整理从OCR或电子书中提取的大量TXT文件。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="284" />
        <source>&lt;b&gt;Add files&lt;/b&gt; — Use &lt;code&gt;[📄 Add files]&lt;/code&gt; or &lt;code&gt;[📂 Add folder]&lt;/code&gt; to load TXT files. You can also drag and drop folders directly onto the file list to recursively collect &lt;code&gt;.txt&lt;/code&gt; files.</source>
        <translation>&lt;b&gt;添加文件&lt;/b&gt; — 使用&lt;code&gt;[📄 添加文件]&lt;/code&gt;或&lt;code&gt;[📂 添加文件夹]&lt;/code&gt;加载TXT文件。也可以将文件夹直接拖放到文件列表中，自动递归收集&lt;code&gt;.txt&lt;/code&gt;文件。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="285" />
        <source>&lt;b&gt;Set options&lt;/b&gt; — Choose the merge mode (Auto / Korean / English) and correction options in the right panel. Use the &lt;b&gt;Preset&lt;/b&gt; dropdown to quickly apply "General document" or "Book / Novel" settings.</source>
        <translation>&lt;b&gt;设置选项&lt;/b&gt; — 在右侧面板中选择合并模式（自动/韩语/英语）和四个校正选项。使用&lt;b&gt;预设&lt;/b&gt;下拉框选择"一般文档"或"书籍·小说"可一键配置选项。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="286" />
        <source>&lt;b&gt;Save settings&lt;/b&gt; — Specify an output folder, or leave it empty to save as &lt;code&gt;[Fixed]filename.txt&lt;/code&gt; beside each original file. Enable &lt;b&gt;Preserve folder structure&lt;/b&gt; to recreate the original subfolder hierarchy inside the output folder.</source>
        <translation>&lt;b&gt;保存设置&lt;/b&gt; — 指定输出文件夹，或留空则以&lt;code&gt;[Fixed]文件名.txt&lt;/code&gt;保存在原文件旁边。勾选&lt;b&gt;保留文件夹结构&lt;/b&gt;可在输出文件夹中重现原始子文件夹层级。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="287" />
        <source>&lt;b&gt;Click &lt;code&gt;[▶ Start batch fix]&lt;/code&gt;&lt;/b&gt; — Progress is shown during processing; a summary of successes and failures is displayed on completion.</source>
        <translation>&lt;b&gt;点击&lt;code&gt;[▶ 开始批量校正]&lt;/code&gt;&lt;/b&gt; — 处理期间显示进度，完成后通知成功和失败文件数。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="288" />
        <source>Click any file in the list to preview the corrected result in the preview panel on the right.</source>
        <translation>点击文件列表中的项目，可在右侧预览面板中预览校正结果。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="289" />
        <source>The default output folder is &lt;code&gt;Output/&lt;/code&gt;. You can change it globally in ⚙ Settings or per-tab individually. The folder opens automatically after saving.</source>
        <translation>默认输出文件夹为&lt;code&gt;Output/&lt;/code&gt;。可在⚙设置中全局更改，也可在各标签页单独指定。保存完成后自动打开。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="290" />
        <source>Only TXT files are supported. Convert DOCX, PDF, etc. to TXT with Text Converter first.</source>
        <translation>仅支持TXT文件。请先用Text Converter将DOCX、PDF等格式转换为TXT后再使用。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="292" />
        <source>&lt;b&gt;Automatic corruption tiering&lt;/b&gt; — Bulk Fixer classifies partially corrupted files into three tiers based on damage severity:&lt;br&gt;• &lt;b&gt;Tier 1&lt;/b&gt; (1–500 damaged chars): Fixed + report generated&lt;br&gt;• &lt;b&gt;Tier 2&lt;/b&gt; (501–5,000 damaged chars): Fixed + report generated (review recommended)&lt;br&gt;• &lt;b&gt;Tier 3&lt;/b&gt; (5,001+ damaged chars): &lt;b&gt;Automatically skipped (original preserved)&lt;/b&gt; + report only</source>
        <translation>&lt;b&gt;编码损坏文件自动分级&lt;/b&gt; — Bulk Fixer 检测到部分损坏文件后，根据损坏程度分为三级处理：&lt;br&gt;• &lt;b&gt;Tier 1&lt;/b&gt;（1~500字符损坏）：校正后生成报告&lt;br&gt;• &lt;b&gt;Tier 2&lt;/b&gt;（501~5,000字符损坏）：校正后生成报告（建议审核）&lt;br&gt;• &lt;b&gt;Tier 3&lt;/b&gt;（5,001字符以上）：&lt;b&gt;自动跳过（保护原文件）&lt;/b&gt; + 仅生成报告</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="293" />
        <source>Reports are created next to the fixed output as &lt;code&gt;{original_filename}.encoding_report.txt&lt;/code&gt;, detailing damaged line/column positions for up to 5,000 entries.</source>
        <translation>报告文件以&lt;code&gt;{原文件名}.encoding_report.txt&lt;/code&gt;的形式生成在校正版旁边，详细记录哪些行、哪些列出现损坏，最多记录 5,000 条。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="294" />
        <source>Files skipped as Tier 3 should be &lt;b&gt;individually reviewed in Text Fixer&lt;/b&gt;. Heavy corruption usually means wrong encoding detection or a corrupted source, so re-acquiring the original is often better than forcing correction.</source>
        <translation>被 Tier 3 跳过的文件应&lt;b&gt;在 Text Fixer 中单独审核&lt;/b&gt;。大量损坏通常意味着编码检测错误或原文件本身存在问题，与其强制批量校正，不如重新获取原件。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="298" />
        <source>Shortcuts &amp; Tips</source>
        <translation>快捷键 &amp; 使用技巧</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="299" />
        <source>Use keyboard shortcuts to navigate quickly. All shortcuts can be customized in Settings.</source>
        <translation>使用键盘快捷键快速操作，可在设置中自定义。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="301" />
        <source>Go to Text Merger</source>
        <translation>转到 Text Merger</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="302" />
        <source>Go to Text Converter</source>
        <translation>转到 Text Converter</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="303" />
        <source>Go to Tag Editor</source>
        <translation>转到 Tag Editor</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="304" />
        <source>Go to Batch Renamer</source>
        <translation>转到 Batch Renamer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="305" />
        <source>Go to Text Fixer</source>
        <translation>转到 Text Fixer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="306" />
        <source>Go to Bulk Fixer</source>
        <translation>转到 Bulk Fixer</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="307" />
        <source>Search text in Text Fixer</source>
        <translation>在 Text Fixer 中搜索文本</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="308" />
        <source>⚙ button (top right)</source>
        <translation>⚙ 按钮(右上角)</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="308" />
        <source>Open Settings — change theme, language, and shortcuts</source>
        <translation>打开设置 — 可更改主题、语言和快捷键</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="309" />
        <source>Settings (theme, language, shortcuts) are saved automatically on exit and restored on next launch.</source>
        <translation>设置（主题、语言、快捷键）在退出时自动保存，下次启动时恢复。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="310" />
        <source>&lt;b&gt;Drag and drop&lt;/b&gt; is supported in all tabs. Dropping a folder adds all supported files inside it at once.</source>
        <translation>所有选项卡均支持&lt;b&gt;拖放&lt;/b&gt;加载文件。拖入文件夹时，将批量添加其中的支持文件。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="311" />
        <source>🔋 &lt;b&gt;Sleep Prevention&lt;/b&gt; — While Text Merger, Text Converter, Text Fixer, or Bulk Fixer is running, Windows sleep mode is automatically blocked. It is released immediately when the task completes or an error occurs. Screen lock is unaffected.</source>
        <translation>🔋 &lt;b&gt;防止休眠&lt;/b&gt; — Text Merger、Text Converter、Text Fixer 或 Bulk Fixer 执行任务期间，Windows 休眠模式将被自动阻止。任务完成或发生错误时立即解除。屏幕锁定与休眠无关，处理过程中仍可正常使用。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="315" />
        <source>File creation notice</source>
        <translation>生成文件说明</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="316" />
        <source>Files and folders created automatically during use</source>
        <translation>程序使用过程中自动创建的文件和文件夹</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="317" />
        <source>File Nexus Suite automatically creates the following items in the program folder for settings storage, default output, and error logging.</source>
        <translation>File Nexus Suite会在程序所在文件夹中自动创建以下内容，用于保存设置、默认输出和错误记录。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="319" />
        <source>&lt;b&gt;FileNexusSuite.json&lt;/b&gt; — Stores your theme, language, shortcuts, and tab settings. Saved on exit, restored on next launch.</source>
        <translation>&lt;b&gt;FileNexusSuite.json&lt;/b&gt; — 保存主题、语言、快捷键及各标签页设置的配置文件。退出时自动保存，下次启动时恢复。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="320" />
        <source>&lt;b&gt;Output/&lt;/b&gt; — Default output folder for Text Converter, Bulk Fixer, and Text Fixer. Created automatically on first launch. Change the location globally in ⚙ Settings; the folder opens automatically after saving.</source>
        <translation>&lt;b&gt;Output/&lt;/b&gt; — Text Converter、Bulk Fixer和Text Fixer的默认输出文件夹。首次启动时自动创建。可在⚙设置中全局更改位置，保存完成时自动打开。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="321" />
        <source>&lt;b&gt;logs/crash_*.log&lt;/b&gt; — Crash logs generated when an unexpected error occurs. Only the 3 most recent logs are kept; older ones are deleted automatically.</source>
        <translation>&lt;b&gt;logs/crash_*.log&lt;/b&gt; — 发生意外错误时自动生成的崩溃日志。仅保留最近3个，旧文件自动删除。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="322" />
        <source>&lt;b&gt;_internal/&lt;/b&gt; — Created automatically in folder-style exe builds. Contains the Python runtime. &lt;b&gt;Deleting it will prevent the program from running.&lt;/b&gt;</source>
        <translation>&lt;b&gt;_internal/&lt;/b&gt; — 文件夹形式exe构建时自动生成的Python运行时文件夹。&lt;b&gt;删除后程序将无法运行。&lt;/b&gt;</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="323" />
        <source>You can safely delete any of these files or folders. Required items will be recreated automatically on the next launch.</source>
        <translation>可以直接删除这些文件和文件夹。下次启动时，所需内容将自动重新创建。</translation>
    </message>
<message>
        <location filename="../fns_help.py" line="132" />
        <source>💡  Help — File Nexus Suite v%1</source>
        <translation>💡  帮助 — File Nexus Suite v%1</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="532" />
        <source>💡  Help</source>
        <translation>💡  帮助</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="582" />
        <source>Close</source>
        <translation>关闭</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="601" />
        <source>About</source>
        <translation>简介</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="144" />
        <source>File Nexus Suite is an integrated file utility for managing text, e-books, and media files. Text merging, EPUB conversion, file-name tag editing, batch renaming, line-break correction, and bulk fixing — six core features, all in one window.</source>
        <translation>File Nexus Suite 是专为文本、电子书及媒体文件作业设计的综合文件工具。文本合并、EPUB转换、文件名标签编辑、批量重命名、换行校正、批量校正 — 六大核心功能集于一个窗口之中。</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="162" />
        <source>Text Merger</source>
        <translation>Text Merger</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="452" />
        <source>Native support</source>
        <translation>原生支持</translation>
    </message>
    <message>
        <location filename="../fns_help.py" line="453" />
        <source>Library required</source>
        <translation>需安装库</translation>
    </message>
</context></TS>