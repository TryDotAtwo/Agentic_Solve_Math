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

---

## 2026-03-12 | C4_eng и C4_math — первый цикл по CayleyPy-444-Cube

### Goal

- Инициализировать инженерный и математический треки в подпроекте `CayleyPy_444_Cube/`.
- Подготовить документацию и кодовую основу для первого сабмита на Kaggle (autosubmit-пайплайн + проверка формата).

### Read / surveyed

- `CayleyPy_444_Cube/README.md`
- `CayleyPy_444_Cube/docs/01_COMPETITION_OVERVIEW.md`
- `CayleyPy_444_Cube/docs/02_AUTOSUBMIT_SETUP.md`
- `CayleyPy_444_Cube/docs/03_STATE_AND_GROUP_STRUCTURE.md`
- `CayleyPy_444_Cube/docs/04_POTENTIAL_HYPOTHESES.md`
- `KAGGLE_TOPICS_ARCHIVE.md` (строки C4 и C6)
- `AGENT_INTERACTIONS_LOG.md`

### Main findings

- Инженерный субагент `C4_eng` описал формат submission и спроектировал autosubmit-пайплайн (CLI + HTTP-fallback) внутри `CayleyPy_444_Cube/submission/`.
- Математический субагент `C4_math` задал концептуальную структуру состояния и группы, а также список потенциальных гипотез и направлений для дальнейшего анализа.
- Подпроект `CayleyPy_444_Cube/` готов к шагу «собрать первый рабочий submission.csv и прогнать autosubmit» при наличии Kaggle-токена.

### Decisions

- Статус C4 в `KAGGLE_TOPICS_ARCHIVE.md` зафиксирован как `in_progress` с ключевыми документами в `CayleyPy_444_Cube/docs/*.md`.
- Первый практический milestone для 444-cube:
  - реализовать простой baseline-решатель (даже если он тривиальный) в `CayleyPy_444_Cube/`;
  - сгенерировать корректный по форме `submission.csv`;
  - прогнать локальные проверки формата и затем autosubmit из `CayleyPy_444_Cube/submission/autosubmit.py` (с реальным `kaggle.json` на стороне пользователя).

### Files created or updated (subagents)

- `CayleyPy_444_Cube/README.md`
- `CayleyPy_444_Cube/docs/01_COMPETITION_OVERVIEW.md`
- `CayleyPy_444_Cube/docs/02_AUTOSUBMIT_SETUP.md`
- `CayleyPy_444_Cube/docs/03_STATE_AND_GROUP_STRUCTURE.md`
- `CayleyPy_444_Cube/docs/04_POTENTIAL_HYPOTHESES.md`
- `CayleyPy_444_Cube/submission/autosubmit.py` (+ пакет `submission/`)
- `CayleyPy_444_Cube/tests/test_submission_format.py`

### Risks / unknowns

- Точный формат данных и ограничения соревнования CayleyPy-444-Cube ещё не подтверждены с Kaggle (ряд мест в доках помечены как ASSUMPTION/TODO).
- Baseline-решатель для генерации корректного `submission.csv` ещё не реализован.

### Next step

- Внутри `CayleyPy_444_Cube/` реализовать минимальный baseline-генератор submission (даже если решения тривиальны).
- Проверить через тесты и валидатор, что `submission.csv` соответствует задокументированному формату.
- С Kaggle-токеном пользователя прогнать autosubmit из подпроекта и зафиксировать результат (score, статус) в локальных доках подпроекта и в корневых журналах.

---

## 2026-03-13 | C4 – инфраструктура, поиск, NN‑скелет и экспериментальный цикл

### Goal

- Развернуть в `CayleyPy_444_Cube/` полный инженерный и математический каркас:
  - жёсткий контракт submission и боевой автосабмит;
  - минимальный baseline‑генератор `submission.csv`;
  - скелет поискового солвера и NN+search гибрида;
  - локальные раннеры экспериментов и лидерборд‑стратегию;
  - канонические summary‑документы для будущей статьи.

### Read / surveyed

- Корневые стандарты:
  - `EXPERIMENT_LOGGING_STANDARD.md`
  - `AGENT_ACTIVITY_LOG_SPEC.md`
- Локальные доки подпроекта:
  - `CayleyPy_444_Cube/README.md`
  - `CayleyPy_444_Cube/docs/01_COMPETITION_OVERVIEW.md`
  - `CayleyPy_444_Cube/docs/02_AUTOSUBMIT_SETUP.md`
  - `CayleyPy_444_Cube/docs/03_STATE_AND_GROUP_STRUCTURE.md`
  - `CayleyPy_444_Cube/docs/04_POTENTIAL_HYPOTHESES.md`

### Decisions

- Зафиксирован жёсткий интерфейс для `submission.csv` (колонки `id`, `solution`) и competition slug `cayleypy-444-cube`, согласованный между доками и кодом (`submission/autosubmit.py`, тесты).
- `submission/autosubmit.py` признан боевым модулем автосабмита; в `02_AUTOSUBMIT_SETUP.md` добавлена явная инструкция по первому ручному сабмиту.
- Реализован минимальный baseline‑генератор:
  - `generate_dummy_submission.py` создаёт тривиальный, но корректный `submission.csv` из `test.csv` и прогоняет локальную валидацию.
- Сформирован поисковый каркас:
  - пакет `search/` с алфавитом ходов (`moves.py`) и стохастическим beam‑search‑скелетом (`solver_random_beam.py`);
  - `solve_with_search.py` генерирует `submission_search.csv` на основе столбца `state` (ASSUMPTION в ожидании реальной схемы данных).
- Подготовлен NN+search слой:
  - пакет `nn/` (`schema.py`, `interfaces.py`) и план `docs/05_NN_HYBRID_SOLVER_PLAN.md`, задающие интерфейсы для policy+value‑моделей и их интеграции в эвристику поиска.
- Построен экспериментальный цикл:
  - раннеры `run_experiment.py` (режимы `dummy` и `search`) и `run_best.py`;
  - документ `docs/06_EXPERIMENT_WORKFLOW.md` описывает использование раннеров совместно с автосабмитом и требования к логированию.
- Развернут math‑трек внутри подпроекта и связь с глобальной math‑лабораторией:
  - `docs/07_MATH_TRACK_INTEGRATION.md` описывает маршрутизацию гипотез `H4C_*` в глобальный math‑проект.
- Определена лидерборд‑стратегия:
  - `docs/08_LEADERBOARD_STRATEGY.md` задаёт лестницу baseline’ов, многоступенчатые пайплайны и практику управления конфигурациями сабмитов.
