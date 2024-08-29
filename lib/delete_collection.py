def delete_collection(client, collection, all):

    if all:
        collections = client.collections.list_all()
        for collection in collections:
            print(f"Deleting collection '{collection}'")
            client.collections.delete(collection)
        print(f"All collections deleted successfully in Weaviate.")
    else:
        if client.collections.exists(collection):
            try:
                client.collections.delete(collection)
            except Exception as e:

                raise Exception(
                    f"Failed to delete collection '{collection}' in Weaviate.: {e}"
                )
        else:
            raise Exception(
                f"Collection '{collection}' doesn't exist in Weaviate."
            )

        assert not client.collections.exists(collection)

        print(f"Collection '{collection}' deleted successfully in Weaviate.")
