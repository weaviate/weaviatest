from weaviate.collections.classes.tenants import TenantActivityStatus


def get_tenants(client, collection, verbose):
    tenants = client.collections.get(collection).tenants.get()

    if verbose:
        print(f"{'Tenant Name':<20}{'Activity Status':<20}")
        for name, tenant in tenants.items():
            print(f"{name:<20}{tenant.activity_status.value:<20}")
    else:
        active_tenants = [
            tenant
            for name, tenant in tenants.items()
            if tenant.activity_status == TenantActivityStatus.ACTIVE
        ]
        inactive_tenants = [
            tenant
            for name, tenant in tenants.items()
            if tenant.activity_status == TenantActivityStatus.INACTIVE
        ]
        offoaded_tenants = [
            tenant
            for name, tenant in tenants.items()
            if tenant.activity_status == TenantActivityStatus.OFFLOADED
        ]

        print(
            f"{'Number Tenants':<20}{'Cold Tenants':<20}{'Hot Tenants': <20}{'Offloaded Tenants':<20}"
        )
        print(
            f"{len(tenants):<20}{len(inactive_tenants):<20}{len(active_tenants):<20}{len(offoaded_tenants):<20}"
        )
    return tenants
