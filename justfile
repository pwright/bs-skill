test:
	pytest -q

run-codex:
	cat tests/golden/simple.in | python -m skill.cli --provider codex

run-claude:
	cat tests/golden/simple.in | python -m skill.cli --provider claude
