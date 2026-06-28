"""
i18n.py - UI translations for English, Spanish, Japanese, Korean.
"""

TRANSLATIONS = {
    "en": {
        "lang_label": "🌐 Language",
        "app_title": "🧪 TestCase Agent",
        "step_upload": "📁 Upload",
        "step_qa": "❓ Q&A",
        "step_generate": "⚙️ Generate",
        "step_done": "✅ Done",
        "sidebar_config": "⚙️ Configuration",
        "sidebar_openai": "🤖 OpenAI",
        "api_key_label": "API Key",
        "api_key_placeholder": "sk-...",
        "api_key_help": "Your OpenAI API key — used only for this session, never stored.",
        "sidebar_confluence": "🔗 Confluence (optional)",
        "conf_url_label": "Confluence URL",
        "conf_url_placeholder": "https://yourorg.atlassian.net/wiki",
        "conf_key_label": "API Key / Token",
        "conf_uid_label": "Email / User ID",
        "conf_uid_placeholder": "you@company.com",
        "conf_page_label": "Page ID (optional)",
        "conf_space_label": "Space Key (optional)",
        "conf_disclaimer": "⚠️ **Disclaimer:** By connecting Confluence, you confirm that the provided credentials belong to an account with legitimate read access to the specified pages/spaces. Content fetched is used only for test case generation in this session.",
        "verify_btn": "🔐 Verify Access",
        "verifying": "Verifying...",
        "verified_as": "🔗 Connected as:",
        "sidebar_docs": "📁 Spec Documents",
        "queued_label": "**Queued:**",
        "start_over": "🔄 Start Over",
        "welcome_msg": (
            "👋 **Welcome to TestCase Agent!**\n\n"
            "I'll analyse your spec documents, ask clarifying questions to fill gaps, "
            "then generate comprehensive test cases — exported as both **Excel** and **CSV**.\n\n"
            "**Get started:**\n"
            "1. Enter your OpenAI API key in the sidebar\n"
            "2. *(Optional)* Connect Confluence\n"
            "3. Upload spec docs (PDF, XLSX, DOCX)\n"
            "4. Click **Analyse Documents**"
        ),
        "no_files_queued": "No files queued — use the sidebar to upload",
        "analyse_btn": "🔍 Analyse Documents",
        "analysing_spinner": "📖 Ingesting documents and analysing gaps...",
        "api_key_error": "⚠️ Please enter your OpenAI API key in the sidebar.",
        "no_content_error": "⚠️ Please upload at least one file or connect Confluence.",
        "qa_prompt": "❓ Please answer the questions below to fill specification gaps:",
        "why_matters": "💡 Why this matters:",
        "answer_placeholder": "Type your answer here (max 1000 characters)...",
        "skip_btn": "⏭ Skip & Generate",
        "submit_btn": "✅ Submit Answers & Generate",
        "submit_hint": "Answer at least 2 questions to enable submission.",
        "generating_spinner": "⚙️ Building knowledge graph and generating test cases...",
        "dl_xlsx": "⬇️ Download Excel (.xlsx)",
        "dl_csv": "⬇️ Download CSV (.csv)",
        "conn_error": "❌ Cannot connect to backend. Make sure FastAPI is running:\n```\ncd backend && uvicorn main:app --reload\n```",
        "char_limit": "characters",
        "test_cases_metric": "Test Cases",
        "features_metric": "Features",
        "edge_cases_metric": "Edge Cases",
        "user_roles_metric": "User Roles",
        "download_ready": "Your reports are ready:",
    },
    "es": {
        "lang_label": "🌐 Idioma",
        "app_title": "🧪 Agente de Casos de Prueba",
        "step_upload": "📁 Subir",
        "step_qa": "❓ Preguntas",
        "step_generate": "⚙️ Generar",
        "step_done": "✅ Listo",
        "sidebar_config": "⚙️ Configuración",
        "sidebar_openai": "🤖 OpenAI",
        "api_key_label": "Clave de API",
        "api_key_placeholder": "sk-...",
        "api_key_help": "Tu clave de API de OpenAI — solo se usa en esta sesión, nunca se almacena.",
        "sidebar_confluence": "🔗 Confluence (opcional)",
        "conf_url_label": "URL de Confluence",
        "conf_url_placeholder": "https://tuorg.atlassian.net/wiki",
        "conf_key_label": "Clave API / Token",
        "conf_uid_label": "Correo / ID de usuario",
        "conf_uid_placeholder": "tu@empresa.com",
        "conf_page_label": "ID de página (opcional)",
        "conf_space_label": "Clave de espacio (opcional)",
        "conf_disclaimer": "⚠️ **Aviso:** Al conectar Confluence, confirmas que las credenciales proporcionadas pertenecen a una cuenta con acceso legítimo de lectura. El contenido se usa solo para generar casos de prueba en esta sesión.",
        "verify_btn": "🔐 Verificar acceso",
        "verifying": "Verificando...",
        "verified_as": "🔗 Conectado como:",
        "sidebar_docs": "📁 Documentos de especificación",
        "queued_label": "**En cola:**",
        "start_over": "🔄 Reiniciar",
        "welcome_msg": (
            "👋 **¡Bienvenido al Agente de Casos de Prueba!**\n\n"
            "Analizaré tus documentos de especificación, haré preguntas aclaratorias y "
            "generaré casos de prueba completos — exportados en **Excel** y **CSV**.\n\n"
            "**Cómo empezar:**\n"
            "1. Ingresa tu clave de API de OpenAI en la barra lateral\n"
            "2. *(Opcional)* Conecta Confluence\n"
            "3. Sube documentos de especificación (PDF, XLSX, DOCX)\n"
            "4. Haz clic en **Analizar Documentos**"
        ),
        "no_files_queued": "Sin archivos — usa la barra lateral para subir",
        "analyse_btn": "🔍 Analizar Documentos",
        "analysing_spinner": "📖 Ingresando documentos y analizando brechas...",
        "api_key_error": "⚠️ Por favor ingresa tu clave de API de OpenAI en la barra lateral.",
        "no_content_error": "⚠️ Por favor sube al menos un archivo o conecta Confluence.",
        "qa_prompt": "❓ Por favor responde las siguientes preguntas para llenar las brechas de la especificación:",
        "why_matters": "💡 Por qué es importante:",
        "answer_placeholder": "Escribe tu respuesta aquí (máx. 1000 caracteres)...",
        "skip_btn": "⏭ Omitir y Generar",
        "submit_btn": "✅ Enviar Respuestas y Generar",
        "submit_hint": "Responde al menos 2 preguntas para habilitar el envío.",
        "generating_spinner": "⚙️ Construyendo grafo de conocimiento y generando casos de prueba...",
        "dl_xlsx": "⬇️ Descargar Excel (.xlsx)",
        "dl_csv": "⬇️ Descargar CSV (.csv)",
        "conn_error": "❌ No se puede conectar al backend.",
        "char_limit": "caracteres",
        "test_cases_metric": "Casos de prueba",
        "features_metric": "Funcionalidades",
        "edge_cases_metric": "Casos límite",
        "user_roles_metric": "Roles de usuario",
        "download_ready": "Tus reportes están listos:",
    },
    "ja": {
        "lang_label": "🌐 言語",
        "app_title": "🧪 テストケースエージェント",
        "step_upload": "📁 アップロード",
        "step_qa": "❓ Q&A",
        "step_generate": "⚙️ 生成",
        "step_done": "✅ 完了",
        "sidebar_config": "⚙️ 設定",
        "sidebar_openai": "🤖 OpenAI",
        "api_key_label": "APIキー",
        "api_key_placeholder": "sk-...",
        "api_key_help": "OpenAI APIキー — このセッションのみ使用され、保存されません。",
        "sidebar_confluence": "🔗 Confluence（任意）",
        "conf_url_label": "Confluence URL",
        "conf_url_placeholder": "https://yourorg.atlassian.net/wiki",
        "conf_key_label": "APIキー / トークン",
        "conf_uid_label": "メール / ユーザーID",
        "conf_uid_placeholder": "you@company.com",
        "conf_page_label": "ページID（任意）",
        "conf_space_label": "スペースキー（任意）",
        "conf_disclaimer": "⚠️ **免責事項:** Confluenceに接続することで、提供された認証情報が正当な読み取りアクセス権を持つアカウントのものであることを確認します。取得したコンテンツはこのセッションのテストケース生成のみに使用されます。",
        "verify_btn": "🔐 アクセスを確認",
        "verifying": "確認中...",
        "verified_as": "🔗 接続済み:",
        "sidebar_docs": "📁 仕様ドキュメント",
        "queued_label": "**キュー:**",
        "start_over": "🔄 最初からやり直す",
        "welcome_msg": (
            "👋 **テストケースエージェントへようこそ！**\n\n"
            "仕様書を分析し、不明点について質問した後、"
            "包括的なテストケースを生成します — **Excel** と **CSV** でエクスポートできます。\n\n"
            "**開始方法:**\n"
            "1. サイドバーにOpenAI APIキーを入力\n"
            "2. *（任意）* Confluenceに接続\n"
            "3. 仕様書をアップロード（PDF、XLSX、DOCX）\n"
            "4. **ドキュメントを分析** をクリック"
        ),
        "no_files_queued": "ファイルがキューにありません — サイドバーからアップロードしてください",
        "analyse_btn": "🔍 ドキュメントを分析",
        "analysing_spinner": "📖 ドキュメントを取り込んでギャップを分析中...",
        "api_key_error": "⚠️ サイドバーにOpenAI APIキーを入力してください。",
        "no_content_error": "⚠️ 少なくとも1つのファイルをアップロードするか、Confluenceに接続してください。",
        "qa_prompt": "❓ 仕様のギャップを埋めるために以下の質問に回答してください:",
        "why_matters": "💡 この質問が重要な理由:",
        "answer_placeholder": "回答を入力してください（最大1000文字）...",
        "skip_btn": "⏭ スキップして生成",
        "submit_btn": "✅ 回答を送信して生成",
        "submit_hint": "送信を有効にするには少なくとも2つの質問に回答してください。",
        "generating_spinner": "⚙️ 知識グラフを構築してテストケースを生成中...",
        "dl_xlsx": "⬇️ Excelをダウンロード (.xlsx)",
        "dl_csv": "⬇️ CSVをダウンロード (.csv)",
        "conn_error": "❌ バックエンドに接続できません。",
        "char_limit": "文字",
        "test_cases_metric": "テストケース",
        "features_metric": "機能",
        "edge_cases_metric": "エッジケース",
        "user_roles_metric": "ユーザーロール",
        "download_ready": "レポートの準備ができました:",
    },
    "ko": {
        "lang_label": "🌐 언어",
        "app_title": "🧪 테스트케이스 에이전트",
        "step_upload": "📁 업로드",
        "step_qa": "❓ Q&A",
        "step_generate": "⚙️ 생성",
        "step_done": "✅ 완료",
        "sidebar_config": "⚙️ 설정",
        "sidebar_openai": "🤖 OpenAI",
        "api_key_label": "API 키",
        "api_key_placeholder": "sk-...",
        "api_key_help": "OpenAI API 키 — 이 세션에서만 사용되며 저장되지 않습니다.",
        "sidebar_confluence": "🔗 Confluence (선택)",
        "conf_url_label": "Confluence URL",
        "conf_url_placeholder": "https://yourorg.atlassian.net/wiki",
        "conf_key_label": "API 키 / 토큰",
        "conf_uid_label": "이메일 / 사용자 ID",
        "conf_uid_placeholder": "you@company.com",
        "conf_page_label": "페이지 ID (선택)",
        "conf_space_label": "스페이스 키 (선택)",
        "conf_disclaimer": "⚠️ **고지사항:** Confluence에 연결함으로써 제공된 자격 증명이 지정된 페이지/공간에 대한 합법적인 읽기 접근 권한을 가진 계정의 것임을 확인합니다. 가져온 콘텐츠는 이 세션의 테스트 케이스 생성에만 사용됩니다.",
        "verify_btn": "🔐 접근 확인",
        "verifying": "확인 중...",
        "verified_as": "🔗 연결됨:",
        "sidebar_docs": "📁 명세 문서",
        "queued_label": "**대기열:**",
        "start_over": "🔄 처음부터 시작",
        "welcome_msg": (
            "👋 **테스트케이스 에이전트에 오신 것을 환영합니다!**\n\n"
            "명세 문서를 분석하고 불명확한 부분에 대해 질문한 후, "
            "포괄적인 테스트 케이스를 생성합니다 — **Excel** 및 **CSV**로 내보내기 가능합니다.\n\n"
            "**시작 방법:**\n"
            "1. 사이드바에 OpenAI API 키 입력\n"
            "2. *(선택)* Confluence 연결\n"
            "3. 명세 문서 업로드 (PDF, XLSX, DOCX)\n"
            "4. **문서 분석** 클릭"
        ),
        "no_files_queued": "파일 없음 — 사이드바에서 업로드하세요",
        "analyse_btn": "🔍 문서 분석",
        "analysing_spinner": "📖 문서 수집 및 갭 분석 중...",
        "api_key_error": "⚠️ 사이드바에 OpenAI API 키를 입력하세요.",
        "no_content_error": "⚠️ 파일을 하나 이상 업로드하거나 Confluence에 연결하세요.",
        "qa_prompt": "❓ 명세의 갭을 채우기 위해 아래 질문에 답변해 주세요:",
        "why_matters": "💡 이 질문이 중요한 이유:",
        "answer_placeholder": "여기에 답변을 입력하세요 (최대 1000자)...",
        "skip_btn": "⏭ 건너뛰고 생성",
        "submit_btn": "✅ 답변 제출 및 생성",
        "submit_hint": "제출을 활성화하려면 최소 2개의 질문에 답변하세요.",
        "generating_spinner": "⚙️ 지식 그래프 구축 및 테스트 케이스 생성 중...",
        "dl_xlsx": "⬇️ Excel 다운로드 (.xlsx)",
        "dl_csv": "⬇️ CSV 다운로드 (.csv)",
        "conn_error": "❌ 백엔드에 연결할 수 없습니다.",
        "char_limit": "자",
        "test_cases_metric": "테스트 케이스",
        "features_metric": "기능",
        "edge_cases_metric": "엣지 케이스",
        "user_roles_metric": "사용자 역할",
        "download_ready": "보고서가 준비되었습니다:",
    },
}

LANG_OPTIONS = {
    "English": "en",
    "Español": "es",
    "日本語": "ja",
    "한국어": "ko",
}


def t(key: str, lang: str = "en") -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
