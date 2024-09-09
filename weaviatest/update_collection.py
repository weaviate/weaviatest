import weaviate.classes.config as wvc


def update_collection(
    client,
    collection,
    description,
    vector_index,
    training_limit,
    async_enabled,
    auto_tenant_creation,
    auto_tenant_activation,
):

    if not client.collections.exists(collection):

        raise Exception(
            f"Collection '{collection}' does not exist in Weaviate. Create first using ./create_collection.py"
        )

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

    col_obj = client.collections.get(collection)
    rf = col_obj.config.get().replication_config.factor
    mt = col_obj.config.get().multi_tenancy_config.enabled
    auto_tenant_creation = (
        auto_tenant_creation
        if auto_tenant_creation is not None
        else col_obj.config.get().multi_tenancy_config.auto_tenant_creation
    )
    auto_tenant_activation = (
        auto_tenant_activation
        if auto_tenant_activation is not None
        else col_obj.config.get().multi_tenancy_config.auto_tenant_activation
    )

    col_obj.config.update(
        description=description,
        vectorizer_config=(vector_index_map[vector_index] if vector_index else None),
        replication_config=(
            wvc.Reconfigure.replication(factor=rf, async_enabled=async_enabled)
            if async_enabled is not None
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

    assert client.collections.exists(collection)

    print(f"Collection '{collection}' modified successfully in Weaviate.")
