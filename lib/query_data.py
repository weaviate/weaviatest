import lib.common as common
import numpy as np
import weaviate.classes.config as wvc
from weaviate.classes.query import MetadataQuery
from weaviate.collections.classes.tenants import TenantActivityStatus
from datetime import datetime


def __query_data(collection, num_objects, cl, search_type, query):
    
    start_time = datetime.now()
    response = None
    if search_type == "fetch":
        # Fetch logic
        response = collection.with_consistency_level(cl).query.fetch_objects(limit=num_objects)
    elif search_type == "vector":
        # Vector logic
        response = collection.with_consistency_level(cl).query.near_text(query=query, return_metadata=MetadataQuery(distance=True, certainty=True), limit=num_objects)
    elif search_type == "keyword":
        # Keyword logic
        response = collection.with_consistency_level(cl).query.bm25(query=query, return_metadata=MetadataQuery(score=True), limit=num_objects)
    elif search_type == "hybrid":
        # Hybrid logic
        response = collection.with_consistency_level(cl).query.hybrid(query=query, return_metadata=MetadataQuery(score=True), limit=num_objects)
    else:
        print(f"Invalid search type: {search_type}. Please choose from 'fetch', 'vector', 'keyword', or 'hybrid'.")
        return
    
    if response != None:
        common.pp_objects(response)
    else:
        print("No objects found")
    end_time = datetime.now()
    latency = end_time - start_time

    print(f"Queried {num_objects} objects using {search_type} search into class '{collection.name}' in {latency.total_seconds()} s")


def query_data(host, api_key, port, collection, search_type, query, consistency_level, limit):

    client = common.connect_to_weaviate(host, api_key, port)
    if not client.collections.exists(collection):
        print(
            f"Class '{collection}' does not exist in Weaviate. Create first using <create class> command."
        )
        client.close()
        return

    collection = client.collections.get(collection)
    try:
        tenants = [key for key, tenant in collection.tenants.get().items() if tenant.activity_status == TenantActivityStatus.ACTIVE ]
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
            __query_data(
                collection,
                limit,
                cl_map[consistency_level],
                search_type,
                query,
            )
        else:
            print(f"Querying tenant '{tenant}'")
            __query_data(
                collection.with_tenant(tenant),
                limit,
                cl_map[consistency_level],
                search_type,
                query,
            )

    client.close()