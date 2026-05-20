from typer.testing import CliRunner
from main import app

runner = CliRunner()

def test_missing_diff_file():
    result = runner.invoke(app, [""])
    assert result.exit_code != 0
