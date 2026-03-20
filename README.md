# Agentic Solve Math

Корень `D:\Agentic_Solve_Math` теперь должен пониматься как **meta-layer / coordinator layer**, а не как ещё один предметный проект.

## Архитектурный инвариант

- Каждый подпроект является **самодостаточной и изолированной системой**.
- У каждого подпроекта должны быть:
  - своя локальная документация;
  - свои локальные правила;
  - свой локальный `AGENTS.md`;
  - своя собственная мультиагентная команда.
- Корень **не смешивает** локальные уровни между собой.
- Корень:
  - координирует подпроекты;
  - ведёт глобальную память и трассируемость;
  - принимает новые задачи;
  - проектирует общую архитектуру;
  - решает глобальные cross-project задачи.

## Что находится в корне

- `main.py` — единая root-level точка запуска.
- `runtime_config.toml` — root-level provider and launch config for OpenAI / OpenRouter / g4f.
- `AGENTS.md` — корневой контракт оркестратора.
- `rules/` — canonical дерево корневой документации.
- `kaggle_intake/` — canonical intake для новых Kaggle-задач.
- `workspace_orchestrator/` — код root-level orchestration scaffold.
- подпроекты `CayleyPy_*` и `Math_Hypothese_AutoCheck_Witch_Agents/`.

## Сначала читать

Перед новой содержательной сессией:

1. `README.md`
2. `AGENTS.md`
3. `rules/README.md`
4. `rules/core/PROJECT_MAP.md`
5. `rules/core/RESEARCH_SURVEY.md`
6. `rules/core/DOCUMENTATION_INDEX.md`
7. `rules/logs/USER_PROMPTS_LOG.md`
8. затем локальные документы нужного подпроекта

## Смысл папки `rules/`

`rules/` — это canonical место для корневых:

- карт и индексов;
- workflow/spec документов;
- стандартов;
- журналов и памяти оркестратора;
- архитектурных планов и design notes для следующего этапа разработки.

Подробности: `rules/README.md`.

## Статус root launcher

`main.py` теперь работает в двух режимах:

- если в окружении есть `OPENAI_API_KEY` или в корне лежит `.env`, запуск без аргументов поднимает единый operator session:
  - стартует local dashboard;
  - URL печатается в терминал;
  - браузер открывается автоматически;
  - live root orchestrator запускается в том же процессе;
  - остановка делается из этого же терминала через `Ctrl+C`;
- если bootstrap ещё не настроен, `main.py` остаётся root CLI entrypoint и показывает overview/служебные команды.

Live root launch использует root-level multi-agent runtime из `workspace_orchestrator/`, может читать последний intake, строить handoff-пакеты и активировать generic subproject commander runtime без правки внутренних файлов подпроекта.

### Минимальный запуск

1. Проверить `runtime_config.toml` и выбрать активный provider:
   - `openai`
   - `openrouter`
   - `g4f`
2. Скопировать `.env.example` в `.env`.
3. Заполнить только секреты для выбранного provider.
4. При желании задать `ASM_OPENAI_MODEL` как глобальный override, но по умолчанию лучше оставить per-agent model policy.
5. Запустить:

```bash
python main.py
```

Это теперь основной рекомендуемый запуск:

- всё стартует из одной команды;
- наблюдение и orchestration живут под одним root process;
- отдельный второй терминал больше не нужен.

Поддерживаются и явные команды:

```bash
python main.py launch-root
python main.py dashboard
python main.py sdk-status
python main.py runtime-summary --json
```

По умолчанию runtime сам распределяет модели по ролям:

- для OpenAI:
  - manager / research / audit: `gpt-5.2`
  - coding: `gpt-5.2-codex`
  - history / support: `gpt-5-mini`
- для OpenRouter debug-path по умолчанию используется per-agent curated free-model pool;
- для g4f используется локальный OpenAI-compatible route с отдельным config block;
- model policy остаётся role-aware и provider-aware и может переопределяться без смены root launcher surface.

### Provider config

Canonical runtime config теперь живёт в `runtime_config.toml`.

Он задаёт:

