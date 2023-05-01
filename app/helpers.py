import re
import unicodedata

from django.conf import settings
from opensearchpy import OpenSearch


def cleanse_text(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\u3000", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[\r\t]+", " ", text)
    text = re.sub(r" {2,}", " ", text)
    return text


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
                    "summary",
                    "body",
                ],
            }
        },
        "sort": {"_score": {"order": "desc"}},
        "highlight": {
            "require_field_match": "false",
            "fields": {
                "title": {},
                "summary": {},
                "body": {},
            },
            "number_of_fragments": 0,
            "fragment_size": 0,
            "pre_tags": ["<strong><em>"],
            "post_tags": ["</em></strong>"],
        },
    }


def get_query_match_all(start_from: int, page_size: int):
    return {
        "from": start_from,
        "size": page_size,
        "query": {"match_all": {}},
    }


def navigation_info(num_hits, current_page, page_size, navi_size):
    if num_hits == 0:
        return {
            "current_page": current_page,
            "num_pages": 0,
            "num_ranges": 0,
            "range_num": 0,
            "range_start": 0,
            "range_end": 0,
            "page_size": page_size,
            "navi_size": navi_size,
        }

    num_pages = -(-num_hits // page_size)  # 何ページあるか計算
    num_ranges = -(-num_pages // navi_size)  # ナビゲーションがいくつの範囲を持っているか計算

    # レンジの開始番号を求める
    range_num = -(-current_page // navi_size)
    navi_remainder = navi_size

    range_start = (range_num - 1) * navi_size + 1
    range_end = range_start + navi_remainder - 1
    if range_end > num_pages:
        range_end = num_pages

    has_previous = True if current_page > 1 else False
    has_next = True if current_page < num_pages else False

    return {
        "current_page": current_page,
        "num_pages": num_pages,
        "num_ranges": num_ranges,
        "range_num": range_num,
        "range_start": range_start,
        "range_end": range_end,
        "labels": [l for l in range(range_start, range_end + 1)],
        "page_size": page_size,
        "navi_size": navi_size,
        "has_previous": has_previous,
        "has_next": has_next,
    }
