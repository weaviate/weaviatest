import lib.common as common


def delete_class(host, api_key, port, collection):

    client = common.connect_to_weaviate(host, api_key, port)

    if client.collections.exists(collection):
        try:
            client.collections.delete(collection)
        except Exception as e:
            print(f"Failed to delete class '{collection}' in Weaviate.: {e}")
            client.close()
            return

    assert not client.collections.exists(collection)

    print(f"Class '{collection}' deleted successfully in Weaviate.")

    client.close()

