from django.http import HttpRequest, HttpResponse, JsonResponse

from base.database import Database


def list(request: HttpRequest, reflist: str) -> HttpResponse:
    payload = []
    with Database(readonly=True) as db:
        for ref in reflist.split(","):
            bookmark = db.get_by_pk("bookmarks", int(ref))
            payload.append(bookmark)
    return JsonResponse(payload, safe=False)
