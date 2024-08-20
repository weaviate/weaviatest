#!/usr/bin/env python3

import click
from lib.create_class import create_class
from lib.create_tenants import create_tenants
from lib.create_backup import create_backup
from lib.delete_class import delete_class
from lib.delete_data import delete_data
from lib.delete_tenants import delete_tenants
from lib.create_data import ingest_data
from lib.update_class import update_class
from lib.update_data import update_data
from lib.update_tenants import update_tenants
from lib.query_data import query_data
from lib.restore_backup import restore_backup

# General CLI group for Weaviate operations
@click.group()
@click.option("--host", default="localhost", help="Weaviate host (default: 'localhost').")
@click.option("--api_key", default=None, help="Weaviate API key (default: None).")
@click.option("--port", default=8080, help="Weaviate port (default: 8080).")
@click.pass_context
def cli(ctx, host, api_key, port):
    """
    Weaviate CLI for managing classes, tenants, and data.
    """
    # Store the general options in the context object for use in subcommands
    ctx.ensure_object(dict)
    ctx.obj['host'] = host
    ctx.obj['api_key'] = api_key
    ctx.obj['port'] = port

# Create Group
@cli.group()
def create():
    """Create resources in Weaviate."""
    pass

# Delete Group
@cli.group()
def delete():
    """Delete resources in Weaviate."""
    pass

# Update Group
@cli.group()
def update():
    """Update resources in Weaviate."""
    pass

# Query Group
@cli.group()
def query():
    """Query resources in Weaviate."""
    pass

@cli.group()
def restore():
    """Restore backups in Weaviate."""
    pass

# Subcommand to create a class
@create.command("class")
@click.option("--class_name", default="Movies", help="The name of the class to create.")
@click.option("--replication_factor", default=3, help="Replication factor (default: 3).")
@click.option("--async_enabled", is_flag=True, help="Enable async (default: False).")
@click.option("--vector_index", default="hnsw", type=click.Choice(["hnsw", "flat", "hnsw_pq", "hnsw_bq", "hnsw_sq", "flat_bq"]), help="Vector index type (default: 'hnsw').")
@click.option("--training_limit", default=10000, help="Training limit for PQ and SQ (default: 10000).")
@click.option("--multitenant", is_flag=True, help="Enable multitenancy (default: False).")
@click.option("--auto_tenant_creation", is_flag=True, help="Enable auto tenant creation (default: False).")
@click.option("--auto_tenant_activation", is_flag=True, help="Enable auto tenant activation (default: False).")
@click.option("--auto_schema", default=True, help="Enable auto-schema (default: True).")
@click.option("--shards", default=1, help="Number of shards (default: 1).")
@click.option("--vectorizer", default=None, type=click.Choice(['contextionary', 'transformers', 'openai']),
              help="Vectorizer to use.")
@click.pass_context
def create_class_cli(ctx, class_name, replication_factor, async_enabled, vector_index,
                     training_limit, multitenant, auto_tenant_creation, auto_tenant_activation,
                     auto_schema, shards, vectorizer):
    """Create a class in Weaviate."""

    # Access the general arguments from the context object
    host = ctx.obj['host']
    api_key = ctx.obj['api_key']
    port = ctx.obj['port']

    # Call the function from create_class.py passing both general and specific arguments
    create_class(
        host=host,
        api_key=api_key,
        port=port,
        class_name=class_name,
        replication_factor=replication_factor,
        async_enabled=async_enabled,
        vector_index=vector_index,
        training_limit=training_limit,
        multitenant=multitenant,
        auto_tenant_creation=auto_tenant_creation,
        auto_tenant_activation=auto_tenant_activation,
        auto_schema=auto_schema,
        shards=shards,
        vectorizer=vectorizer
    )

# Subcommand to ingest data
@create.command("data")
@click.option("--class_name", default="Movies", help="The name of the class to ingest data into.")
@click.option("--number_objects", default=1000, help="Number of objects to import (default: 1000).")
@click.option("--consistency_level", default="quorum", type=click.Choice(["quorum", "all", "one"]), help="Consistency level (default: 'quorum').")
@click.option("--randomize", is_flag=True, help="Randomize the data (default: False).")
@click.option("--auto_tenants", is_flag=True, help="Enable auto tenants (default: False).")
@click.pass_context
def create_data_cli(ctx, class_name, number_objects, consistency_level, randomize, auto_tenants):
    """Ingest data into a class in Weaviate."""
    
    # Access the general arguments from the context object
    host = ctx.obj['host']
    api_key = ctx.obj['api_key']
    port = ctx.obj['port']
    
    # Call the function from ingest_data.py with general and specific arguments
    ingest_data(
        host=host,
        api_key=api_key,
        port=port,
        class_name=class_name,
        number_objects=number_objects,
        consistency_level=consistency_level,
        randomize=randomize,
        auto_tenants=auto_tenants
    )
    
