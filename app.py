import json
import requests
from flask import Flask, request, flash, render_template, url_for, redirect

import pulumi
from pulumi.x import automation as auto
from pulumi_aws import s3

def ensure_plugins():
    ws = auto.LocalWorkspace()
    ws.install_plugin("aws", "v3.23.0")


ensure_plugins()
app = Flask(__name__)
app.secret_key = "secret"
project_name = "static-site-platyform"


# This function defines our pulumi s3 static website in terms of the content that the caller passes in.
# This allows us to dynamically deploy websites based on user defined values from the POST body.
def create_pulumi_program(content: str):
    # Create a bucket and expose a website index document
    site_bucket = s3.Bucket("s3-website-bucket", website=s3.BucketWebsiteArgs(index_document="index.html"))
    index_content = content

    # Write our index.html into the site bucket
    s3.BucketObject("index",
                    bucket=site_bucket.id,
                    content=index_content,
                    key="index.html",
                    content_type="text/html; charset=utf-8")

    # Set the access policy for the bucket so all objects are readable
    s3.BucketPolicy("bucket-policy",
                    bucket=site_bucket.id,
                    policy=site_bucket.id.apply(lambda id: json.dumps({
                        "Version": "2012-10-17",
                        "Statement": {
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": ["s3:GetObject"],
                            # Policy refers to bucket explicitly
                            "Resource": [f"arn:aws:s3:::{id}/*"]
                        },
                    })))

    # Export the website URL
    pulumi.export("website_url", site_bucket.website_endpoint)
    pulumi.export("website_content", index_content)


@app.route("/", methods=["GET"])
def index():
    """index page"""
    return render_template("index.html")

@app.route("/databases", methods=["GET"])
def list_databases():
    """index page"""
    return render_template("databases/index.html")


@app.route("/sites/new", methods=["GET", "POST"])
def create_site():
    """creates new sites"""
    if request.method == "POST":
        stack_name = request.form.get("site-id")
        file_url = request.form.get("file-url")
        if file_url:
            site_content = requests.get(file_url).text
        else:
            site_content = request.form.get("site-content")

        def pulumi_program():
            return create_pulumi_program(str(site_content))

        try:
            # create a new stack, generating our pulumi program on the fly from the POST body
            stack = auto.create_stack(stack_name=str(stack_name),
                                      project_name=project_name,
                                      program=pulumi_program)
            stack.set_config("aws:region", auto.ConfigValue("us-west-2"))
            # deploy the stack, tailing the logs to stdout
            stack.up(on_output=print)
            flash(f"Successfully created site '{stack_name}'", category="success")
        except auto.StackAlreadyExistsError:
            flash(f"Error: Site with name '{stack_name}' already exists, pick a unique name", category="danger")

        return redirect(url_for("list_sites"))

    return render_template("sites/create.html")


@app.route("/sites", methods=["GET"])
def list_sites():
    """lists all sites"""
    sites = []
    try:
        ws = auto.LocalWorkspace(project_settings=auto.ProjectSettings(name=project_name, runtime="python"))
        all_stacks = ws.list_stacks()
        for stack in all_stacks:
            stack = auto.select_stack(stack_name=stack.name,
                                      project_name=project_name,
                                      # no-op program, just to get outputs
                                      program=lambda: None)
            outs = stack.outputs()
            sites.append({"name": stack.name, "url": outs["website_url"].value})
    except Exception as exn:
        flash(str(exn), category="danger")

    return render_template("sites/index.html", sites=sites)


@app.route("/sites/<string:id>/update", methods=["GET", "POST"])
def update_site(id: str):
    stack_name = id

    if request.method == "POST":
        file_url = request.form.get("file-url")
        if file_url:
            site_content = requests.get(file_url).text
        else:
            site_content = request.form.get("site-content")

        try:
            def pulumi_program():
                create_pulumi_program(str(site_content))
            stack = auto.select_stack(stack_name=stack_name,
                                      project_name=project_name,
                                      program=pulumi_program)
            stack.set_config("aws:region", auto.ConfigValue("us-west-2"))
            # deploy the stack, tailing the logs to stdout
            stack.up(on_output=print)
            flash(f"Site '{stack_name}' successfully updated!", category="success")
        except auto.ConcurrentUpdateError:
            flash(f"Error: site '{stack_name}' already has an update in progress", category="danger")
        except Exception as exn:
            flash(str(exn), category="danger")
        return redirect(url_for("list_sites"))

    stack = auto.select_stack(stack_name=stack_name,
                              project_name=project_name,
                              # noop just to get the outputs
                              program=lambda: None)
    outs = stack.outputs()
    content_output = outs.get("website_content")
    content = content_output.value if content_output else None
    return render_template("sites/update.html", name=stack_name, content=content)


@app.route("/sites/<string:id>/delete", methods=["POST"])
def delete_site(id: str):
    stack_name = id
    try:
        stack = auto.select_stack(stack_name=stack_name,
                                  project_name=project_name,
                                  # noop program for destroy
                                  program=lambda: None)
        stack.destroy(on_output=print)
        stack.workspace.remove_stack(stack_name)
        flash(f"Site '{stack_name}' successfully deleted!", category="success")
    except auto.ConcurrentUpdateError:
        flash(f"Error: Site '{stack_name}' already has update in progress", category="danger")
    except Exception as exn:
        flash(str(exn), category="danger")

    return redirect(url_for("list_sites"))
