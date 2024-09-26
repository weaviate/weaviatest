import socket
import string
import random
import weaviate
import os


def check_host_docker_internal(port=8080):
    """Check if host.docker.internal is reachable."""
    try:
        # Attempt to connect to host.docker.internal on any port (e.g., 80)
        fd = socket.create_connection(("host.docker.internal", port), timeout=2)
        fd.close()  # Close the socket
        return True
    except (socket.timeout, socket.error):
        return False


def get_host(port):
    """Determine the appropriate host based on the environment."""
    if check_host_docker_internal(port):
        return "host.docker.internal"  # macOS/Windows Docker
    else:
        return "localhost"  # Default fallback (Linux or unreachable)


def connect_to_weaviate(host, api_key, port, grpc_port):
    openai_key = os.getenv("OPENAI_APIKEY")
    headers = {
        "X-OpenAI-Api-Key": openai_key,
    }
    # Connect to Weaviate instance
    if host == "localhost":
        client = weaviate.connect_to_local(
            host=get_host(port),
            port=port,
            grpc_port=grpc_port,
            headers=headers if openai_key is not None else None,
        )
    else:
        client = weaviate.connect_to_wcs(
            cluster_url=host,
            auth_credentials=weaviate.auth.AuthApiKey(api_key=api_key),
            headers=headers if openai_key is not None else None,
        )
    return client


# Insert objects to the replicated collection
def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


# Pretty print objects in the response in a table format
def pp_objects(response, main_properties):

    if len(response.objects) == 0:
        print("No objects found")
        return

    # Create the header
    header = f"{'ID':<37}"
    for prop in main_properties:
        header += f"{prop.capitalize():<37}"
    header += f"{'Distance':<11}{'Certainty':<11}{'Score':<11}"
    print(header)

    # Print each object
    for obj in response.objects:
        row = f"{str(obj.uuid):<36} "
        for prop in main_properties:
            row += f"{obj.properties.get(prop, '')[:36]:<36} "
        row += f"{str(obj.metadata.distance)[:10] if obj.metadata.distance else 'None':<10} "
        row += f"{str(obj.metadata.certainty)[:10] if obj.metadata.certainty else 'None':<10} "
        row += f"{str(obj.metadata.score)[:10] if obj.metadata.score else 'None':<10}"
        print(row)

    # Print footer
    footer = f"{'':<37}" * (len(main_properties) + 1) + f"{'':<11}{'':<11}{'':<11}"
    print(footer)
    print(f"Total: {len(response.objects)} objects")