# Subcommand to create tenants (without --vectorizer option)
@create.command("tenants")
@click.option("--class_name", default="Movies", help="The name of the class to create.")
@click.option("--tenant_suffix", default="Tenant--", help="The suffix to add to the tenant name (default: 'Tenant--').")
@click.option("--number_tenants", default=100, help="Number of tenants to create (default: 100).")
@click.option("--state", default="active", type=click.Choice(["hot", "active", "cold", "inactive", "frozen", "offloaded"]))
@click.pass_context
def create_tenants_cli(ctx, class_name, tenant_suffix, number_tenants, state):
    """Create tenants in Weaviate."""

    # Access the general arguments from the context object
    host = ctx.obj['host']
    api_key = ctx.obj['api_key']
    port = ctx.obj['port']

    # Call the function from create_tenants.py with general and specific arguments
    create_tenants(
        host=host, 
        api_key=api_key,
        port=port,
        class_name=class_name,
        tenant_suffix=tenant_suffix,
        number_tenants=number_tenants,
        state=state
    )

@create.command("backup")
@click.option("--backend", default="s3", type=click.Choice(["s3", "gcs", "filesystem"]), help="The backend used for storing the backups (default: s3).")
@click.option("--backup_id", default="test-backup", help="Identifier used for the backup (default: test-backup).")
@click.option("--include", default=None, help="Comma separated list of collections to include in the backup. If not provided, all collections will be included.")
@click.option("--exclude", default=None, help="Comma separated list of collections to exclude from the backup. If not provided, all collections will be included.")
@click.option("--wait", is_flag=True, help="Wait for the backup to complete before returning.")
@click.option("--cpu_for_backup", default=40, help="The percentage of CPU to use for the backup (default: 40). The larger, the faster it will occur, but it will also consume more memory.")
@click.pass_context
def create_backup_cli(ctx, backend, backup_id, include, exclude, wait, cpu_for_backup):
    """Create a backup in Weaviate."""
    
    # Access the general arguments from the context object
    host = ctx.obj['host']
    api_key = ctx.obj['api_key']
    port = ctx.obj['port']
    
    # Call the function from create_backup.py with general and specific arguments
    create_backup(
        host=host,
        api_key=api_key,
        port=port,
        backend=backend,
        backup_id=backup_id,
        include=include,
        exclude=exclude,
        wait=wait,
        cpu_for_backup=cpu_for_backup
    )

@delete.command("class")
@click.option("--class_name", default="Movies", help="The name of the class to delete.")
@click.pass_context
def delete_class_cli(ctx, class_name):
    """Delete a class in Weaviate."""
    
    # Access the general arguments from the context object
    host = ctx.obj['host']
    api_key = ctx.obj['api_key']
    port = ctx.obj['port']
    
    # Call the function from delete_class.py with general and specific arguments
    delete_class(
        host=host,
        api_key=api_key,
        port=port,
        class_name=class_name
    )

@delete.command("data")
@click.option("--class_name", default="Movies", help="The name of the class to delete tenants from.")
@click.option("--number_objects", default=100, help="Number of objects to delete (default: 100).")
@click.option("--consistency_level", default="quorum", type=click.Choice(["quorum", "all", "one"]), help="Consistency level (default: 'quorum').")
@click.pass_context
def delete_data_cli(ctx, class_name, number_objects, consistency_level):
    """Delete data from a class in Weaviate."""
    
    # Access the general arguments from the context object
    host = ctx.obj['host']
    api_key = ctx.obj['api_key']
    port = ctx.obj['port']
    
    # Call the function from delete_data.py with general and specific arguments
    delete_data(
        host=host,
        api_key=api_key,
        port=port,
        class_name=class_name,
        number_objects=number_objects,
        consistency_level=consistency_level
    )

@delete.command("tenants")
@click.option("--class_name", default="Movies", help="The name of the class to delete tenants from.")
@click.option("--tenant_suffix", default="Tenant--", help="The suffix to add to the tenant name (default: 'Tenant--').")
@click.option("--number_tenants", default=100, help="Number of tenants to delete (default: 100).")
@click.pass_context
def delete_tenants_cli(ctx, class_name, tenant_suffix, number_tenants):
    """Delete tenants from a class in Weaviate."""
    
    # Access the general arguments from the context object
    host = ctx.obj['host']
    api_key = ctx.obj['api_key']
    port = ctx.obj['port']
    
    # Call the function from delete_tenants.py with general and specific arguments
    delete_tenants(
        host=host,
        api_key=api_key,
        port=port,
        class_name=class_name,
        tenant_suffix=tenant_suffix,
        number_tenants=number_tenants
    )

