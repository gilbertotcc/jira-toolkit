# Jira toolkit

Python library to interact with Jira.

## Bruno collection

In the directory `bruno` you can find a [Bruno](https://www.usebruno.com/)
collection to interact with the Jira API.

To use it with the *Default* environment you must set the following environment
variables:

* `BASE_URL`: Base URL of the Jira account (e.g.,
  <https://example.atlassian.net>)
* `JIRA_USER`: Email of the Jira user associated with the token.
* `JIRA_TOKEN`: Token to interact with the API.

You can define these variables through a `.env` file.
You can find an example in `bruno/Jira/.env.sample`.

## Python library

This project uses [uv](https://github.com/astral-sh/uv).

To install the required dependencies, move to the project root and run:

```shell
uv sync
```

If you need to develop new scripts and implement new code, then install also the
development dependencies with:

```shell
uv sync --dev
```

### Environment variables

These environment variables must be set to make use the toolkit.
You can use a `.env` file for it.

* `JIRA_SERVER`: Base URL of the Jira account (e.g.,
  <https://example.atlassian.net>)
* `JIRA_USER`: The email address of the Atlassian user to interact with the
  Atlassian services.
* `JIRA_TOKEN`: The Atlassian API token.

## References

* [Jira Cloud Platform API reference](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro)
* [Jira Software Cloud API reference](https://developer.atlassian.com/cloud/jira/software/rest/intro/)