- активный provider;
- dashboard / launch параметры;
- role-aware model tiers;
- OpenRouter free-pool strategy;
- g4f local API auto-start policy.

Для OpenRouter root теперь использует safer refresh policy:

- каталог free-моделей может только подтвердить доступность root-curated pool;
- runtime больше не заменяет локальный curated pool всем каталогом целиком;
- источником истины для отладки остаётся `runtime_config.toml`.

Диагностические команды:

```bash
python main.py provider-status --json
python main.py provider-status --provider openrouter --json
python main.py provider-status --provider g4f --json
```

## Browser Dashboard

Для наблюдения за ходом работ теперь есть отдельный root-level browser dashboard.

По умолчанию он уже поднимается внутри `python main.py`.

Запуск:

```bash
python main.py dashboard
```

Что показывает dashboard:

- bootstrap/provider status;
- dual graph view:
  - root command graph and active subproject graph side by side;
  - explicit bridge surface between the two teams;
- live execution pulse с текущим scope, активным агентом, phase и last event;
- live activity stream по runtime events из root-owned event journal;
- dialogue console со split-view:
  - compact event list;
  - filter chips;
  - detail preview for the selected exchange;
- agent inspector с private memory, base instructions, rules и report surfaces выбранного агента;
- milestone stream из user-facing отчётов глав департаментов;
- последние root-owned handoff/run артефакты;
- root runtime status из `.agent_workspace/runtime/root_runtime_status.json`;
- root runtime events из `.agent_workspace/runtime/root_runtime_events.jsonl`;
- root journals и user prompts;
- карту подпроектов и session storage.

У каждого root-agent теперь есть собственный private profile-root в `.agent_workspace/agent_profiles/`, где материализуются:

- `memory.md` — долговременная приватная память агента;
- `instructions.md` — базовые инструкции роли;
- `rules.md` — правила работы и иерархические ограничения;
- `reports.md` — отчёты и milestone entries для пользовательского dashboard surface.

Рекомендуемый режим работы:

1. Просто выполнить `python main.py`.
2. Дождаться открытия browser dashboard.
3. При необходимости остановить всё через `Ctrl+C` в этом же терминале.

Отдельная команда `python main.py dashboard` остаётся доступной как standalone observability mode, если нужно поднять только UI без live root launch.

Подробная целевая архитектура вынесена в:

- `rules/architecture/ROOT_RESTRUCTURE_PLAN.md`
- `rules/architecture/ROOT_MULTIAGENT_ARCHITECTURE.md`
- `rules/architecture/AGENT_PROTOCOLS.md`
- `rules/architecture/ROOT_OBSERVABILITY_DASHBOARD.md`
- `rules/architecture/MULTIPROVIDER_RUNTIME_CONFIG.md`
- `rules/architecture/KAGGLE_RESEARCH_AGENT_BLUEPRINT.md`
- `rules/architecture/MCP_SERVER_STRATEGY.md`
- `rules/architecture/IMPLEMENTATION_ROADMAP.md`

## Intake для Kaggle

Новые Kaggle-задачи поступают через `kaggle_intake/`.

Root orchestrator обязан:

1. прочитать intake-файл;
2. извлечь competition links, требования, источники и ограничения;
3. зафиксировать запрос и старт ветки исследования;
4. определить, нужен ли новый изолированный подпроект;
5. делегировать локальную работу соответствующей мультиагентной команде подпроекта;
6. сохранить глобальные выводы в корневой памяти.

См. также:

- `rules/workflows/BASELINE_INTAKE_SPEC.md`
- `rules/workflows/KAGGLE_AUTONOMOUS_WORKFLOW.md`
- `rules/workflows/SOURCE_COLLECTION_POLICY.md`

## Подпроекты

- `CayleyPy_Pancake/` — инженерный эталон по UX, beam search, GPU-oriented solve pipeline, логированию и сабмитной дисциплине.
- `CayleyPy_444_Cube/` и другие `CayleyPy_*` — отдельные competition-specific подпроекты.
- `Math_Hypothese_AutoCheck_Witch_Agents/` — эталон memory/research architecture для математической ветки.

Главное правило: корень координирует, подпроекты реализуют.
