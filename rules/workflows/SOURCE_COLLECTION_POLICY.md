# Source Collection Policy

## Цель

Этот документ задаёт правила сбора внешних источников для новых Kaggle-задач и связанных математических исследований.

## Основной принцип

Агент должен собирать источники широко, но документировать их аккуратно и различать по уровню надёжности.

## Категории источников

### 1. Official competition sources

- Kaggle competition page
- official rules
- official data description
- evaluation details
- submission format

Статус по умолчанию:

- `authoritative`

### 2. Public community sources

- Kaggle discussions
- public notebooks
- forum threads
- blog posts

Статус по умолчанию:

- `useful but non-authoritative`

### 3. Technical references

- GitHub repositories
- library docs
- benchmark implementations
- reproducible papers with code

Статус зависит от качества:

- `reference`
- `baseline candidate`
- `needs verification`

### 4. Scientific and mathematical sources

- papers
- books
- survey articles
- lecture notes
- OEIS and formal math references where relevant

Статус зависит от контекста:

- `theoretical reference`
- `proof support`
- `background`

## Что агент должен фиксировать по каждому важному источнику

- название или короткий идентификатор;
- URL или путь;
- тип источника;
- зачем он нужен;
- какому направлению он помогает:
  - engineering;
  - mathematics;
  - both.

## Правило evidence ladder

При конфликте источников приоритет такой:

1. official competition documentation
2. reproducible code and direct experiment logs
3. peer-reviewed or well-established theoretical references
4. strong public notebooks and repos
5. discussions and informal interpretations
6. собственная гипотеза агента

## Что нельзя делать

- Нельзя выдавать public notebook за официальный baseline.
- Нельзя принимать красивую discussion idea без проверки.
- Нельзя переносить теоретическое утверждение в engineering plan без указания, как оно будет верифицировано.
- Нельзя собирать ссылки хаотично без классификации.

## Рекомендуемый выход первичного source collection

После стартового сбора агент должен уметь сформировать:

- curated list of official sources;
- curated list of strong community baselines;
- curated list of scientific references;
- список идей, которые нужно проверить отдельно;
- список источников, которые пока только фоновые.

## Связь с другими документами

- `BASELINE_INTAKE_SPEC.md`
- `KAGGLE_AUTONOMOUS_WORKFLOW.md`
- `RESEARCH_JOURNAL.md`
