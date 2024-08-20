import lib.common as common
import numpy as np
import weaviate.classes.config as wvc


def __delete_data(collection, num_objects, cl):

    res = collection.query.fetch_objects(limit=num_objects)
    if len(res.objects) == 0:
        print(
            f"No objects found in class '{collection.name}'. Insert objects first using <ingest data> command"
        )
        return
    data_objects = res.objects

    for obj in data_objects:
        collection.with_consistency_level(cl).data.delete_by_id(uuid=obj.uuid)

    print(f"Deleted {num_objects} objects into class '{collection.name}'")


def delete_data(host, api_key, port, class_name, number_objects, consistency_level):

    client = common.connect_to_weaviate(host, api_key, port)
    if not client.collections.exists(class_name):
        print(
            f"Class '{class_name}' does not exist in Weaviate. Create first using <create class> command."
        )
        client.close()
        return

    collection = client.collections.get(class_name)
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
            __delete_data(collection, number_objects, cl_map[consistency_level])
        else:
            print(f"Processing tenant '{tenant}'")
            __delete_data(
                collection.with_tenant(tenant),
                number_objects,
                cl_map[consistency_level],
            )

    client.close()

