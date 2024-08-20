import common
import json
import numpy as np
import string
import random
import weaviate.classes.config as wvc
import os
from datetime import datetime, timedelta


def __import_json(collection, file_name, cl, num_objects=None):
    counter = 0
    properties = collection.config.get().properties
    if os.path.isfile(file_name):
        with open(file_name) as f:
            data = json.load(f)
            cl_collection = collection.with_consistency_level(cl)
            with cl_collection.batch.dynamic() as batch:
                for obj in data[:num_objects] if num_objects else data:
                    added_obj = {}
                    for prop in properties:
                        if prop.name == "release_date":
                            prop.name = "releaseDate"
                        if prop.name in obj:
                            if prop.data_type == wvc.DataType.NUMBER:
                                added_obj[prop.name] = float(obj[prop.name])
                            elif prop.data_type == wvc.DataType.DATE:
                                date = datetime.strptime(obj[prop.name], "%Y-%m-%d")
                                # Format the datetime object to a string
                                added_obj[prop.name] = date.strftime(
                                    "%Y-%m-%dT%H:%M:%SZ"
                                )
                            else:
                                added_obj[prop.name] = obj[prop.name]
                    batch.add_object(properties=added_obj)
                    counter += 1

            if cl_collection.batch.failed_objects:
                for failed_object in cl_collection.batch.failed_objects:
                    print(
                        f"Failed to add object with UUID {failed_object.original_uuid}: {failed_object.message}"
                    )
            expected = len(data[:num_objects]) if num_objects else len(data)
            assert (
                counter == expected
            ), f"Expected {expected} objects, but added {counter} objects."
    else:
        print(f"File '{file_name}' does not exist or is not a file.")
    print(f"Finished processing {counter} objects.")
    return counter


# Insert objects to the replicated collection
def __get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


def __generate_data_object(number_objects):

    data_objects = []
    for _ in range(number_objects):
        date = datetime.strptime("1980-01-01", "%Y-%m-%d")
        random_date = date + timedelta(days=random.randint(1, 15_000))
        release_date = random_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        data_object = {
            "title": "title" + __get_random_string(10),
            "genres": "genre" + __get_random_string(3),
            "keywords": "keywords" + __get_random_string(3),
            "popularity": float(random.randint(1, 200)),
            "runtime": "runtime" + __get_random_string(3),
            "cast": "cast" + __get_random_string(3),
            "language": "language" + __get_random_string(3),
            "tagline": "tagline" + __get_random_string(3),
            "budget": random.randint(1_000_000, 1_000_0000_000),
            "release_date": release_date,
            "revenue": random.randint(1_000_000, 10_000_0000_000),
            "status": "status" + __get_random_string(3),
        }

        data_objects.append(data_object)

    return data_objects


def __ingest_data(collection, num_objects, cl, randomize):
    if randomize:
        counter = 0
        data_objects = __generate_data_object(num_objects)
        cl_collection = collection.with_consistency_level(cl)
        with cl_collection.batch.dynamic() as batch:
            for obj in data_objects:
                batch.add_object(
                    properties=obj,
                    vector={"default": np.random.rand(1, 1536)[0].tolist()},
                )
                counter += 1

        if cl_collection.batch.failed_objects:
            for failed_object in cl_collection.batch.failed_objects:
                print(
                    f"Failed to add object with UUID {failed_object.original_uuid}: {failed_object.message}"
                )
        print(f"Inserted {counter} objects into class '{collection.name}'")
    else:
        num_objects_inserted = __import_json(collection, "movies.json", cl, num_objects)
        print(f"Inserted {num_objects_inserted} objects into class '{collection.name}'")


def ingest_data(host, api_key, port, class_name, number_objects, consistency_level, randomize, auto_tenants):

    client = common.connect_to_weaviate(host, api_key, port)
    if not client.collections.exists(class_name):
        print(
            f"Class '{class_name}' does not exist in Weaviate. Create first using <create class> command"
        )
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
    if (
        auto_tenants > 0
        and collection.config.get().multi_tenancy_config.auto_tenant_creation == False
    ):
        print(
            f"Auto tenant creation is not enabled for class '{collection.name}'. Please enable it using <update class> command"
        )
        return

    cl_map = {
        "quorum": wvc.ConsistencyLevel.QUORUM,
        "all": wvc.ConsistencyLevel.ALL,
        "one": wvc.ConsistencyLevel.ONE,
    }
    if auto_tenants > 0:
        if tenants == "None":
            tenants = [f"Tenant--{i}" for i in range(1, auto_tenants + 1)]
        else:
            if len(tenants) < auto_tenants:
                tenants += [
                    f"Tenant--{i}"
                    for i in range(len(tenants) + 1, auto_tenants + 1)
                ]

    for tenant in tenants:
        if tenant == "None":
            __ingest_data(
                collection,
                number_objects,
                cl_map[consistency_level],
                randomize,
            )
        else:
            print(f"Processing tenant '{tenant}'")
            __ingest_data(
                collection.with_tenant(tenant),
                number_objects,
                cl_map[consistency_level],
                randomize,
            )

    client.close()

