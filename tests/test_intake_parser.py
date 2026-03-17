from pathlib import Path

from workspace_orchestrator.intake import parse_intake_file


def test_parse_intake_file_classifies_links_and_sections(tmp_path: Path) -> None:
    intake = tmp_path / "sample.md"
    intake.write_text(
        """# Kaggle Task Intake Template

## Competition links

- https://www.kaggle.com/competitions/example-comp

## Optional notes from user

- Need a strong baseline
- Pay attention to math structure

## Optional extra sources

- Discussions: https://www.kaggle.com/competitions/example-comp/discussion/1
- Notebooks: https://www.kaggle.com/code/example/notebook
- Papers: https://arxiv.org/abs/1234.5678
- Repositories: https://github.com/example/repo

## Optional priorities

- Build a strong baseline
- Search for literature
""",
        encoding="utf-8",
    )

    brief = parse_intake_file(intake)

    assert brief.competition_links == ["https://www.kaggle.com/competitions/example-comp"]
    assert brief.notebook_links == ["https://www.kaggle.com/code/example/notebook"]
    assert brief.paper_links == ["https://arxiv.org/abs/1234.5678"]
    assert brief.repo_links == ["https://github.com/example/repo"]
    assert "Need a strong baseline" in brief.notes
    assert "Build a strong baseline" in brief.priorities
