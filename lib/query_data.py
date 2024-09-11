import lib.common as common
import weaviate.classes.config as wvc
from weaviate.classes.query import MetadataQuery
from weaviate.collections.classes.tenants import TenantActivityStatus
from datetime import datetime


def __query_data(collection, num_objects, cl, search_type, query):

    start_time = datetime.now()
    response = None
    if search_type == "fetch":
        # Fetch logic
        response = collection.with_consistency_level(cl).query.fetch_objects(
            limit=num_objects
        )
    elif search_type == "vector":
        # Vector logic
        response = collection.with_consistency_level(cl).query.near_text(
            query=query,
            return_metadata=MetadataQuery(distance=True, certainty=True),
            limit=num_objects,
        )
    elif search_type == "count":
        # Aggregate logic
        res = collection.with_consistency_level(cl).aggregate.over_all(total_count=True)
        total_object_count = res.total_count
    elif search_type == "keyword":
        # Keyword logic
        response = collection.with_consistency_level(cl).query.bm25(
            query=query, return_metadata=MetadataQuery(score=True), limit=num_objects
        )
    elif search_type == "hybrid":
        # Hybrid logic
        response = collection.with_consistency_level(cl).query.hybrid(
            query=query, return_metadata=MetadataQuery(score=True), limit=num_objects
        )
    else:
        print(
            f"Invalid search type: {search_type}. Please choose from 'fetch objects', 'vector', 'keyword', or 'hybrid'."
        )
        return -1

    if response is not None:
        common.pp_objects(response)
    elif total_object_count is not None:
        print(total_object_count)
    else:
        print("No objects found")
        return -1

    end_time = datetime.now()
    latency = end_time - start_time

    print(
        f"Queried {num_objects} objects using {search_type} search into class '{collection.name}' in {latency.total_seconds()} s"
    )
    return num_objects


def query_data(client, collection, search_type, query, consistency_level, limit):

    if not client.collections.exists(collection):

        raise Exception(
            f"Class '{collection}' does not exist in Weaviate. Create first using <create class> command."
        )

    collection = client.collections.get(collection)
    try:
        tenants = [
            key
            for key, tenant in collection.tenants.get().items()
            if tenant.activity_status == TenantActivityStatus.ACTIVE
        ]
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
            ret = __query_data(
                collection,
                limit,
                cl_map[consistency_level],
                search_type,
                query,
            )
        else:
            print(f"Querying tenant '{tenant}'")
            ret = __query_data(
                collection.with_tenant(tenant),
                limit,
                cl_map[consistency_level],
                search_type,
                query,
            )
        if ret == -1:

            raise Exception(
                f"Failed to query objects in class '{collection.name}' for tenant '{tenant}'"
            )
