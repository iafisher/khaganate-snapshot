"""
Pre-commit configuration for git.

This file was created by precommit (https://github.com/iafisher/precommit).
You are welcome to edit it yourself to customize your pre-commit hook.
"""
from precommitlib import checks


def init(precommit):
    # Generic checks
    precommit.check(checks.NoStagedAndUnstagedChanges())
    precommit.check(checks.NoWhitespaceInFilePath())
    precommit.check(checks.DoNotSubmit())

    # Python checks
    pyinclude = ["scripts/*"]
    pyexclude = ["scripts/kg", "scripts/kgdb", "scripts/sync"]
    precommit.check(checks.PythonFormat(include=pyinclude, exclude=pyexclude))
    precommit.check(
        checks.PythonLint(
            ["--config", ".config/flake8"], include=pyinclude, exclude=pyexclude
        )
    )
    # precommit.check(checks.PipFreeze(venv=".venv"))

    precommit.check(
        checks.JavaScriptLint(
            ["--config", ".config/eslintrc.json"],
            include=["*.vue"],
            exclude=["build.js"],
        )
    )
    precommit.check(
        checks.JavaScriptPrettierFormat(
            ["--config", ".config/prettierrc.json"], include=["*.vue"]
        )
    )

    precommit.check(
        checks.PythonImportOrder(
            ["--settings-file", ".config/isort.cfg"], exclude=["*/migrations/*"]
        )
    )

    precommit.check(checks.Command("UnitTests", ["./t"]))

    precommit.check(
        checks.Command(
            "PythonTypes",
            [
                ".venv/bin/mypy",
                "--config-file",
                ".config/mypy.ini",
                "--ignore-missing-imports",
                ".",
            ],
        )
    )