- Выделены канонические summary‑документы:
  - инженерный: `CayleyPy_444_Cube/docs/09_ENGINEERING_SUMMARY.md`;
  - математический: `CayleyPy_444_Cube/docs/10_MATH_SUMMARY.md`.

### Files created or updated

- В корне:
  - `RESEARCH_JOURNAL.md` (эта запись)
  - `KAGGLE_TOPICS_ARCHIVE.md` (уточнение ключевых docs для C4 при необходимости)
- В `CayleyPy_444_Cube/`:
  - `README.md`
  - `generate_dummy_submission.py`
  - `solve_with_search.py`
  - `run_experiment.py`
  - `run_best.py`
  - `search/__init__.py`
  - `search/moves.py`
  - `search/solver_random_beam.py`
  - `nn/__init__.py`
  - `nn/schema.py`
  - `nn/interfaces.py`
- В `CayleyPy_444_Cube/docs`:
  - `01_COMPETITION_OVERVIEW.md` (добавлен раздел про hard interface contract)
  - `02_AUTOSUBMIT_SETUP.md` (добавлен сценарий первого end‑to‑end сабмита)
  - `05_NN_HYBRID_SOLVER_PLAN.md`
  - `06_EXPERIMENT_WORKFLOW.md`
  - `07_MATH_TRACK_INTEGRATION.md`
  - `08_LEADERBOARD_STRATEGY.md`
  - `09_ENGINEERING_SUMMARY.md`
  - `10_MATH_SUMMARY.md`

### Risks / unknowns

- Реальный формат данных соревнования (колонки `state` и др.) и точная формула score ещё не подтверждены (документы явно помечают ASSUMPTION/TODO точки).
- Поисковые и NN‑компоненты пока работают на абстрактных строковых состояниях и не используют полноценный 4×4×4 engine.
- NN‑слой задан на уровне интерфейса и планов; фактические training pipelines и модели требуют отдельной ML‑среды и набора данных.

### Next step

- Подключить конкретный 4×4×4 движок (библиотеку или собственную реализацию) к каркасу `search/` и наладить симуляцию состояний.
- Построить первые содержательные эвристики (в том числе PDB‑подобные) в терминах гипотез `H4C_metric_*` и `H4C_invariant_*`.
- В отдельной ML‑среде реализовать proof‑of‑concept NN‑модель, совместимую с `PolicyValueModel`, и сравнить search‑only и NN‑guided search под ограниченным бюджетом.

---

## 2026-03-13 | Root main.py orchestrator for C4

### Goal

- Добавить в корень workspace исполняемый скрипт, который:
  - сам запускает нужные подпроектные скрипты/солверы;
  - может по одной команде пользователя скачать данные C4, сгенерировать сабмит и отправить его на Kaggle.

### Read / surveyed

- Корневые документы:
  - `README.md`
  - `AGENTS.md`
  - `KAGGLE_AUTONOMOUS_WORKFLOW.md`
- Подпроектные entry points:
  - `CayleyPy_444_Cube/run_best.py`
  - `CayleyPy_444_Cube/submission/autosubmit.py`

### Decisions

- В корне добавлен скрипт `main.py`, который:
  - для соревнования C4 (`--competition c4`):
    - при отсутствии флага `--no-download-data` вызывает Kaggle CLI:
      - `kaggle competitions download -c cayley-py-444-cube -p CayleyPy_444_Cube/data`;
    - проверяет наличие `CayleyPy_444_Cube/data/test.csv`;
    - вызывает `CayleyPy_444_Cube/run_best.py` для генерации `submission_best.csv`;
    - при отсутствии флага `--no-submit` использует `CayleyPy_444_Cube/submission/autosubmit.py` для валидации и сабмита файла.
- Корневой `README.md` обновлён:
  - описан `main.py` как стандартный способ запуска полного пайплайна (download → solve → submit) для C4;
  - приведены примеры команд запуска.
- В `AGENTS.md` зафиксировано, что:
  - помимо документирования, корневой агент должен по возможности **запускать** скрипты (через доступные инструменты);
  - `main.py` выступает скриптовым оркестратором, инициирующим пайплайны подпроектов.

### Files created or updated

- `main.py` (новый корневой оркестратор)
- `README.md` (раздел про root orchestrator script)
- `AGENTS.md` (описание роли `main.py` и обязанности запускать скрипты)
- `RESEARCH_JOURNAL.md` (эта запись)

### Risks / unknowns

- Успешная работа `main.py` зависит от:
  - наличия установленного Kaggle CLI в PATH;
  - корректно настроенного `kaggle.json` у пользователя;
  - готовности подпроектного солвера (сейчас это скелет search‑based/NN‑guided решения).

### Next step

- По мере взросления солверов для C4 обновлять:
  - реализацию `CayleyPy_444_Cube/run_best.py`, чтобы он всегда указывал на фактически сильнейшую конфигурацию;
  - при необходимости – логику `main.py`, если появятся новые режимы или дополнительные шаги (например, пост‑обработка, ансамбли).

---

## 2026-03-13 | C4 – выравнивание формата данных и сабмишена с реальными файлами соревнования

### Goal

- Начать следующий цикл работы над CayleyPy-444-Cube по пользовательскому запросу:
  - перечитать профильные md-документы;
  - внимательно посмотреть, что уже реализовано в подпроекте;
  - выровнять генераторы сабмишена и автосабмит по реальным файлам соревнования (`data/test.csv`, `data/sample_submission.csv`), чтобы всё строго соответствовало Kaggle.

### Read / surveyed

- Корневые документы:
  - `README.md`
  - `PROJECT_MAP.md`
  - `DOCUMENTATION_INDEX.md`
  - `KAGGLE_TOPICS_ARCHIVE.md`
  - `KAGGLE_AUTONOMOUS_WORKFLOW.md`
  - `USER_PROMPTS_LOG.md` (добавлен Prompt 004 с формулировкой запроса про 444‑кубик)
- Подпроект `CayleyPy_444_Cube/`:
  - `README.md`
  - `docs/01_COMPETITION_OVERVIEW.md`
  - `docs/02_AUTOSUBMIT_SETUP.md`
  - `docs/03_STATE_AND_GROUP_STRUCTURE.md`
  - `docs/04_POTENTIAL_HYPOTHESES.md`
  - `docs/05_NN_HYBRID_SOLVER_PLAN.md`
  - `docs/06_EXPERIMENT_WORKFLOW.md`
  - `docs/07_MATH_TRACK_INTEGRATION.md`
  - `docs/08_LEADERBOARD_STRATEGY.md`
  - `docs/09_ENGINEERING_SUMMARY.md`
  - `docs/10_MATH_SUMMARY.md`
  - Код: `search/moves.py`, `search/solver_random_beam.py`, `generate_dummy_submission.py`, `run_experiment.py`, `run_best.py`

