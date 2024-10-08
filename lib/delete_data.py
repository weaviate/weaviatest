import weaviate.classes.config as wvc


def __delete_data(collection, num_objects, cl):

    res = collection.query.fetch_objects(limit=num_objects)
    if len(res.objects) == 0:
        print(
            f"No objects found in class '{collection.name}'. Insert objects first using <ingest data> command"
        )
        return -1
    data_objects = res.objects

    for obj in data_objects:
        collection.with_consistency_level(cl).data.delete_by_id(uuid=obj.uuid)

    print(f"Deleted {num_objects} objects into class '{collection.name}'")
    return num_objects


def delete_data(client, collection, limit, consistency_level):

    if not client.collections.exists(collection):
        print(
            f"Class '{collection}' does not exist in Weaviate. Create first using <create class> command."
        )

        return 1

    collection = client.collections.get(collection)
    try:
        tenants = [key for key in collection.tenants.get().keys()]
    except Exception as e:
        # Check if the error is due to multi-tenancy being disabled
        if "multi-tenancy is not enabled" in str(e):
            print(
                f"Collection '{collection.name}' does not have multi-tenancy enabled. Skipping tenant information collection."
            )
            tenants = ["None"]

    cl_map = {
        "quorum": wvc.ConsistencyLevel.QUORUM,
        "all": wvc.ConsistencyLevel.ALL,
        "one": wvc.ConsistencyLevel.ONE,
    }

    for tenant in tenants:
        if tenant == "None":
            ret = __delete_data(collection, limit, cl_map[consistency_level])
        else:
            print(f"Processing tenant '{tenant}'")
            ret = __delete_data(
                collection.with_tenant(tenant),
                limit,
                cl_map[consistency_level],
            )
        if ret == -1:

            raise Exception(
                f"Failed to delete objects in class '{collection.name}' for tenant '{tenant}'"
            )
