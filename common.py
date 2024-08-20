import socket
import weaviate

def check_host_docker_internal():
    """Check if host.docker.internal is reachable."""
    try:
        # Attempt to connect to host.docker.internal on any port (e.g., 80)
        fd = socket.create_connection(("host.docker.internal", 80), timeout=2)
        fd.close()  # Close the socket
        return True
    except (socket.timeout, socket.error):
        return False

def get_host():
    """Determine the appropriate host based on the environment."""
    if check_host_docker_internal():
        return "host.docker.internal"  # macOS/Windows Docker
    else:
        return "localhost"  # Default fallback (Linux or unreachable)

def connect_to_weaviate(host, api_key, port):
 # Connect to Weaviate instance
    if host == "localhost":
        client = weaviate.connect_to_local(host=get_host(), port=port)
    else:
        client = weaviate.connect_to_wcs(
            cluster_url=host,
            auth_credentials=weaviate.auth.AuthApiKey(api_key=api_key),
        )
    return client