### Main findings

- Инженерный и математический каркас для C4 уже развёрнут: есть autosubmit‑модуль, dummy‑генератор, search‑скелет, NN‑интерфейсы, раннеры и профильные доки.
- Реальные файлы соревнования в подпроекте (через zip и `data/`) используют схему:
  - `data/test.csv`: колонки `initial_state_id`, `initial_state`, `comment`;
  - `data/sample_submission.csv`: колонки `initial_state_id`, `path`.
- Текущие доки и код (генераторы, autosubmit, тесты) во многих местах продолжают опираться на старый контракт `id`/`solution` и на вымышленную колонку `state`, а также ожидают `test.csv` в корне подпроекта, а не под `data/`.
- Субагент по `CayleyPy_444_Cube/` (engineering/explore) провёл аудит подпроекта и реальных CSV и вернул подробное техзадание на выравнивание: смена колонок на `initial_state_id`/`path`, переход на `data/test.csv`, обновление `submission/autosubmit.py` и `tests/test_submission_format.py`, а также пересборка соответствующих разделов доков.

### Decisions

- Зафиксировано, что **источником правды** по формату данных для C4 являются локальные файлы Kaggle‑соревнования в `CayleyPy_444_Cube/data/`:
  - тест: `initial_state_id`, `initial_state`, `comment`;
  - сабмишен: `initial_state_id`, `path`.
- Принято, что:
  - все генераторы сабмишена в подпроекте (`generate_dummy_submission.py`, `solve_with_search.py`, `run_experiment.py`, `run_best.py`) должны работать относительно `data/test.csv` и производить `submission.csv` со столбцами `initial_state_id` и `path`;
  - модуль `submission/autosubmit.py` и локальные тесты должны валидировать именно эту схему;
  - профильные доки (`README.md`, `docs/01_*.md`, `docs/02_*.md`, `docs/09_*.md`) должны быть обновлены так, чтобы их «hard interface contract» совпадал с реальными CSV, а старый контракт `id`/`solution` явно считался устаревшим.
- Выделены две отдельные задачи на следующие шаги:
  - подтверждение реального Kaggle‑slug соревнования и синхронизация его с `DEFAULT_KAGGLE_COMPETITION` в autosubmit‑модуле и доках;
  - расшифровка и формализация языка путей в колонке `path` (токены вида `f1`, `-d3.-r3`) и выравнивание поискового скелета (`search/moves.py`) с этим форматом.

### Files created or updated

- В корне:
  - `USER_PROMPTS_LOG.md` (добавлен Prompt 004 — запрос пользователя начать работу над 444‑кубиком с опорой на реальные файлы соревнования)
  - `RESEARCH_JOURNAL.md` (эта запись)
- В подпроекте `CayleyPy_444_Cube/` на этом шаге изменений не вносилось (субагент работал в режиме анализа; правки кода и доков запланированы отдельно).

### Risks / unknowns

- Фактический slug Kaggle‑соревнования всё ещё не подтверждён (в autosubmit и доках используется рабочее предположение `cayleypy-444-cube`).
- Семантика колонки `path` (набор генераторов, кодирование направления и шага, разделители) пока только угадывается по `sample_submission.csv`; без точной спецификации тяжело связать её с внутренними представлениями `search/` и NN‑слоя.
- Текущие генераторы и валидатор продолжают использовать старую схему (`id`/`solution`, `test.csv` в корне); до применения правок возможны несоответствия между локальными сабмишенами и требованиями конкурса.

### Next step

- В подпроекте `CayleyPy_444_Cube/`:
  - применить предлагаемые субагентом правки к `generate_dummy_submission.py`, `solve_with_search.py`, `run_experiment.py`, `run_best.py`, `submission/autosubmit.py`, `tests/test_submission_format.py` и профильным докам, чтобы всё выровнять под `initial_state_id`/`path` и `data/test.csv`;
  - подтвердить Kaggle‑slug через веб‑интерфейс и обновить autosubmit и документацию;
  - начать обратную инженерии языка `path` и спроектировать слой отображения между внутренними ходами поискового солвера и строками `path`.

---

## 2026-03-13 | C4 – боевой солвер и submission pipeline

### Goal

Довести CayleyPy-444-Cube до рабочего решения и подтверждённой отправки на Kaggle (Prompt 006).

### Decisions

1. **Движок** (`cube_engine.py`): `parse_state`, `apply_move`, `apply_path`, `is_solved`, `hamming_to_solved` на базе `puzzle_info.json`.
2. **Поиск** (`search/solver_beam.py`): state-aware beam search; двухступенчатый pipeline (fast pass → hard retry); retries с разными seeds.
3. **Интеграция**: `solve_with_search` использует `solve_batch_two_stage`; fallback non-empty path.
4. **Kaggle**: поддержка `kaggle (1).json`; `_ensure_kaggle_env` в main.py.

### Files created/updated

- `cube_engine.py`, `search/solver_beam.py`
- `solve_with_search.py`, `main.py`, `submission/autosubmit.py`
- `docs/SUBMISSION_GUIDE.md`, `README.md`
- `USER_PROMPTS_LOG.md`, `RESEARCH_JOURNAL.md`

---

## 2026-03-17 | Root-level architecture redesign for autonomous subproject teams

### Goal

Подготовить первый архитектурный этап новой мультиагентной системы:

- глубоко изучить весь workspace;
- использовать `CayleyPy_Pancake/` как engineering reference;
- использовать `Math_Hypothese_AutoCheck_Witch_Agents/` как scientific-memory reference;
- вынести корневые markdown-документы в `rules/`;
- описать архитектуру root orchestrator, локальных project teams и MCP stack;
- сохранить всё в форме подробных md-документов, пригодных как база для следующего этапа кодогенерации.

### Read / surveyed

- обязательные root docs;
- ключевые docs и entrypoints `CayleyPy_Pancake/`;
- ключевые docs `Math_Hypothese_AutoCheck_Witch_Agents/`;
- официальные внешние источники по MCP, Kaggle API и scholarly APIs.

### Main findings

- `CayleyPy_Pancake/` уже содержит зрелые engineering patterns для будущей системы: entrypoints, experiment loop, evaluate/log/summarize discipline.
- `Math_Hypothese_AutoCheck_Witch_Agents/` уже содержит сильные patterns scientific memory: inbox, atomic cards, multimodel analysis, formalization path.
- Пользователь уточнил главный инвариант: каждый подпроект должен оставаться автономной локальной системой со своей мультиагентной командой.
- Полное физическое удаление или перенос root markdown оказался частично ограничен файловым доступом; поэтому канонические версии помещены в `rules/`, а корень будет использовать compatibility shims.

