# tap-sellercloud

`tap-sellercloud` is a Singer tap for Sellercloud.



## Installation

```bash
pipx install tap-sellercloud
```

## Configuration

### Accepted Config Options


A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-sellercloud --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

```bash
{
  "server_id":"Sellercloud server id",
  "username":"Sellercloud username",
  "password": "SellerCloud password"
}
```


### Executing the Tap Directly

```bash
tap-sellercloud --version
tap-sellercloud --help
tap-sellercloud --config CONFIG --discover > ./catalog.json
```


### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_sellercloud/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-sellercloud` CLI interface directly using `poetry run`:

```bash
poetry run tap-sellercloud --help
```
