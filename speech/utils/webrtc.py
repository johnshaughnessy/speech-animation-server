peer_connections = {}


def peer_connection_for_session_id(session_id: str):
    return peer_connections.get(session_id)