### Decisions

1. Root layer определяется строго как coordination layer, а не как третий рабочий подпроект.
2. `rules/` становится каноническим root documentation layer.
3. `main.py` остаётся единственным top-level entrypoint.
4. MCP strategy строится вокруг shared neutral servers и custom bridges для Kaggle и research APIs.

### Files created or updated

- `rules/architecture/ROOT_MULTIAGENT_ARCHITECTURE.md`
- `rules/architecture/SUBPROJECT_TEAM_PROTOCOL.md`
- `rules/architecture/MCP_SERVER_STRATEGY.md`
- `rules/architecture/PHASE_1_EXECUTION_PLAN.md`
- `rules/architecture/ROOT_LAYOUT_AND_MIGRATION.md`
- root-level rule docs updated to reflect the new invariant

### Risks / unknowns

- Generic root runtime is not implemented yet; this step defines contracts, not full execution.
- A production-grade `kaggle-bridge` MCP and `papers-bridge` MCP still need implementation.

### Next step

- Implement the root runtime skeleton while preserving local autonomy of all subprojects.

---

## 2026-03-17 | Root-level scaffold, rules migration and phase-1 launcher

### Goal

Довести первый этап root-level перестройки до рабочего состояния:

- сделать `rules/` каноническим деревом root-level документов;
- зафиксировать строгую границу root orchestrator vs autonomous subproject teams;
- подготовить root launcher и минимальный orchestration scaffold;
- сохранить научную трассируемость текущей архитектурной сессии.

### Read / surveyed

- обязательные root docs;
- `CayleyPy_Pancake/` как engineering reference;
- `Math_Hypothese_AutoCheck_Witch_Agents/` как scientific-memory reference;
- текущий корневой layout и root entrypoint;
- официальные внешние источники по MCP, Kaggle API и Playwright.

### Main findings

- Корень уже частично перестраивался, но часть root docs и индексов содержала миграционный шум и старые пути (`rules/policies`, `rules/memory`, numbered architecture docs).
- Для реальной первой итерации достаточно root launcher, который умеет:
  - видеть изолированные подпроекты;
  - разбирать intake markdown;
  - делегировать запуск в локальные `main.py`;
  - не вторгаться во внутренние project workflows.
- Физическое удаление оставшихся root duplicates (`RESEARCH_JOURNAL.md`, `EXPERIMENT_LOGGING_STANDARD.md`) ограничено файловыми правами текущей среды; поэтому canonical copies живут в `rules/`, а корневые файлы рассматриваются как compatibility shims до отдельной очистки.

### Decisions

1. `rules/` закреплён как canonical root documentation layer.
2. Root launcher переведён на пакет `workspace_orchestrator/`.
3. Root discovery учитывает только реальные подпроекты и игнорирует технические временные директории.
4. Правило контроля изменений зафиксировано отдельно: writes делает root orchestrator или субагент по его прямой указке.

### Files created or updated

- `README.md`
- `AGENTS.md`
- `main.py`
- `kaggle_intake/README.md`
- `rules/README.md`
- `rules/core/PROJECT_MAP.md`
- `rules/core/DOCUMENTATION_INDEX.md`
- `rules/workflows/KAGGLE_AUTONOMOUS_WORKFLOW.md`
- `rules/standards/SUBAGENT_STANDARD_PROMPT.md`
- `rules/registry/KAGGLE_TOPICS_ARCHIVE.md`
- `rules/architecture/README.md`
- `rules/architecture/ROOT_RESTRUCTURE_PLAN.md`
- `rules/architecture/ROOT_LAYOUT_AND_MIGRATION.md`
- `rules/architecture/ROOT_MULTIAGENT_ARCHITECTURE.md`
- `rules/architecture/SUBPROJECT_TEAM_PROTOCOL.md`
- `rules/architecture/AGENT_PROTOCOLS.md`
- `rules/architecture/KAGGLE_RESEARCH_AGENT_BLUEPRINT.md`
- `rules/architecture/MCP_SERVER_STRATEGY.md`
- `rules/architecture/IMPLEMENTATION_ROADMAP.md`
- `rules/architecture/PHASE_1_EXECUTION_PLAN.md`
- `workspace_orchestrator/__init__.py`
- `workspace_orchestrator/models.py`
- `workspace_orchestrator/workspace.py`
- `workspace_orchestrator/intake.py`
- `workspace_orchestrator/cli.py`
- `tests/test_intake_parser.py`
- `tests/test_workspace_discovery.py`

### Verification

- `py main.py overview`
- `py main.py list-subprojects`
- `py main.py parse-intake kaggle_intake\_TEMPLATE_KAGGLE_INPUT.md`
- `py -m pytest -q tests\test_intake_parser.py tests\test_workspace_discovery.py`

### Verification notes

- Root launcher commands worked as expected.
- Tests passed: `2 passed`.
- Pytest emitted a cache warning due directory creation oddities in the environment, but test results themselves were successful.

### Risks / unknowns

- `rules/core/DOCUMENTATION_INDEX.md` still contains a legacy body below the new canonical section; it is now safe to read, but deserves later cleanup.
- Kaggle control bridge and papers bridge are not implemented yet; this stage defines the skeleton and contracts.

### Final cleanup update

- Elevated cleanup removed the remaining root duplicate markdown files.
- Temporary pytest cache folders were removed from the workspace root.
- Non-canonical duplicate files under `rules/` plus legacy `memory/` and `policies/` directories were removed.
- Canonical root structure is now physically aligned with the intended layout: bootstrap files in root, canonical docs in `rules/`, isolated subprojects in sibling folders.

### Next step

- Реализовать handoff package generation и root-level delegate flows поверх текущего `workspace_orchestrator/`.

---

## 2026-03-17 | Official framework research and phase-2 architecture freeze

### Goal

Подготовить следующий шаг к coding phase так, чтобы:

- финальная цель root-level multi-agent system была зафиксирована явно;
- выбор официального framework был подтверждён источниками;
- состав root team и subproject teams был описан до coding;
- communication protocols и tool/MCP strategy были вынесены в канонические документы;
- следующая реализация шла через TDD и могла быть согласована с пользователем до активного coding.

### Read / surveyed

