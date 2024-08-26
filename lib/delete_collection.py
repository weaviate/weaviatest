import lib.common as common


def delete_collection(host, api_key, port, collection):

    client = common.connect_to_weaviate(host, api_key, port)

    if client.collections.exists(collection):
        try:
            client.collections.delete(collection)
        except Exception as e:
            client.close()
            raise Exception(
                f"Failed to delete collection '{collection}' in Weaviate.: {e}"
            )

    assert not client.collections.exists(collection)

    print(f"Collection '{collection}' deleted successfully in Weaviate.")

    client.close()
