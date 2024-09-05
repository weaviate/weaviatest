import semver
from weaviate.collections.classes.tenants import TenantActivityStatus, Tenant


def create_tenants(client, collection, tenant_suffix, number_tenants, state):

    if not client.collections.exists(collection):

        raise Exception(
            f"Class '{collection}' does not exist in Weaviate. Create first using <create class>"
        )

    version = semver.Version.parse(client.get_meta()["version"])
    collection = client.collections.get(collection)

    if not collection.config.get().multi_tenancy_config.enabled:

        raise Exception(
            f"Collection '{collection.name}' does not have multi-tenancy enabled. Recreate or modify the class with: <create class>"
        )

    tenant_state_map = {
        "hot": TenantActivityStatus.HOT,
        "active": TenantActivityStatus.ACTIVE,
        "cold": TenantActivityStatus.COLD,
        "inactive": TenantActivityStatus.INACTIVE,
        "frozen": TenantActivityStatus.FROZEN,
        "offloaded": TenantActivityStatus.OFFLOADED,
    }

    existing_tenants = collection.tenants.get()
    if existing_tenants:

        raise Exception(
            f"Tenants already exist in class '{collection.name}'. Update their status using ./update_tenants.py or delete them using <delete tenants> command"
        )
    else:
        collection.tenants.create(
            [
                Tenant(
                    name=f"{tenant_suffix}{i}",
                    activity_status=tenant_state_map[state],
                )
                for i in range(number_tenants)
            ]
        )

    # get_by_names is only available after 1.25.0
    if version.compare(semver.Version.parse("1.25.0")) < 0:
        tenants_list = {
            name: tenant
            for name, tenant in collection.tenants.get().items()
            if name.startswith(tenant_suffix)
        }
    else:
        tenants_list = collection.tenants.get_by_names(
            [f"{tenant_suffix}{i}" for i in range(number_tenants)]
        )
    assert (
        len(tenants_list) == number_tenants
    ), f"Expected {number_tenants} tenants, but found {len(tenants_list)}"
    for tenant in tenants_list.values():
        if tenant.activity_status != tenant_state_map[state]:

            raise Exception(
                f"Tenant '{tenant.name}' has activity status '{tenant.activity_status}', but expected '{tenant_state_map[state]}'"
            )
    print(
        f"{len(tenants_list)} tenants added with tenant status '{tenant.activity_status}' for collection '{collection.name}'"
    )
