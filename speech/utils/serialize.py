def serialize(data):

    if isinstance(data, list):
        return [serialize(item) for item in data]

    elif isinstance(data, tuple):
        return [serialize(item) for item in data]

    if isinstance(data, dict):
        return {
            key: serialize(value)
            for key, value in data.items()
            if key != "_sa_instance_state"
        }

    if hasattr(data, "_asdict"):
        return serialize(data._asdict())

    if hasattr(data, "__dict__"):
        return {
            key: serialize(value)
            for key, value in data.__dict__.items()
            if key != "_sa_instance_state"
        }

    return data
