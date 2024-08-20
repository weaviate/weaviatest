import weaviate.classes.config as wvc
import common

def create_class(host, api_key, port, class_name, replication_factor, async_enabled,
                 vector_index, training_limit, multitenant, auto_tenant_creation,
                 auto_tenant_activation, auto_schema, shards, vectorizer):
    
    client = common.connect_to_weaviate(host, api_key, port)

    if client.collections.exists(class_name):
        print(
            f"Class '{class_name}' already exists in Weaviate. Delete using <delete class> command."
        )
        client.close()
        return

    vector_index_map = {
        "hnsw": wvc.Configure.VectorIndex.hnsw(),
        "flat": wvc.Configure.VectorIndex.flat(),
        "hnsw_pq": wvc.Configure.VectorIndex.hnsw(
            quantizer=wvc.Configure.VectorIndex.Quantizer.pq(
                training_limit=training_limit
            )
        ),
        "hnsw_bq": wvc.Configure.VectorIndex.hnsw(
            quantizer=wvc.Configure.VectorIndex.Quantizer.bq()
        ),
        "hnsw_bq_cache": wvc.Configure.VectorIndex.hnsw(
            quantizer=wvc.Configure.VectorIndex.Quantizer.bq(cache=True)
        ),
        "hnsw_sq": wvc.Configure.VectorIndex.hnsw(
            quantizer=wvc.Configure.VectorIndex.Quantizer.sq(
                training_limit=training_limit
            )
        ),
        # Should fail at the moment as Flat and PQ are not compatible
        "flat_pq": wvc.Configure.VectorIndex.flat(
            quantizer=wvc.Configure.VectorIndex.Quantizer.pq()
        ),
        # Should fail at the moment as Flat and PQ are not compatible
        "flat_sq": wvc.Configure.VectorIndex.flat(
            quantizer=wvc.Configure.VectorIndex.Quantizer.sq()
        ),
        "flat_bq": wvc.Configure.VectorIndex.flat(
            quantizer=wvc.Configure.VectorIndex.Quantizer.bq()
        ),
        "flat_bq_cache": wvc.Configure.VectorIndex.flat(
            quantizer=wvc.Configure.VectorIndex.Quantizer.bq(cache=True)
        ),
    }

    vectorizer_map = {
        "contextionary": wvc.Configure.Vectorizer.text2vec_contextionary(),
        "transformers": wvc.Configure.Vectorizer.text2vec_transformers(),
        "openai": wvc.Configure.Vectorizer.text2vec_openai(),
    }
    
    properties = [
        wvc.Property(name="title", data_type=wvc.DataType.TEXT),
        wvc.Property(name="genres", data_type=wvc.DataType.TEXT),
        wvc.Property(name="keywords", data_type=wvc.DataType.TEXT),
        wvc.Property(name="popularity", data_type=wvc.DataType.NUMBER),
        wvc.Property(name="runtime", data_type=wvc.DataType.TEXT),
        wvc.Property(name="cast", data_type=wvc.DataType.TEXT),
        wvc.Property(name="language", data_type=wvc.DataType.TEXT),
        wvc.Property(name="tagline", data_type=wvc.DataType.TEXT),
        wvc.Property(name="budget", data_type=wvc.DataType.NUMBER),
        wvc.Property(name="releaseDate", data_type=wvc.DataType.DATE),
        wvc.Property(name="revenue", data_type=wvc.DataType.NUMBER),
        wvc.Property(name="status", data_type=wvc.DataType.TEXT),
    ]
    
    try:
        collection = client.collections.create(
            name=class_name,
            vector_index_config=vector_index_map[vector_index],
            replication_config=wvc.Configure.replication(
                factor=replication_factor, async_enabled=async_enabled
            ),
            sharding_config=(
                wvc.Configure.sharding(desired_count=shards)
                if shards > 1
                else None
            ),
            multi_tenancy_config=wvc.Configure.multi_tenancy(
                enabled=multitenant,
                auto_tenant_creation=auto_tenant_creation,
                auto_tenant_activation=auto_tenant_activation,
            ),
            vectorizer_config=(
                vectorizer_map[vectorizer] if vectorizer else None
            ),
            properties=properties if auto_schema else None,
        )
    except Exception as e:
        print(f"Error creating class '{class_name}': {e}")
        client.close()
        return

    assert client.collections.exists(class_name)

    print(f"Class '{class_name}' created successfully in Weaviate.")

    client.close()
