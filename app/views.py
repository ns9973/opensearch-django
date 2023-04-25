import json

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

from opensearchpy import OpenSearch

from . import helper


# Create your views here.
def index(request):
    return render(request, "app/index.html")


def search(request):
    client = helper.get_http_client(
        settings.OPENSEARCH_HOST,
        settings.OPENSEARCH_PORT,
        (settings.OPENSEARCH_USER, settings.OPENSEARCH_PASS),
    )
    query = request.GET.get("q") if request.GET.get("q") else ""
    page_num = request.GET.get("pn") if request.GET.get("pn") else 1
    page_size = request.GET.get("ps") if request.GET.get("ps") else 10
    search_body = {}
    start_from = (page_num - 1) * page_size

    if query:
        search_body = helper.get_default_search_body(start_from, page_size, query)
    else:
        search_body = helper.get_query_match_all(start_from, page_size)

    search_result = client.search(index=settings.DEFAULT_INDEX, body=search_body)
    total = search_result["hits"]["total"]["value"]
    num_pages = total // page_size + 1 if total % page_size else total // page_size
    response = {
        "hits": search_result["hits"]["hits"],
        "num_pages": num_pages,
        "page_num": page_num,
        "page_size": page_size,
        "query": query,
        "total": total,
    }
    # response = {"key1": [0, 1, 2, 3, 4, 5]}
    return render(request, "app/search.html", response)