@update.command("class")
@click.option("--class_name", default="Movies", help="The name of the class to update.")
@click.option("--async_enabled", default=None, type=bool, help="Enable async (default: None).")
@click.option("--vector_index", default=None, type=click.Choice(["hnsw", "flat", "hnsw_pq", "hnsw_bq", "hnsw_sq", "flat_bq"]), help='Vector index type (default: "None").')
@click.option("--description", default=None, help="Class description (default: None).")
@click.option("--training_limit", default=10000, help="Training limit for PQ and SQ (default: 10000).")
@click.option("--auto_tenant_creation",  default=None, type=bool, help="Enable auto tenant creation (default: None).")
@click.option("--auto_tenant_activation",  default=None, type=bool, help="Enable auto tenant activation (default: None).")
@click.pass_context
def update_class_cli(ctx, class_name, async_enabled, vector_index, description, training_limit, auto_tenant_creation, auto_tenant_activation):
    """Update a class in Weaviate."""
    
    # Access the general arguments from the context object
    host = ctx.obj['host']
    api_key = ctx.obj['api_key']
    port = ctx.obj['port']
    
    # Call the function from update_class.py with general and specific arguments
    update_class(
        host=host,
        api_key=api_key,
        port=port,
        class_name=class_name,
        async_enabled=async_enabled,
        vector_index=vector_index,
        description=description,
        training_limit=training_limit,
        auto_tenant_creation=auto_tenant_creation,
        auto_tenant_activation=auto_tenant_activation
    )

@update.command("data")
@click.option("--class_name", default="Movies", help="The name of the class to update.")
@click.option("--number_objects", default=100, help="Number of objects to update (default: 100).")
@click.option("--consistency_level", default="quorum", type=click.Choice(["quorum", "all", "one"]), help="Consistency level (default: 'quorum').")
@click.option("--randomize", is_flag=True, help="Randomize the data (default: False).")
@click.pass_context
def update_data_cli(ctx, class_name, number_objects, consistency_level, randomize):
    """Update data in a class in Weaviate."""
    
    # Access the general arguments from the context object
    host = ctx.obj['host']
    api_key = ctx.obj['api_key']
    port = ctx.obj['port']
    
    # Call the function from update_data.py with general and specific arguments
    update_data(
        host=host,
        api_key=api_key,
        port=port,
        class_name=class_name,
        number_objects=number_objects,
        consistency_level=consistency_level,
        randomize=randomize
    )


@update.command("tenants")
@click.option("--class_name", default="Movies", help="The name of the class to update.")
@click.option("--tenant_suffix", default="Tenant--", help="The suffix to add to the tenant name (default: 'Tenant--').")
@click.option("--number_tenants", default=100, help="Number of tenants to update (default: 100).")
@click.option("--state", default="active", type=click.Choice(["hot", "active", "cold", "inactive", "frozen", "offloaded"]))
@click.pass_context
def update_tenants_cli(ctx, class_name, tenant_suffix, number_tenants, state):
    """Update tenants in Weaviate."""
    
    # Access the general arguments from the context object
    host = ctx.obj['host']
    api_key = ctx.obj['api_key']
    port = ctx.obj['port']
    
    # Call the function from update_tenants.py with general and specific arguments
    update_tenants(
        host=host,
        api_key=api_key,
        port=port,
        class_name=class_name,
        tenant_suffix=tenant_suffix,
        number_tenants=number_tenants,
        state=state
    )
@restore.command("backup")
@click.option("--backend", default="s3", type=click.Choice(["s3", "gcs", "filesystem"]), help="The backend used for storing the backups (default: s3).")
@click.option("--backup_id", default="test-backup", help="Identifier used for the backup (default: test-backup).")
@click.option("--wait", is_flag=True, help="Wait for the backup to complete before returning.")
@click.pass_context
def restore_backup_cli(ctx, backend, backup_id, wait):
    """Restore a backup in Weaviate."""
    
    # Access the general arguments from the context object
    host = ctx.obj['host']
    api_key = ctx.obj['api_key']
    port = ctx.obj['port']
    
    # Call the function from restore_backup.py with general and specific arguments
    restore_backup(
        host=host,
        api_key=api_key,
        port=port,
        backend=backend,
        backup_id=backup_id,
        wait=wait
    )

@query.command("data")
@click.option("--class_name", default="Movies", help="The name of the class to query.")
@click.option("--search_type", default="fetch", type=click.Choice(["fetch", "vector", "keyword", "hybrid"]), help='Search type (default: "fetch").')
@click.option("--query", default="Action movie", help="Query string for the search. Only used when search type is vector, keyword or hybrid (default: 'Action movie').")
@click.option("--consistency_level", default="quorum", type=click.Choice(["quorum", "all", "one"]), help="Consistency level (default: 'quorum').")
@click.option("--number_objects", default=10, help="Number of objects to query (default: 10).")
@click.pass_context
def query_data_cli(ctx, class_name, search_type, query, consistency_level, number_objects):
    """Query data in a class in Weaviate."""
    
    # Access the general arguments from the context object
    host = ctx.obj['host']
    api_key = ctx.obj['api_key']
    port = ctx.obj['port']
    
    # Call the function from query_data.py with general and specific arguments
    query_data(
        host=host,
        api_key=api_key,
        port=port,
        class_name=class_name,
        search_type=search_type,
        query=query,
        consistency_level=consistency_level,
        number_objects=number_objects
    )

if __name__ == "__main__":
    cli()