- обязательные root docs и текущие architecture docs;
- текущий root scaffold `workspace_orchestrator/`;
- `CayleyPy_Pancake/` как engineering reference;
- `Math_Hypothese_AutoCheck_Witch_Agents/` как scientific-memory reference;
- official OpenAI docs:
  - [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
  - [Agent orchestration](https://openai.github.io/openai-agents-python/multi_agent/)
  - [Using tools](https://platform.openai.com/docs/guides/tools)
  - [Remote MCP guide](https://platform.openai.com/docs/guides/tools-remote-mcp)
  - [Tracing](https://openai.github.io/openai-agents-python/tracing/)
- supporting primary sources:
  - [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
  - [Official Kaggle API repository](https://github.com/Kaggle/kaggle-api)
  - [arXiv API User Manual](https://info.arxiv.org/help/api/user-manual.html)
  - [Semantic Scholar API](https://api.semanticscholar.org/api-docs/)
  - [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)

### Subagent research inputs

- `Avicenna` провёл read-only exploration `CayleyPy_Pancake/` и подтвердил ценность:
  - single operational CLI;
  - experiment dispatcher;
  - resumable research loop;
  - artifact discipline;
  - operator notifications;
  - test stratification.
- `Mendel` провёл read-only exploration `Math_Hypothese_AutoCheck_Witch_Agents/` и подтвердил ценность:
  - docs-first local memory;
  - inbox -> cards -> reports pipeline;
  - multimodel analysis with restricted writes;
  - strict separation between local working memory and export-to-root summary.
- `Locke` провёл read-only audit current root scaffold и зафиксировал основные gaps:
  - нет исполнимых runtime contracts;
  - нет real handoff/result protocol;
  - нет delegation runtime beyond subprocess wrapper;
  - нет automatic root log integration;
  - нет TDD coverage around orchestration and boundaries.

### Main findings

- Лучший официальный foundation для системы - `OpenAI Agents SDK` поверх Responses API/tool layer, а не самодельный orchestration framework.
- Главная архитектурная форма подтверждена: root = coordination layer; subprojects = autonomous local systems.
- Для root выгодно сочетать:
  - code-first routing and contracts;
  - manager-style orchestration;
  - selective handoffs;
  - built-in tracing.
- Для v1 не нужно перегружать стек множеством MCP servers; разумнее стартовать с hosted tools, local filesystem/repo access и custom bridges для Kaggle/papers.
- Следующая engineering phase должна начинаться с TDD contracts/router/delegation/handoff/logging, а не с попытки сразу "оживить" всю автономию.

### Decisions

1. Рекомендовать `OpenAI Agents SDK` как canonical framework choice для root and local multi-agent teams.
2. Зафиксировать финальную цель root runtime в отдельном design document.
3. Зафиксировать recommended root team и subproject team topology в отдельном design document.
4. Зафиксировать explicit TDD implementation plan в отдельном design document.
5. Уточнить `MCP_SERVER_STRATEGY.md` так, чтобы hosted tools и approval/logging policy были частью design.

### Files created or updated

- `rules/architecture/RESEARCH_AND_DESIGN_PROGRAM.md`
- `rules/architecture/OPENAI_AGENTS_SDK_DECISION.md`
- `rules/architecture/TEAM_TOPOLOGY_AND_RUNTIME_PROTOCOLS.md`
- `rules/architecture/PHASE_2_TDD_IMPLEMENTATION_PLAN.md`
- `rules/architecture/MCP_SERVER_STRATEGY.md`
- `rules/architecture/README.md`
- `rules/core/DOCUMENTATION_INDEX.md`
- `rules/logs/USER_PROMPTS_LOG.md`
- `rules/logs/AGENT_INTERACTIONS_LOG.md`
- этот файл

### Risks / unknowns

- Архитектурное направление теперь существенно лучше зафиксировано, но ещё не утверждено пользователем.
- Реальная интеграция с Agents SDK и bridges пока не реализована; этот шаг посвящён design freeze, а не production code.
- Понадобится отдельное решение по approval policy для первого реального Kaggle submit.
- Нужно будет решить, какие root roles сразу делать полноценными agents, а какие временно оставить кодовыми utilities.

### Next step

- Обсудить с пользователем ключевые решения:
  - recommended root team composition;
  - recommended subproject team composition;
  - boundary protocols;
  - v1 tool/MCP stack;
  - approval gates.
- После approval перейти к TDD implementation phase.

---

## 2026-03-17 | Hierarchical department model and code-enforced visibility

### Goal

Уточнить architecture phase после нового пользовательского запроса:

- уйти от слишком "плоской" topology;
- перейти к department-based hierarchy;
- формализовать multi-level access control;
- завести отдельное organizational tree с папками департаментов;
- встроить ACL и visibility enforcement в TDD roadmap.

### Read / surveyed

- `rules/architecture/TEAM_TOPOLOGY_AND_RUNTIME_PROTOCOLS.md`
- `rules/architecture/AGENT_PROTOCOLS.md`
- `rules/architecture/RESEARCH_AND_DESIGN_PROGRAM.md`
- `rules/architecture/PHASE_2_TDD_IMPLEMENTATION_PLAN.md`
- свежие требования пользователя по department hierarchy, audit flow, history agents и code-enforced isolation

### Main findings

- Предыдущая simplified topology хороша как minimal baseline, но недостаточна для целевой системы пользователя.
- Требуется explicit organizational model:
  - root orchestrator;
  - 7-8 root departments;
  - heads as coordination boundary;
  - shared service agents;
  - mirrored but domain-specific subproject hierarchy.
- ACL/visibility model должна стать first-class частью runtime, а не только policy prose.
- Наличие separate history/editorial function на root и subproject уровне должно быть зафиксировано как обязательный элемент research workflow.

### Decisions

1. Зафиксировать root target как 25-agent organization:
   - 1 `Root Orchestrator`
   - 8 departments
   - 1 head + 2 staff in each department
2. Зафиксировать subproject target как 33-agent organization:
   - 1 `Subproject Commander`
   - 8 departments
   - 1 head + 3 staff in each department
3. Завести root organizational tree в `rules/organization/`.
4. Создать отдельный architecture doc для hierarchical department model.
5. Создать отдельный architecture doc для access control and visibility model.
6. Включить manifests, ACL, visibility gateways и communication graph в следующую TDD phase.

### Files created or updated

- `rules/architecture/HIERARCHICAL_DEPARTMENT_MODEL.md`
- `rules/architecture/ACCESS_CONTROL_AND_VISIBILITY_MODEL.md`
- `rules/organization/README.md`
- `rules/organization/root_command/README.md`
- `rules/organization/root_departments/README.md`
- `rules/organization/root_departments/*/README.md`
- `rules/organization/subproject_template_departments/README.md`
- `rules/organization/subproject_template_departments/*/README.md`
- `rules/architecture/AGENT_PROTOCOLS.md`
- `rules/architecture/TEAM_TOPOLOGY_AND_RUNTIME_PROTOCOLS.md`
- `rules/architecture/PHASE_2_TDD_IMPLEMENTATION_PLAN.md`
- `rules/architecture/RESEARCH_AND_DESIGN_PROGRAM.md`
- `rules/README.md`
- `rules/core/DOCUMENTATION_INDEX.md`
- этот файл

### Risks / unknowns

- Численность иерархии уже реалистично отражает цель пользователя, но техническая реализация такого масштаба потребует постепенного ввода manifests, ACL и runtime gateways.
- Нужно будет отдельно решить, какие staff roles должны быть shared service agents в v1, а какие лучше держать strictly departmental.
- В дальнейшем потребуется решить, как именно материализовать скрытие файлов:
  - через filtered file gateway;
  - через отдельные workspace views;
  - или через combined manifest + adapter layer.

### Next step

- Утвердить с пользователем department model, shared service exceptions и access-control principles.
- После approval перейти к coding phase, начиная с manifest/ACL contracts и tests.

---

## 2026-03-17 | Phase 2 implementation start - agent manifests, ACL and visibility runtime

### Goal

Начать actual implementation after architecture approval:

- материализовать hierarchy в коде;
- создать manifests для root и subproject organizations;
- создать ACL и visibility policies;
- добавить CLI inspection commands;
- закрыть всё это тестами.

### Read / surveyed

- `workspace_orchestrator/models.py`
- `workspace_orchestrator/cli.py`
- `workspace_orchestrator/workspace.py`
- существующие root tests
- new architecture docs:
  - `HIERARCHICAL_DEPARTMENT_MODEL.md`
  - `ACCESS_CONTROL_AND_VISIBILITY_MODEL.md`
  - `PHASE_2_TDD_IMPLEMENTATION_PLAN.md`

### Implementation decisions

1. Начать не с полного Agents SDK runtime, а с более фундаментального слоя:
   - manifests;
   - communication ACL;
   - path visibility;
   - write scopes;
   - inspection CLI.
2. Реализовать root target organization на 25 agents и subproject organization на 33 agents.
3. Завести explicit ids для агентов:
   - `root.orchestrator`
   - `root.<department>.head`
   - `root.<department>.<staff>`
   - `subproject.<name>.commander`
   - `subproject.<name>.<department>.head`
   - `subproject.<name>.<department>.<staff>`
4. Реализовать first-class shared service agents как часть call graph.
5. Инспектировать всё это через новые CLI команды, а не только через unit tests.

### Files created or updated

- `workspace_orchestrator/organization.py`
- `workspace_orchestrator/acl.py`
- `workspace_orchestrator/visibility.py`
- `workspace_orchestrator/communications.py`
- `workspace_orchestrator/cli.py`
- `tests/test_organization.py`
- `tests/test_acl.py`
- `tests/test_visibility.py`
- `tests/test_communications.py`
- `rules/logs/USER_PROMPTS_LOG.md`
- этот файл

### Verification

- `py -m pytest -q -p no:cacheprovider tests\test_organization.py tests\test_acl.py tests\test_visibility.py tests\test_communications.py tests\test_intake_parser.py tests\test_workspace_discovery.py`
- `py main.py org-summary`
- `py main.py callable-targets root.03_architecture_and_capability.rule_engineer`
- `py main.py org-summary --project CayleyPy_444_Cube`
- `py main.py check-path root.06_editorial_and_history.history_scribe rules\logs\RESEARCH_JOURNAL.md --mode read`
- `py main.py can-call subproject.CayleyPy_444_Cube.commander root.orchestrator`

### Verification notes

- Tests passed: `11 passed`.
- CLI inspection commands returned the expected organization scale and permissions.
- Root summary reports `25` agents.
- Subproject summary reports `33` agents.

### Risks / unknowns

- Это ещё не полный runtime на Agents SDK; пока реализован organization and policy substrate.
- Write scopes пока intentionally conservative и опираются на `.agent_workspace` plus selected allowed roots.
- Следующим шагом потребуется связать manifests/ACL с handoff/result cycle и затем с actual Agents SDK adapter layer.

### Next step

- Реализовать runtime contracts for department manifests and change requests.
- Подключить manifests/ACL к delegation/handoff layer.
- После этого переходить к OpenAI Agents SDK adapter for real team activation.

---

## 2026-03-17 | Phase 2 implementation continuation - root-owned handoff lifecycle

### Goal

Continue the implementation phase after the manifest/ACL substrate and turn the new hierarchy into an operational root-controlled delegation cycle:

- prepare structured handoff packages;
- persist them in root-owned run directories;
- record structured delegation results;
- expose the lifecycle through root CLI commands;
- verify the flow with both tests and live smoke runs.

### Read / surveyed

- `README.md`
- `rules/core/PROJECT_MAP.md`
- `rules/core/RESEARCH_SURVEY.md`
- `rules/core/DOCUMENTATION_INDEX.md`
- `rules/logs/USER_PROMPTS_LOG.md`
- `workspace_orchestrator/cli.py`
- `workspace_orchestrator/handoff.py`
- `workspace_orchestrator/contracts.py`
- `workspace_orchestrator/runs.py`
- `tests/test_handoff.py`
- `tests/test_contracts.py`
- `rules/architecture/AGENT_PROTOCOLS.md`
- `rules/architecture/PHASE_2_TDD_IMPLEMENTATION_PLAN.md`

### Implementation decisions

1. Keep all handoff runtime artifacts under root ownership in `.agent_workspace/runs/<run_id>/`.
2. Add a dedicated delegation layer instead of overloading the CLI with ad hoc JSON file manipulation.
3. Treat `trace.json` as the canonical status register of a run and `delegation_result.json` as the canonical return package.
4. Expose only a small operational surface for now:
   - `build-handoff`
   - `show-run`
   - `record-result`
5. Use `root.02_research_intelligence.head` as the default requester for research-oriented subproject handoffs, matching the approved department hierarchy more closely than `root.orchestrator`.

### Files created or updated

- `workspace_orchestrator/delegation.py`
- `workspace_orchestrator/runs.py`
- `workspace_orchestrator/cli.py`
- `tests/test_delegation.py`
- `tests/test_cli_runtime.py`
- `rules/architecture/AGENT_PROTOCOLS.md`
- `rules/architecture/PHASE_2_TDD_IMPLEMENTATION_PLAN.md`
- `rules/logs/USER_PROMPTS_LOG.md`
- this file

### Verification

- `py -m pytest -q -p no:cacheprovider tests\test_organization.py tests\test_acl.py tests\test_visibility.py tests\test_communications.py tests\test_intake_parser.py tests\test_workspace_discovery.py tests\test_contracts.py tests\test_handoff.py tests\test_delegation.py tests\test_cli_runtime.py`
- `py main.py build-handoff --project CayleyPy_444_Cube --objective "Smoke-validate root handoff lifecycle" --intake-file kaggle_intake\First_input.md --json`
- `py main.py show-run run-0c9af585bdbc --json`
- `py main.py record-result run-0c9af585bdbc --produced-by subproject.CayleyPy_444_Cube.commander --status completed --summary "Smoke runtime validation completed." --canonical-path CayleyPy_444_Cube/docs/01_COMPETITION_OVERVIEW.md --json`
- `py main.py show-run run-0c9af585bdbc --json`

### Verification notes

- Full root test suite passed: `19 passed`.
- New targeted runtime tests passed: `5 passed`.
- Live smoke run was materialized at `.agent_workspace/runs/run-0c9af585bdbc`.
- The smoke run confirmed the expected artifact progression:
  - prepared handoff package
  - trace inspection
  - delegation result recording
  - trace transition to `completed`

### Risks / unknowns

- The delegated local runtime is not yet launched automatically from the run package; current result recording is still an explicit root-side action.
- Root logs are still updated manually rather than by an automatic run-completion ingestion layer.
- There is still no OpenAI Agents SDK adapter connected to this control plane.
- Failure-path handling for subprocess timeouts, non-zero exits and malformed result bundles is still pending.

### Next step

- Implement the execution adapter that consumes a prepared handoff package and launches the delegated local runtime safely.
- Add structured failure ingestion and trace transitions for runtime errors.
- After that, connect this control plane to the first OpenAI Agents SDK runtime adapter.

---

## 2026-03-17 | Phase 2 implementation continuation - execution adapter and integration dry run

### Goal

Move from passive handoff storage to actual root-controlled activation of delegated local runtimes:

- consume prepared handoff runs;
- launch the corresponding subproject `main.py` safely;
- capture execution artifacts in the root-owned run directory;
- support compatibility mode for legacy subprojects;
- add integration coverage for a root-to-subproject dry run.

### Read / surveyed

- `workspace_orchestrator/delegation.py`
- `workspace_orchestrator/contracts.py`
- `workspace_orchestrator/cli.py`
- `workspace_orchestrator/organization.py`
- `CayleyPy_444_Cube/main.py`
- `rules/architecture/AGENT_PROTOCOLS.md`
- `rules/architecture/PHASE_2_TDD_IMPLEMENTATION_PLAN.md`

### Implementation decisions

1. Introduce a dedicated execution layer instead of embedding subprocess logic directly into the CLI.
2. Formalize execution metadata via `ExecutionRecord`.
3. Add a root-side runtime registry with execution profiles:
   - `protocol_v1` for handoff-aware fixture or future subprojects;
   - `legacy` compatibility mode for current `CayleyPy_444_Cube`.
4. Make the legacy profile safety-biased by default:
   - current compatibility command for `CayleyPy_444_Cube` includes `--no-submit`.
5. Keep all execution artifacts root-owned inside the run directory.
6. If a protocol-aware subproject writes `subproject_result.json`, ingest it automatically into canonical `delegation_result.json`.

### Files created or updated

- `workspace_orchestrator/execution.py`
- `workspace_orchestrator/runtime_registry.py`
- `workspace_orchestrator/contracts.py`
- `workspace_orchestrator/delegation.py`
- `workspace_orchestrator/cli.py`
- `tests/test_contracts.py`
- `tests/test_execution.py`
- `tests/integration/test_root_dry_run.py`
- `rules/architecture/AGENT_PROTOCOLS.md`
- `rules/architecture/PHASE_2_TDD_IMPLEMENTATION_PLAN.md`
- `rules/logs/USER_PROMPTS_LOG.md`
- this file

### Verification

- `py -m pytest -q -p no:cacheprovider tests\test_contracts.py tests\test_execution.py tests\integration\test_root_dry_run.py`
- `py -m pytest -q -p no:cacheprovider tests\test_organization.py tests\test_acl.py tests\test_visibility.py tests\test_communications.py tests\test_intake_parser.py tests\test_workspace_discovery.py tests\test_contracts.py tests\test_handoff.py tests\test_delegation.py tests\test_cli_runtime.py tests\test_execution.py tests\integration\test_root_dry_run.py`
- `py main.py build-handoff --project CayleyPy_444_Cube --objective "Smoke-validate execution adapter" --intake-file kaggle_intake\First_input.md --json`
- `py main.py execute-run run-11e576a9cddc --dry-run --json`
- `py main.py show-run run-11e576a9cddc --json`

### Verification notes

- New execution-focused tests passed: `7 passed`.
- Full root test suite passed: `25 passed`.
- Integration coverage now includes a fixture subproject that completes an end-to-end root CLI flow:
  - `build-handoff`
  - `execute-run`
  - `show-run`
- Real workspace smoke confirmed that:
  - a run can be prepared for `CayleyPy_444_Cube`;
  - `execute-run --dry-run` materializes a compatibility execution record;
  - the planned legacy command is safety-biased with `--no-submit`;
  - `trace.json` transitions to `dry_run`.

### Risks / unknowns

- `CayleyPy_444_Cube/main.py` is still legacy and not yet root-handoff aware.
- Automatic root log ingestion from run completion is still not implemented.
- Incoming malformed `subproject_result.json` handling is still basic and should be hardened.
- The OpenAI Agents SDK team activation layer is still pending above this substrate.

### Next step

- Add root log ingestion helpers that update canonical logs directly from run completion and failure events.
- After that, connect the execution substrate to the first OpenAI Agents SDK root-team adapter.

---

## 2026-03-17 | Phase 2 implementation continuation - automatic root log sync

### Goal

Close the gap between run artifacts and canonical root memory:

- sync execution events into root logs automatically;
- sync result-ingestion events into root logs automatically;
- keep the sync idempotent;
- preserve `.agent_workspace/runs/<run_id>/` as canonical artifact storage.

### Read / surveyed

- `rules/logs/RESEARCH_JOURNAL.md`
- `rules/logs/AGENT_INTERACTIONS_LOG.md`
- `workspace_orchestrator/delegation.py`
- `workspace_orchestrator/execution.py`
- `tests/integration/test_root_dry_run.py`

### Implementation decisions

1. Keep log synchronization in a dedicated root module instead of mixing markdown appends into runtime logic.
2. Synchronize only summaries into root logs; raw runtime artifacts stay in run directories.
3. Track idempotence per run/event via `log_sync_state.json`.
4. Sync two event categories for now:
   - execution
   - result
5. Update `RESEARCH_JOURNAL.md` and `AGENT_INTERACTIONS_LOG.md` automatically, but leave `USER_PROMPTS_LOG.md` user-driven.

### Files created or updated

- `workspace_orchestrator/root_logs.py`
- `workspace_orchestrator/delegation.py`
- `workspace_orchestrator/execution.py`
- `tests/test_root_logs.py`
- `tests/integration/test_root_dry_run.py`
- `rules/architecture/AGENT_PROTOCOLS.md`
- `rules/architecture/PHASE_2_TDD_IMPLEMENTATION_PLAN.md`
- `rules/logs/USER_PROMPTS_LOG.md`
- this file

### Verification

- `py -m pytest -q -p no:cacheprovider tests\test_root_logs.py tests\test_execution.py tests\integration\test_root_dry_run.py`
- `py -m pytest -q -p no:cacheprovider tests\test_organization.py tests\test_acl.py tests\test_visibility.py tests\test_communications.py tests\test_intake_parser.py tests\test_workspace_discovery.py tests\test_contracts.py tests\test_handoff.py tests\test_delegation.py tests\test_cli_runtime.py tests\test_execution.py tests\test_root_logs.py tests\integration\test_root_dry_run.py`
- `py main.py build-handoff --project CayleyPy_444_Cube --objective "Smoke-validate automatic root log sync" --intake-file kaggle_intake\First_input.md --json`
- `py main.py execute-run run-fc8dc0e0c870 --dry-run --json`
- `py main.py show-run run-fc8dc0e0c870 --json`
- `rg -n "run-fc8dc0e0c870|execution:dry_run" rules\logs\RESEARCH_JOURNAL.md rules\logs\AGENT_INTERACTIONS_LOG.md`

### Verification notes

- New root-log-focused tests passed.
- Full root test suite passed: `28 passed`.
- Real workspace dry-run created log sync state in `.agent_workspace/runs/run-fc8dc0e0c870/log_sync_state.json`.
- Real workspace logs now contain synchronized entries for `run-fc8dc0e0c870` in:
  - `RESEARCH_JOURNAL.md`
  - `AGENT_INTERACTIONS_LOG.md`

### Risks / unknowns

- `USER_PROMPTS_LOG.md` is intentionally not auto-filled from runs and remains a separate discipline.
- Malformed `subproject_result.json` hardening is still basic.
- Topic/archive updates from run completion are still not automated.
- The OpenAI Agents SDK adapter is still pending above the current substrate.

### Next step

- Build the first OpenAI Agents SDK root-team adapter on top of the existing control plane.
- Then connect handoff preparation, execution and log sync to real agent activation flows.


## 2026-03-17 | Automated run sync | run-fc8dc0e0c870 | execution:dry_run

### Context

- Project: `CayleyPy_444_Cube`
- Target agent: `subproject.CayleyPy_444_Cube.commander`
- Requester: `root.02_research_intelligence.head`
- Objective: Smoke-validate automatic root log sync

### Trace snapshot

- Status: `dry_run`
- Events: prepared, execution_dry_run
- Artifacts: handoff.json, task_request.json, routing_decision.json, research_plan.json, execution_record.json

### Execution snapshot

- Mode: `legacy`
- Status: `dry_run`
- Command: `C:\Users\Иван Литвак\AppData\Local\Programs\Python\Python311\python.exe D:\Agentic_Solve_Math\CayleyPy_444_Cube\main.py --no-submit`
---

## 2026-03-17 | Phase 2 implementation continuation - OpenAI runtime adapter

### Goal

Add the first real OpenAI-oriented runtime layer above the existing control plane without making the workspace depend on immediate SDK installation.

Target properties:

- inspectable team specs for root and subproject organizations;
- propagation of prepared run metadata into runtime context;
- explicit mapping from hierarchy manifests to handoff/tool targets;
- lazy SDK activation boundary with graceful degraded mode;
- new CLI inspection commands for reproducibility.

### Read / surveyed

- `workspace_orchestrator/organization.py`
- `workspace_orchestrator/handoff.py`
- `workspace_orchestrator/delegation.py`
- `workspace_orchestrator/cli.py`
- `rules/architecture/OPENAI_AGENTS_SDK_DECISION.md`
- official OpenAI docs:
  - `https://openai.github.io/openai-agents-python/`
  - `https://openai.github.io/openai-agents-python/multi_agent/`
  - `https://platform.openai.com/docs/guides/tools`
  - `https://platform.openai.com/docs/guides/tools-remote-mcp`
  - `https://openai.github.io/openai-agents-python/tracing/`

### Implementation decisions

1. Keep the runtime spec as the canonical adapter output so the architecture stays debuggable and article-friendly.
2. Derive tool-style targets only from shared-service agents, while regular callable agents remain handoff targets.
3. Propagate `run_id`, `handoff_id`, `objective`, `target_agent_id` and related metadata into generated agent instructions.
4. Use lazy import of `agents` so the control plane, CLI and tests remain operational when the SDK is absent locally.
5. Materialize only a bounded SDK bundle for a selected entry agent in v1 to avoid pretending that the full cyclic org graph is already solved at activation time.

### Files created or updated

- `workspace_orchestrator/openai_runtime.py`
- `workspace_orchestrator/cli.py`
- `tests/test_openai_runtime.py`
- `tests/integration/test_root_runtime_summary.py`
- `rules/architecture/AGENT_PROTOCOLS.md`
- `rules/architecture/PHASE_2_TDD_IMPLEMENTATION_PLAN.md`
- `rules/architecture/OPENAI_AGENTS_SDK_DECISION.md`
- `rules/logs/USER_PROMPTS_LOG.md`
- this file

### Verification

- `py -m pytest -q -p no:cacheprovider tests\test_openai_runtime.py`
- `py -m pytest -q -p no:cacheprovider tests\integration\test_root_runtime_summary.py`

### Verification notes

- New runtime-adapter-focused tests passed: `4 passed`.
- New integration test for CLI runtime inspection passed: `1 passed`.
- The adapter now reports environment degradation explicitly when `agents` is not installed.
- Root runtime summary can be generated from a real prepared run id without executing the subproject runtime.

### Risks / unknowns

- The local environment still does not have the `agents` package, so live SDK execution is not yet validated here.
- The current SDK bundle materialization is intentionally bounded and not yet a full cycle-aware activation strategy for the entire organization graph.
- Hosted tools, tracing hooks and MCP-backed service adapters are still future layers above the current runtime spec.

### Next step

- Connect the runtime spec layer to a real SDK runner path when the package becomes available.
- Then start wiring hosted tools and bridge services into the root orchestrator entry flow.
