import csv
import json
import mimetypes
import os
import subprocess
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

from base import constants
from base.utils import get_short_file_path


def files_get(request: HttpRequest, path: str = "") -> HttpResponse:
    fullpath = os.path.normpath(os.path.join(constants.FILES, path))
    revision = request.GET.get("r")

    # Guard against attempts to read files outside the FILES directory.
    if not fullpath.startswith(constants.FILES):
        return JsonResponse({"error": "not found"})

    if not os.path.exists(fullpath):
        return JsonResponse({"error": "not found"})

    if os.path.isdir(fullpath):
        dir_entries = sorted(os.scandir(fullpath), key=lambda d: d.name.lower())
        dir_entries = sorted(dir_entries, key=lambda d: d.is_dir(), reverse=True)
        files = [
            {
                "name": dir_entry.name,
                "path": get_short_file_path(dir_entry.path),
                "isDirectory": dir_entry.is_dir(),
            }
            for dir_entry in dir_entries
        ]
        payload = {
            "isDirectory": True,
            "path": path,
            "files": files,
        }
    else:
        if not revision:
            with open(fullpath, "r", encoding="utf8") as f:
                body = f.read()
        else:
            result = subprocess.run(
                ["git", "-C", constants.FILES, "show", f"{revision}:{path}"],
                stdout=subprocess.PIPE,
                encoding="utf8",
            )
            result.check_returncode()
            body = result.stdout

        revisions = []
        result = subprocess.run(
            [
                "git",
                "-C",
                constants.FILES,
                "rev-list",
                "--date=iso",
                "--format=%h %ad",
                "HEAD",
                path,
            ],
            stdout=subprocess.PIPE,
            encoding="utf8",
        )
        result.check_returncode()
        for line in result.stdout.splitlines():
            if line.startswith("commit "):
                # git rev-list prints a header line for each commit, which we ignore.
                continue

            parts = line.split(maxsplit=1)
            revisions.append({"hash": parts[0], "dateTime": parts[1]})

        if fullpath.endswith(".csv"):
            with open(fullpath, "r", encoding="utf8", newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                fields = reader.fieldnames

            payload = {
                "isDirectory": False,
                "isCsv": True,
                "path": path,
                "rows": rows,
                "fields": fields,
                "body": body,
                "revisions": revisions,
            }
        else:
            payload = {
                "isDirectory": False,
                "path": path,
                "body": body,
                "revisions": revisions,
            }

    return JsonResponse(payload)


def files_get_raw(request: HttpRequest, path: str) -> HttpResponse:
    fullpath = os.path.join(constants.FILES, os.path.normpath(path))

    with open(fullpath, "rb") as f:
        data = f.read()

    return HttpResponse(data, content_type=mimetypes.guess_type(path)[0])


@require_POST
def files_save(request: HttpRequest) -> HttpResponse:
    payload = json.loads(request.body, encoding="utf8")
    path = os.path.join(constants.FILES, payload["path"])
    body = payload["body"]

    with open(path, "w", encoding="utf8") as f:
        f.write(body)

    # Return a {"error": "..."} response to signal to the frontend that the save was
    # not successful. Do not include a trailing period in the error message.
    return JsonResponse({})
