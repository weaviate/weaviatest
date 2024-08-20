import lib.common as common
import semver
import weaviate.classes.config as wvc
from weaviate.collections.classes.tenants import TenantActivityStatus, Tenant


def create_tenants(host, api_key,port,
                   class_name,tenant_suffix, number_tenants, state):

    client = common.connect_to_weaviate(host, api_key, port)
    
    if not client.collections.exists(class_name):
        print(
            f"Class '{class_name}' does not exist in Weaviate. Create first using <create class>"
        )
        client.close()
        return

    version = semver.Version.parse(client.get_meta()["version"])
    collection = client.collections.get(class_name)

    if not collection.config.get().multi_tenancy_config.enabled:
        print(
            f"Collection '{collection.name}' does not have multi-tenancy enabled. Recreate or modify the class with: <create class>"
        )
        client.close()
        return

    tenant_state_map = {
        "hot": TenantActivityStatus.HOT,
        "active": TenantActivityStatus.ACTIVE,
        "cold": TenantActivityStatus.COLD,
        "inactive": TenantActivityStatus.INACTIVE,
        "frozen": TenantActivityStatus.FROZEN,
        "offloaded": TenantActivityStatus.OFFLOADED,
    }

    try:
        existing_tenants = collection.tenants.get()
        if existing_tenants:
            client.close()
            print(
                f"Tenants already exist in class '{collection.name}'. Update their status using ./update_tenants.py or delete them using <delete tenants> command"
            )
            client.close()
            return
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

    except Exception as e:
        print(f"Failed to create tenants: {e}")
        client.close()

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
            print(
                f"Tenant '{tenant.name}' has activity status '{tenant.activity_status}', but expected '{tenant_state_map[state]}'"
            )
    print(
        f"{len(tenants_list)} tenants added with tenant status '{tenant.activity_status}' for collection '{collection.name}'"
    )

    client.close()

