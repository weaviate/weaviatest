import lib.common as common


def delete_class(host, api_key, port, class_name):

    client = common.connect_to_weaviate(host, api_key, port)

    if client.collections.exists(class_name):
        try:
            client.collections.delete(class_name)
        except Exception as e:
            print(f"Failed to delete class '{class_name}' in Weaviate.: {e}")
            client.close()
            return

    assert not client.collections.exists(class_name)

    print(f"Class '{class_name}' deleted successfully in Weaviate.")

    client.close()

