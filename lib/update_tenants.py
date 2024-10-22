import semver
from weaviate.collections.classes.tenants import TenantActivityStatus, Tenant


def update_tenants(client, collection, tenant_suffix, number_tenants, state):

    if not client.collections.exists(collection):

        raise Exception(
            f"Class '{collection}' does not exist in Weaviate. Create first using ./create_class.py"
        )

    version = semver.Version.parse(client.get_meta()["version"])
    collection = client.collections.get(collection)

    if not collection.config.get().multi_tenancy_config.enabled:

        raise Exception(
            f"Collection '{collection.name}' does not have multi-tenancy enabled. Recreate or modify the class with ./create_class.py"
        )

    tenant_state_map = {
        "hot": TenantActivityStatus.HOT,
        "active": TenantActivityStatus.ACTIVE,
        "cold": TenantActivityStatus.COLD,
        "inactive": TenantActivityStatus.INACTIVE,
        "frozen": TenantActivityStatus.FROZEN,
        "offloaded": TenantActivityStatus.OFFLOADED,
    }

    equivalent_state_map = {
        "hot": TenantActivityStatus.ACTIVE,
        "active": TenantActivityStatus.ACTIVE,
        "cold": TenantActivityStatus.INACTIVE,
        "inactive": TenantActivityStatus.INACTIVE,
        "frozen": TenantActivityStatus.OFFLOADED,
        "offloaded": TenantActivityStatus.OFFLOADED,
    }

    tenants_with_suffix = {
        name: tenant
        for name, tenant in collection.tenants.get().items()
        if name.startswith(tenant_suffix)
    }

    if len(tenants_with_suffix) < number_tenants:

        raise Exception(
            f"Not enough tenants present in class {collection.name} with suffix {tenant_suffix}. Expected {number_tenants}, found {len(tenants_with_suffix)}."
        )

    existing_tenants = dict(list(tenants_with_suffix.items())[:number_tenants])

    for name, tenant in existing_tenants.items():
        collection.tenants.update(
            Tenant(name=name, activity_status=tenant_state_map[state])
            if tenant.activity_status != tenant_state_map[state]
            else tenant
        )

    # get_by_names is only available after 1.25.0
    if version.compare(semver.Version.parse("1.25.0")) < 0:
        tenants_list = {
            name: tenant
            for name, tenant in collection.tenants.get().items()
            if name in existing_tenants.keys()
        }
    else:
        tenants_list = collection.tenants.get_by_names(
            [name for name in existing_tenants.keys()]
        )

    assert (
        len(tenants_list) == number_tenants
    ), f"Expected {number_tenants} tenants, but found {len(tenants_list)}"
    for tenant in tenants_list.values():
        if tenant.activity_status != equivalent_state_map[state]:

            raise Exception(
                f"Tenant '{tenant.name}' has activity status '{tenant.activity_status}', but expected '{tenant_state_map[state]}'"
            )
    print(
        f"{len(tenants_list)} tenants updated with tenant status '{tenant.activity_status}' for class '{collection.name}'."
    )
