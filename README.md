# Static Website Platyform

This application demonstrates how to run Automation API in an HTTP server to expose infrastructure as RESTful resources. In our case, we've defined and exposed a static website `site` that exposes all of the `CRUD` operations plus list. Users can hit our REST endpoint and create custom static websites by specifying the `content` field in the `POST` body. All of our infrastructure is defined in `inline` programs that are constructed and altered on the fly based on input parsed from user-specified `POST` bodies. Be sure to read through the handlers to see how Automation API detect structured error cases such as update conflicts (409), and missing stacks (404).

To run this example you'll need a few pre-reqs:
1. A Pulumi CLI installation ([v2.10.1](https://www.pulumi.com/docs/get-started/install/versions/) or later)
2. The AWS CLI, with appropriate credentials.

In one terminal window, run the HTTP server that uses Automation API. It will also stream update logs:

```bash
$ FLASK_RUN_PORT=1337 FLASK_ENV=development venv/bin/flask run
* Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:1337/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 328-006-235
```
