import lib.common as common
import semver
from weaviate.collections.classes.tenants import Tenant


def delete_tenants(host, api_key, port, collection, tenant_suffix, number_tenants):

    client = common.connect_to_weaviate(host, api_key, port)
    version = semver.Version.parse(client.get_meta()["version"])
    if not client.collections.exists(collection):

        raise Exception(
            f"Class '{collection}' does not exist in Weaviate. Create first using <create class> command"
        )

    collection = client.collections.get(collection)

    if not collection.config.get().multi_tenancy_config.enabled:

        raise Exception(
            f"Collection '{collection.name}' does not have multi-tenancy enabled. Recreate or modify the class with <create class> command"
        )

    total_tenants = len(collection.tenants.get())
    try:
        if total_tenants == 0:

            raise Exception(f"No tenants present in class {collection.name}.")
        # get_by_names is only available after 1.25.0
        if version.compare(semver.Version.parse("1.25.0")) < 0:
            tenants_list = {
                name: tenant
                for name, tenant in collection.tenants.get().items()
                if name.startswith(tenant_suffix)
            }
            print("hello")
            deleting_tenants = {
                name: tenant
                for name, tenant in tenants_list.items()
                if int(name[len(tenant_suffix) :]) < number_tenants
            }
        else:
            deleting_tenants = collection.tenants.get_by_names(
                [
                    f"{tenant_suffix}{i}"
                    for i in range(
                        number_tenants
                        if number_tenants < total_tenants
                        else total_tenants
                    )
                ]
            )
        if not deleting_tenants:

            raise Exception(f"No tenants present in class {collection.name}.")
        else:
            for name, tenant in deleting_tenants.items():
                collection.tenants.remove(Tenant(name=name))

    except Exception as e:

        raise Exception(f"Failed to delete tenants: {e}")

    tenants_list = collection.tenants.get()
    assert (
        len(tenants_list) == total_tenants - number_tenants
    ), f"Expected {total_tenants - number_tenants} tenants, but found {len(tenants_list)}"

    print(f"{number_tenants} tenants deleted")
