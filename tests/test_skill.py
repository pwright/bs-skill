from subprocess import run, PIPE

def test_simple():
    p = run(
        ["python", "-m", "skill.cli", "--provider", "codex"],
        input=open("tests/golden/simple.in").read(),
        text=True,
        stdout=PIPE
    )
    assert p.stdout == open("tests/golden/simple.out").read()
