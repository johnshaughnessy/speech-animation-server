from speech.api.fastapi import create_app
import argparse
import uvicorn
from speech.utils.settings import settings


def main():
    parser = argparse.ArgumentParser(description="Speech Animation Server")
    parser.add_argument(
        "--path-client",
        type=str,
        default=settings.path_client,
        help="path to the client build directory",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host for the server (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port", type=int, default=6443, help="Port for the server (default: 6443)"
    )
    parser.add_argument(
        "--cert-file",
        type=str,
        default=settings.path_ssl_cert,
        help="path to the ssl certificate file (default: cert.pem)",
    )
    parser.add_argument(
        "--key-file",
        type=str,
        default=settings.path_ssl_key,
        help="path to the ssl key file (default: key.pem)",
    )
    args = parser.parse_args()
    app = create_app(args.path_client)

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        ssl_keyfile=args.key_file,
        ssl_certfile=args.cert_file,
    )


if __name__ == "__main__":
    main()
