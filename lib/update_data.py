import lib.common as common
import numpy as np
import random
import weaviate.classes.config as wvc
from datetime import datetime, timedelta


def __update_data_object():

    date = datetime.strptime("1980-01-01", "%Y-%m-%d")
    random_date = date + timedelta(days=random.randint(1, 15_000))
    release_date = random_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    data_object = {
        "title": "title-update" + common.get_random_string(10),
        "genres": "genre-update" + common.get_random_string(3),
        "keywords": "keywords-update" + common.get_random_string(3),
        "popularity": float(random.randint(1, 200)),
        "runtime": "runtime-update" + common.get_random_string(3),
        "cast": "cast-update" + common.get_random_string(3),
        "language": "language-update" + common.get_random_string(3),
        "tagline": "tagline-update" + common.get_random_string(3),
        "budget": random.randint(1_000_000, 1_000_0000_000),
        "release_date": release_date,
        "revenue": random.randint(1_000_000, 10_000_0000_000),
        "status": "status-update" + common.get_random_string(3),
    }

    return data_object


def __update_data(collection, num_objects, cl, randomize):
    if randomize:
        res = collection.query.fetch_objects(limit=num_objects)
        if len(res.objects) == 0:
            print(
                f"No objects found in class '{collection.name}'. Insert objects first using ./ingest_data.py"
            )
            return -1
        data_objects = res.objects
        for obj in data_objects:
            res = collection.with_consistency_level(cl).data.replace(
                uuid=obj.uuid,
                properties=__update_data_object(),
                vector={"default": np.random.rand(1, 1536)[0].tolist()},
            )
        found_objects = len(data_objects)
        assert (
            found_objects == num_objects
        ), f"Found {found_objects} objects, expected {num_objects}"
        print(f"Updated {found_objects} objects into class '{collection.name}'")
        return found_objects
    else:
        res = collection.query.fetch_objects(limit=num_objects)
        if len(res.objects) == 0:
            print(
                f"No objects found in class '{collection.name}'. Insert objects first using ./ingest_data.py"
            )
            return -1
        data_objects = res.objects
        for obj in data_objects:
            for property, value in obj.properties.items():
                if isinstance(value, str):
                    obj.properties[property] = "updated-" + value
                elif isinstance(value, int):
                    obj.properties[property] += 1
                elif isinstance(value, float):
                    obj.properties[property] += 1.0
                elif isinstance(value, datetime):
                    obj.properties[property] = value + timedelta(days=1)
            res = collection.with_consistency_level(cl).data.update(
                uuid=obj.uuid,
                properties=obj.properties,
            )
        found_objects = len(data_objects)
        assert (
            found_objects == num_objects
        ), f"Found {found_objects} objects, expected {num_objects}"
        print(f"Updated {num_objects} objects into class '{collection.name}'")
        return found_objects


def update_data(client, collection, limit, consistency_level, randomize):

    if not client.collections.exists(collection):

        raise Exception(
            f"Class '{collection}' does not exist in Weaviate. Create first using ./create_class.py"
        )

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
            ret = __update_data(
                collection,
                limit,
                cl_map[consistency_level],
                randomize,
            )
        else:
            print(f"Processing tenant '{tenant}'")
            ret = __update_data(
                collection.with_tenant(tenant),
                limit,
                cl_map[consistency_level],
                randomize,
            )
        if ret == -1:

            raise Exception(
                f"Failed to update objects in class '{collection.name}' for tenant '{tenant}'"
            )
