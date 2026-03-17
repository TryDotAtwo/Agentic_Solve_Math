# Kaggle Topics Archive and Index

## Назначение

Этот документ хранит общую сводку по Kaggle-соревнованиям и темам, которые уже прошли через `kaggle_intake/`, и связывает их с подпроектами, доками и артефактами.

Каждая новая тема из intake-файла должна со временем появляться здесь с указанием статуса.

## Структура записи

Для каждой темы (competition) рекомендуется фиксировать:

- ID или короткий slug;
- официальный competition name и URL;
- подпроект (папка) в корне;
- основную цель/метрику;
- статус проработки;
- ключевые документы;
- ссылки на лог экспериментов и математические заметки.

## Статусы

- `planned` — соревнование только добавлено, работа не начата;
- `in_progress` — есть активная работа по подпроекту;
- `paused` — работа временно приостановлена;
- `completed` — цель первого цикла исследований достигнута (baseline/статья/анализ);
- `archived` — подпроект заморожен, тема описана и помещена в архив.

## Таблица тем (первая инициализация)

| ID | Competition | URL | Subproject | Status | Key docs |
|----|-------------|-----|-----------|--------|----------|
| C1 | CayleyPy-Christopher's-Jewel | https://www.kaggle.com/competitions/cayleypy-christophers-jewel | CayleyPy_Christophers_Jewel/ | planned | (TBD) |
| C2 | CayleyPy-Professor-Tetraminx-Solve-Optimally | https://www.kaggle.com/competitions/cayley-py-professor-tetraminx-solve-optimally | CayleyPy_Professor_Tetraminx/ | planned | (TBD) |
| C3 | CayleyPy-IHES-Cube | https://www.kaggle.com/competitions/cayleypy-ihes-cube | CayleyPy_IHES_Cube/ | planned | (TBD) |
| C4 | CayleyPy-444-Cube | https://www.kaggle.com/competitions/cayley-py-444-cube | CayleyPy_444_Cube/ | in_progress | CayleyPy_444_Cube/docs/01_COMPETITION_OVERVIEW.md; 02_AUTOSUBMIT_SETUP.md; 03_STATE_AND_GROUP_STRUCTURE.md; 04_POTENTIAL_HYPOTHESES.md; 06_EXPERIMENT_WORKFLOW.md; 08_LEADERBOARD_STRATEGY.md; 09_ENGINEERING_SUMMARY.md; 10_MATH_SUMMARY.md |
| C5 | CayleyPy-Glushkov | https://www.kaggle.com/competitions/cayleypy-glushkov | CayleyPy_Glushkov/ | planned | (TBD) |
| C6 | CayleyPy-Pancake | https://www.kaggle.com/competitions/CayleyPy-pancake | CayleyPy_Pancake/ | in_progress | CayleyPy_Pancake/docs/*.md |
| C7 | CayleyPy-Megaminx | https://www.kaggle.com/competitions/cayley-py-megaminx | CayleyPy_Megaminx/ | planned | (TBD) |
| C8 | CayleyPy-Rapapport-M2 | https://www.kaggle.com/competitions/cayleypy-rapapport-m2 | CayleyPy_Rapapport_M2/ | planned | (TBD) |
| C9 | CayleyPy-Reversals | https://www.kaggle.com/competitions/cayleypy-reversals | CayleyPy_Reversals/ | planned | (TBD) |
| C10 | CayleyPy-555-Cube | https://www.kaggle.com/competitions/cayley-py-555-cube | CayleyPy_555_Cube/ | planned | (TBD) |
| C11 | CayleyPy-666-Cube | https://www.kaggle.com/competitions/cayley-py-666-cube | CayleyPy_666_Cube/ | planned | (TBD) |
| C12 | CayleyPy-777-Cube | https://www.kaggle.com/competitions/cayley-py-777-cube | CayleyPy_777_Cube/ | planned | (TBD) |
| C13 | CayleyPy-Transposons | https://www.kaggle.com/competitions/cayleypy-transposons | CayleyPy_Transposons/ | planned | (TBD) |

## Архивирование

- Когда подпроект по соревнованию завершён или заморожен, его статус обновляется на `completed` или `archived`.
- В случае архивирования:
  - указать, где лежат основные артефакты (submission, отчёты, код);
  - кратко описать уроки и выводы;
  - при необходимости добавить отдельный архивный md-документ с более подробным обзором.

## Связь с другими документами

- Intake и первичный brief: `../workflows/BASELINE_INTAKE_SPEC.md`, `../workflows/KAGGLE_AUTONOMOUS_WORKFLOW.md`.
- Общий исследовательский контекст: `../logs/RESEARCH_JOURNAL.md`.
- Агентный контракт и маршрутизация: `../../AGENTS.md`.
