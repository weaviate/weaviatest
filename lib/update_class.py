import lib.common as common
import weaviate.classes.config as wvc


def update_class(host, api_key, port, class_name, description, vector_index, training_limit,
                 async_enabled, auto_tenant_creation, auto_tenant_activation):

    client = common.connect_to_weaviate(host, api_key, port)
    if not client.collections.exists(class_name):
        print(
            f"Class '{class_name}' does not exist in Weaviate. Create first using ./create_class.py"
        )
        client.close()
        return

    vector_index_map = {
        "hnsw": wvc.Reconfigure.VectorIndex.hnsw(),
        "flat": wvc.Reconfigure.VectorIndex.flat(),
        "hnsw_pq": wvc.Reconfigure.VectorIndex.hnsw(
            quantizer=wvc.Reconfigure.VectorIndex.Quantizer.pq(
                training_limit=training_limit
            )
        ),
        "hnsw_sq": wvc.Reconfigure.VectorIndex.hnsw(
            quantizer=wvc.Reconfigure.VectorIndex.Quantizer.sq(
                training_limit=training_limit
            )
        ),
        "hnsw_bq": wvc.Reconfigure.VectorIndex.hnsw(
            quantizer=wvc.Reconfigure.VectorIndex.Quantizer.bq()
        ),
        "flat_bq": wvc.Reconfigure.VectorIndex.flat(
            quantizer=wvc.Reconfigure.VectorIndex.Quantizer.bq()
        ),
    }

    collection = client.collections.get(class_name)
    rf = collection.config.get().replication_config.factor
    mt = collection.config.get().multi_tenancy_config.enabled
    auto_tenant_creation = (
        auto_tenant_creation
        if auto_tenant_creation != None
        else collection.config.get().multi_tenancy_config.auto_tenant_creation
    )
    auto_tenant_activation = (
        auto_tenant_activation
        if auto_tenant_activation != None
        else collection.config.get().multi_tenancy_config.auto_tenant_activation
    )
    try:
        collection.config.update(
            description=description,
            vectorizer_config=(
                vector_index_map[vector_index] if vector_index else None
            ),
            replication_config=(
                wvc.Reconfigure.replication(factor=rf, async_enabled=async_enabled)
                if async_enabled != None
                else None
            ),
            multi_tenancy_config=(
                wvc.Reconfigure.multi_tenancy(
                    auto_tenant_creation=auto_tenant_creation,
                    auto_tenant_activation=auto_tenant_activation,
                )
                if mt
                else None
            ),
        )
    except Exception as e:
        print(f"Error updating class '{class_name}': {e}")
        client.close()
        return

    assert client.collections.exists(class_name)

    print(f"Class '{class_name}' modified successfully in Weaviate.")

    client.close()

