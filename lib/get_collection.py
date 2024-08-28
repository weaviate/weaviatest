import json
from weaviate.collections.classes.tenants import TenantActivityStatus


def __get_total_objects_with_multitenant(col_obj):
    acc = 0
    for tenant_name, tenant in col_obj.tenants.get().items():
        acc += (
            len(col_obj.with_tenant(tenant))
            if tenant.activity_status == TenantActivityStatus.ACTIVE
            else 0
        )
    return acc


def get_collection(client, collection):

    if collection != None:
        if not client.collections.exists(collection):

            raise Exception(f"Collection '{collection}' does not exist")
        col_obj = client.collections.get(collection)
        # Pretty print the dict structure
        print(json.dumps(col_obj.config.get().to_dict(), indent=4))
    else:
        print(
            f"{'Collection':<30}{'Multitenancy':<16}{'Tenants': <16}{'Objects':<16}{'ReplicationFactor':<20}{'VectorIndex':<16}{'Vectorizer':<16}"
        )
        all_collections = client.collections.list_all()
        for collection in all_collections:
            col_obj = client.collections.get(collection)
            schema = col_obj.config.get()
            print(
                f"{collection:<29} {'True' if schema.multi_tenancy_config.enabled else 'False':<15} {len(col_obj.tenants.get()) if schema.multi_tenancy_config.enabled else 0:<15} {__get_total_objects_with_multitenant(col_obj) if schema.multi_tenancy_config.enabled else len(col_obj):<15} {schema.replication_config.factor:<19} {schema.vector_index_type if schema.vector_index_type else 'None':<15} {schema.vectorizer if schema.vectorizer else 'None':<15}"
            )
        print(f"{'':<30}{'':<16}{'':<16}{'':<16}{'':<20}{'':<16}{'':<16}")
        print(f"Total: {len(all_collections)} collections")
