import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings

from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer

from . import helpers

model = SentenceTransformer(settings.SENTENCE_TRANSFORMERS_MODEL)


# Create your views here.
def index(request):
    return render(request, "app/index.html")


def simdocs(request):
    text = request.POST.get("text") if request.POST.get("text") else ""
    page_num = request.POST.get("p") if request.POST.get("p") else 1
    page_size = request.POST.get("s") if request.POST.get("s") else settings.PAGE_SIZE
    main_form = request.POST.get("m")

    page_num = int(page_num)
    page_size = int(page_size)

    if main_form == "1":
        page_num = 1

    start_from = (page_num - 1) * page_size

    if not text:
        return render(request, "app/simdocs.html", {"text": "", "result": {}})

    print(len(text))

    norm_text = helpers.cleanse_text(text)
    embeddings = model.encode([norm_text])
    boby = {
        "from": start_from,
        "size": page_size,
        "query": {"knn": {"my_vector": {"vector": embeddings[0].tolist(), "k": 2}}},
    }

    client = helpers.get_http_client(
        settings.OPENSEARCH_HOST,
        settings.OPENSEARCH_PORT,
        (settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
    )

    result = client.search(index=settings.DEFAULT_INDEX, body=boby)
    num_hits = result["hits"]["total"]["value"]
    navi_info = helpers.navigation_info(
        num_hits, page_num, page_size, settings.NAVI_SIZE
    )

    context = {
        "text": text,
        "encoded_text": json.dumps(embeddings[0].tolist()),
        "page_num": page_num,
        "result": result,
        "navi_info": navi_info,
    }
    return render(request, "app/simdocs.html", context)


def simdocs_most_frequent_terms(request):
    encoded_text = (
        request.POST.get("encoded_text") if request.POST.get("encoded_text") else ""
    )

    if not encoded_text:
        return JsonResponse({})

    embedding = json.loads(encoded_text)

    boby = {
        "query": {"knn": {"my_vector": {"vector": embedding, "k": 2}}},
        "aggs": {
            "freq_terms": {
                "terms": {"field": "feature_terms", "order": {"_count": "desc"}}
            }
        },
    }

    client = helpers.get_http_client(
        settings.OPENSEARCH_HOST,
        settings.OPENSEARCH_PORT,
        (settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
    )

    result = client.search(index=settings.DEFAULT_INDEX, body=boby)

    context = {
        "result": result,
    }
    return JsonResponse(context)


def search(request):
    query = request.GET.get("q") if request.GET.get("q") else ""
    page_num = int(request.GET.get("pn")) if request.GET.get("pn") else 1
    page_size = int(request.GET.get("ps")) if request.GET.get("ps") else 10
    search_body = {}
    start_from = (page_num - 1) * page_size

    if query:
        search_body = helpers.get_default_search_body(start_from, page_size, query)
    else:
        search_body = helpers.get_query_match_all(start_from, page_size)

    client = helpers.get_http_client(
        settings.OPENSEARCH_HOST,
        settings.OPENSEARCH_PORT,
        (settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
    )

    search_result = client.search(index=settings.DEFAULT_INDEX, body=search_body)
    total = search_result["hits"]["total"]["value"]
    num_pages = total // page_size + 1 if total % page_size else total // page_size
    context = {
        "hits": search_result["hits"]["hits"],
        "num_pages": num_pages,
        "page_num": page_num,
        "page_size": page_size,
        "query": query,
        "total": total,
    }
    # response = {"key1": [0, 1, 2, 3, 4, 5]}
    return render(request, "app/search.html", context)
