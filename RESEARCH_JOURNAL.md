# Research Journal

## 2026-03-12 | Initial root survey

### Goal

- Выполнить первый глубокий аудит двух проектов в workspace.
- Подготовить корневую долговременную память агента.
- Начать формирование общей структуры для будущего Kaggle + math agent workflow.

### Read / surveyed

- Ключевые README обоих проектов.
- Workflow, inbox, multimodel и index-документы из `Math_Hypothese_AutoCheck_Witch_Agents/`.
- Навигационные, hypothesis, analysis и history documents из `ML in Math/`.
- Representative code files: entry points, runners и logging utilities.

### Main findings

- Первый проект уже даёт зрелую структуру исследовательской памяти и обработки знаний.
- Второй проект уже даёт зрелую инженерную дисциплину: runners, hypothesis loop, experiment logging, result analysis.
- Главный пробел был на уровне корня: не хватало общей памяти, prompt log, правил и канонического intake для новых Kaggle-задач.

### Decisions

- Корень workspace оформляется как orchestrator layer, а не как третий вычислительный проект.
- Новый корневой `kaggle_intake/` будет каноническим intake для markdown-файлов со ссылками на Kaggle competitions.
- Внутренний `ML in Math/baseline/` не переопределяется и остаётся проектным архивом/референсом.
- Пользовательские промпты должны храниться в отдельном корневом md-файле в максимально полном виде.

### Files created or updated

- `README.md`
- `PROJECT_MAP.md`
- `RESEARCH_SURVEY.md`
- `DOCUMENTATION_INDEX.md`
- `AGENTS.md`
- `USER_PROMPTS_LOG.md`
- `AGENT_ACTIVITY_LOG_SPEC.md`
- `DOCUMENTATION_STANDARDS.md`
- `EXPERIMENT_LOGGING_STANDARD.md`
- `MATH_RESEARCH_WORKFLOW.md`
- `BASELINE_INTAKE_SPEC.md`
- `KAGGLE_AUTONOMOUS_WORKFLOW.md`
- `SOURCE_COLLECTION_POLICY.md`
- `kaggle_intake/README.md`
- `kaggle_intake/_TEMPLATE_KAGGLE_INPUT.md`
- `.cursor/rules/root-core-memory.mdc`
- `.cursor/rules/root-documentation-sync.mdc`
- `.cursor/rules/root-baseline-intake.mdc`
- `.cursor/rules/root-kaggle-research.mdc`
- `.cursor/rules/root-math-research.mdc`
- `KAGGLE_TOPICS_ARCHIVE.md`
- `AGENT_INTERACTIONS_LOG.md`
- этот файл

### Risks / unknowns

- В будущем потребуется не только documentation layer, но и явный operational intake/playbook для новых Kaggle competitions.
- Нужно аккуратно развести корневые правила и локальные проектные docs, чтобы не получить дублирование.
- Понадобится следить, чтобы сверхподробное логирование не превращалось в хаотичный архив без индексов.

### Next step

- Использовать корневой `kaggle_intake/` как фактическую точку входа для первой новой Kaggle-задачи.
- При следующей крупной сессии синхронизировать корневые журналы с изменениями внутри дочерних проектов и соответствующих подпроектов.
- Накапливать prompt history, narrative activity log и взаимодействия субагентов в соответствующих корневых документах без разрыва формата.

---

## 2026-03-12 | First CayleyPy intake (First_input.md)

### Goal

- Зафиксировать первый реальный intake-файл с набором CayleyPy-соревнований.
- Создать стартовые записи в `KAGGLE_TOPICS_ARCHIVE.md` для каждой competition.
- Уточнить роль корневого агента как постоянного оркестратора субагентов.

### Read / surveyed

- `kaggle_intake/First_input.md`
- `KAGGLE_TOPICS_ARCHIVE.md`
- `AGENTS.md`
- `SUBAGENT_STANDARD_PROMPT.md`

### Main findings

- В одном intake-файле перечислен целый набор CayleyPy-соревнований (pancake, кубы, мегаминкс, transposons и др.).
- Pancake-competition уже частично покрывается подпроектом `CayleyPy_Pancake/`, остальные требуют новых подпроектов.
- Требуется стандартный промпт и дисциплина для субагентов, чтобы корневой агент всегда оставался оркестратором.

### Decisions

- Для каждой competition из `First_input.md` создана стартовая строка в `KAGGLE_TOPICS_ARCHIVE.md`.
- `CayleyPy_Pancake/` отмечен как subproject для CayleyPy-Pancake (status `in_progress`).
- Для `C4` (CayleyPy-444-Cube) подпроект `CayleyPy_444_Cube/` переведён в статус `in_progress` с ожиданием настроенного автосабмита и проверки формата сабмишена.
- Добавлен стандартный промпт для субагентов: `SUBAGENT_STANDARD_PROMPT.md`.
- В `AGENTS.md` зафиксировано, что корневой агент обязан запускать и курировать субагентов над подпроектами.

### Files created or updated

- `KAGGLE_TOPICS_ARCHIVE.md`
- `AGENTS.md`
- `SUBAGENT_STANDARD_PROMPT.md`
- `USER_PROMPTS_LOG.md` (Prompt 003)
- этот файл

### Risks / unknowns

- Конкретные подпроекты для каждой competition ещё не созданы (только помечены как `planned`).
- Не определены конкретные роли и специализации субагентов для каждой задачи (math/engineering/synthesis).

### Next step

- Завести для выбранной CayleyPy-темы первый реальный подпроект в корне (свою папку и локальные docs).
- Запустить math- и engineering-субагентов по этой теме, соблюдая `SUBAGENT_STANDARD_PROMPT.md`.
- Записать первую коммуникацию между субагентами и корневым агентом в `AGENT_INTERACTIONS_LOG.md`.
