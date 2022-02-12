import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from typing import List

from base.database import Database, Row


class BaseCorsExemptView(View):
    def options(self, request):
        response = HttpResponse()
        response.status_code = 204
        self.add_cors_headers(response)
        return response

    def add_cors_headers(self, response: HttpResponse) -> None:
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = self.get_http_method()
        response["Access-Control-Allow-Headers"] = "Content-Type"

    def get_http_method(self) -> str:
        raise NotImplementedError


class TopicSearchView(BaseCorsExemptView):
    def get_http_method(self) -> str:
        return "GET"

    def get(self, request: HttpRequest) -> HttpResponse:
        query = request.GET.get("q", "")
        with Database(readonly=True) as db:
            results = [
                {"id": topic["id"], "text": topic["path"]}
                for topic in db.select(
                    "bookmark_topics",
                    where="path LIKE :path_pattern",
                    values={"path_pattern": "%" + query + "%"},
                )
            ]

        response = JsonResponse({"results": results})
        self.add_cors_headers(response)
        return response


class BookmarkCreateView(BaseCorsExemptView):
    def get_http_method(self) -> str:
        return "POST"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request: HttpRequest) -> HttpResponse:
        with Database() as db:
            payload = json.loads(request.body)
            title = payload["title"]
            url = payload["url"]
            author = payload["author"]
            year = payload["year"]
            keywords = payload["keywords"]
            quality = int(payload["quality"])
            topics = payload["topics"]
            annotation = payload["annotation"]

            if payload["id"]:
                self.update(
                    db,
                    payload["id"],
                    title=title,
                    author=author,
                    year=year,
                    keywords=keywords,
                    topics=topics,
                    quality=quality,
                    annotation=annotation,
                )
            else:
                self.create(
                    db,
                    title=title,
                    author=author,
                    year=year,
                    url=url,
                    keywords=keywords,
                    topics=topics,
                    quality=quality,
                    annotation=annotation,
                )

            response = JsonResponse({})
            self.add_cors_headers(response)
            return response

    def create(
        self,
        db: Database,
        *,
        title: str,
        author: str,
        year: str,
        url: str,
        keywords: str,
        topics: List[Row],
        quality: int,
        annotation: str,
    ) -> None:
        pk = db.insert(
            "bookmarks",
            {
                "title": title,
                "url": url,
                "author": author,
                "year": year,
                "keywords": keywords,
                "quality": quality,
                "annotation": annotation,
            },
        )

        self.set_topics(db, pk, topics)

    def update(
        self,
        db: Database,
        pk: int,
        *,
        title: str,
        author: str,
        year: str,
        keywords: str,
        topics: List[Row],
        quality: int,
        annotation: str,
    ) -> None:
        db.update_by_pk(
            "bookmarks",
            pk,
            {
                "title": title,
                "author": author,
                "year": year,
                "keywords": keywords,
                "quality": quality,
                "annotation": annotation,
            },
        )

        db.delete("bookmark_topic_relations", where="bookmark = :pk", values={"pk": pk})
        self.set_topics(db, pk, topics)

    def set_topics(self, db: Database, pk: int, topics: List[Row]) -> None:
        for topic in topics:
            try:
                topic_id = int(topic["id"])
            except ValueError:
                topic_id = db.insert("bookmark_topics", {"path": topic["path"]})

            db.insert("bookmark_topic_relations", {"bookmark": pk, "topic": topic_id})


class BookmarkGetView(BaseCorsExemptView):
    def get_http_method(self) -> str:
        return "GET"

    def get(self, request: HttpRequest) -> HttpResponse:
        with Database() as db:
            url = request.GET.get("url")
            bookmark = db.get("bookmarks", where="url = :url", values={"url": url})
            if bookmark is not None:
                topic_relations = db.select(
                    "bookmark_topic_relations",
                    where="bookmark = :bookmark",
                    values={"bookmark": bookmark["id"]},
                    get_related=["topic"],
                )
                topics = [r["topic"] for r in topic_relations]

                response = JsonResponse(
                    {
                        "bookmark": {
                            "id": bookmark["id"],
                            "title": bookmark["title"],
                            "author": bookmark["author"],
                            "year": bookmark["year"],
                            "url": bookmark["url"],
                            "keywords": bookmark["keywords"],
                            "topics": topics,
                            "quality": bookmark["quality"],
                            "annotation": bookmark["annotation"],
                        }
                    }
                )
            else:
                response = JsonResponse({"bookmark": None})

            self.add_cors_headers(response)
            return response


class BookmarkDeleteView(BaseCorsExemptView):
    def get_http_method(self) -> str:
        return "POST"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request: HttpRequest) -> HttpResponse:
        with Database() as db:
            payload = json.loads(request.body)
            pk = payload["id"]
            db.delete(
                "bookmark_topic_relations", where="bookmark = :pk", values={"pk": pk}
            )
            db.delete_by_pk("bookmarks", pk)

            response = JsonResponse({})
            self.add_cors_headers(response)
            return response
