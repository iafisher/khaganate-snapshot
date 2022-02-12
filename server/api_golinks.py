import re
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from typing import Any, List, Tuple

from base.database import Database


def direct(request: HttpRequest, path: str = "") -> HttpResponse:
    with Database() as db:
        link = db.get("golinks", where="link_text = :path", values={"path": path})
        if link is not None:
            db.insert("golink_visits", {"golink": link["id"]})
            return redirect(link["path"])
        else:
            for pattern, replacement in SPECIAL:
                if pattern.match(path):
                    return redirect(pattern.sub(replacement, path))

            return render(request, "app.html", {"path": path})


SPECIAL: List[Tuple[re.Pattern, Any]] = [
    # go/define/XYZ redirects to the Dictionary.com definition of XYZ.
    (re.compile("^define/([^/]+)$"), r"https://www.dictionary.com/browse/\1"),
    # go/golang/XYZ redirects to the docs for the XYZ package in Go.
    (re.compile("^golang/([^/]+)$"), r"https://pkg.go.dev/\1"),
    # go/js/XYZ/ABC redirects to the MDN docs on method ABC on JavaScript object XYZ,
    # e.g. go/js/Array/join.
    (
        re.compile("^js/([^/]+)(/.+)?$"),
        r"https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/\1\2",
    ),
    # go/python/XYZ redirects to the docs for the XYZ module in Python.
    (re.compile("^python/([^/]+)$"), r"https://docs.python.org/3.8/library/\1.html"),
    # go/synonym/XYZ redirects to the Thesaurus.com entry for XYZ.
    (re.compile("^synonym/([^/]+)$"), r"https://www.thesaurus.com/browse/\1"),
]
