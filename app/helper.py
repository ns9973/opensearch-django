from django.conf import settings
from opensearchpy import OpenSearch


def get_http_client(host, port, auth: tuple):
    return OpenSearch(
        hosts=[{"host": host, "port": port}],
        http_auth=auth,
        use_ssl=False,
        verify_certs=False,
    )


def get_default_search_body(start_from: int, page_size: int, query: str):
    return {
        "from": start_from,
        "size": page_size,
        "query": {
            "query_string": {
                "query": query,
                "fields": [
                    "title",
                    "body",
                ],
            }
        },
        "sort": {"_score": {"order": "desc"}},
    }


def get_query_match_all(start_from: int, page_size: int):
    return {
        "from": start_from,
        "size": page_size,
        "query": {"match_all": {}},
    }
