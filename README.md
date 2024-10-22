Speech Animation Server

# Self-signed SSL certs for development

- Create self-signed certs for development:
``` bash
openssl req -x509 -newkey rsa:4096 -nodes -out dev-cert.pem -keyout dev-key.pem -days 3650
```


# Configure environment variables

Environment variables can be configured in standalone files for each environment:

- `.env.development`
- `.env.production`
- `.env.staging`

These files are omitted from version control to prevent accidental key leaks. 

The `.env.example` file is provided as a template and shows the expected format of the environment variables.

# Configure a conda environment

Set up a conda environment according to your system (rocm or cuda).

The following environment files are provided for conda:

- `conda_env_rocm.yml`

The conda environment must be activated before running the server.

# Run the development server

Activate the conda environment, then run:

``` bash
./scripts/dev.sh
```

Access the server at `https://localhost:6443`. The browser will show a warning about the self-signed certificate. Accept the risk to proceed.



