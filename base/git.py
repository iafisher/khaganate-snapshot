import subprocess


def get_diff(path):
    if not path.startswith("/"):
        path = "/" + path

    result = subprocess.run(
        ["git", "-C", path, "diff", "--staged"], capture_output=True, encoding="utf8"
    )
    return result.stdout
