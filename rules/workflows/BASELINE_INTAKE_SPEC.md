# Kaggle Intake Spec

## Назначение

Корневой `kaggle_intake/` является канонической входной папкой для новых Kaggle-задач в этом workspace.

Он не предназначен для хранения project-local референсов текущего pancake-проекта. Для этого уже существует `ML in Math/baseline/`.

## Формат входа

Пользователь кладёт в `kaggle_intake/` один или несколько `.md` файлов. Каждый такой файл должен содержать:

- ссылку или ссылки на Kaggle competition;
- при наличии: краткие заметки пользователя;
- при наличии: дополнительные ссылки на notebooks, discussions, papers, repos.

## Что считается корректным intake-файлом

Минимально достаточно:

- одной валидной ссылки на Kaggle competition;
- markdown-формата;
- понятного имени файла.

Рекомендуемое имя:

- `YYYY-MM-DD_<short-topic>.md`
- или `kaggle_<short-topic>.md`

## Что должен сделать агент после появления файла

1. Прочитать файл целиком.
2. Извлечь competition URLs и связанные ссылки.
3. Зафиксировать пользовательскую постановку в `USER_PROMPTS_LOG.md`, если она дана в самом файле или в чате.
4. Создать запись в `RESEARCH_JOURNAL.md` о начале новой исследовательской ветки.
5. Сформировать initial problem brief:
   - competition name;
   - objective;
   - evaluation metric;
   - file format requirements;
   - deadlines and constraints if they доступны;
   - baseline directions.
6. Запустить сбор источников по `SOURCE_COLLECTION_POLICY.md`.
7. Развести дальнейшую работу по двум веткам:
   - engineering / Kaggle implementation -> `ML in Math/`
   - mathematics / theory / invariants / proof ideas -> `Math_Hypothese_AutoCheck_Witch_Agents/`

## Артефакты первого шага intake

После чтения нового intake-файла агент должен уметь породить или обновить:

- problem brief;
- список внешних источников;
- исследовательские заметки;
- initial hypotheses;
- plan of attack;
- ссылки на подпроекты, куда пойдёт дальнейшая работа.

## Что нельзя делать

- Нельзя считать `ML in Math/baseline/` корневым intake.
- Нельзя сразу начинать кодинг без фиксации problem statement и источников.
- Нельзя терять исходный markdown-файл пользователя.
- Нельзя смешивать подтверждённые сведения о competition с неподтверждёнными догадками.

## Связанные документы

- `KAGGLE_AUTONOMOUS_WORKFLOW.md`
- `SOURCE_COLLECTION_POLICY.md`
- `USER_PROMPTS_LOG.md`
- `RESEARCH_JOURNAL.md`
