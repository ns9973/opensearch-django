from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{"host": "192.168.205.1", "port": 9200}],
    http_auth=("admin", "admin"),
    use_ssl=False,
    verify_certs=False,
)
print(client)

boby = {
    "query": {"match_all": {}},
}

result = client.search(index="ldcc", body=boby)
print(result)
