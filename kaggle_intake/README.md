# Kaggle Intake (root)

Эта папка предназначена для **новых входных задач** на уровне всего workspace.

Пользователь кладёт сюда markdown-файл со ссылками на Kaggle competition и при необходимости с короткими заметками. После этого агент должен:

1. прочитать файл;
2. извлечь ссылки и контекст;
3. зафиксировать задачу в корневой памяти;
4. собрать источники;
5. распределить дальнейшую работу между:
   - `ML in Math/`
   - `Math_Hypothese_AutoCheck_Witch_Agents/`

Важно:

- эта папка **не заменяет** `ML in Math/baseline/`;
- `ML in Math/baseline/` остаётся проектным архивом и референсом pancake-проекта;
- корневой `kaggle_intake/` — это intake новых задач для всей агентной системы.

См. также:

- `../BASELINE_INTAKE_SPEC.md`
- `../KAGGLE_AUTONOMOUS_WORKFLOW.md`
- `../SOURCE_COLLECTION_POLICY.md`
