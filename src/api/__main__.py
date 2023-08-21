import flask
from dotenv import load_dotenv


from great_expectations.checkpoint.types.checkpoint_result import (
    CheckpointResult,
)
from great_expectations.data_context import FileDataContext
from great_expectations.util import get_context

import datetime

load_dotenv()


app = flask.Flask(__name__)


@app.route("/")
def index():
    return "Hello, world!"


@app.route("/checkpoint/<checkpoint_name>")
def checkpoint(checkpoint_name):
    data_context: FileDataContext = get_context(
        context_root_dir="/app/great_expectations"
    )
    checkpoints = data_context.list_checkpoints()
    if checkpoint_name not in checkpoints:
        return f"Checkpoint {checkpoint_name} does not exist!"

    result: CheckpointResult = data_context.run_checkpoint(
        checkpoint_name=checkpoint_name,
        batch_request=None,
        run_name=f"{checkpoint_name}-{datetime.datetime.now().isoformat()}",
    )

    return {"success": result["success"], "checkpoint_name": checkpoint_name}


@app.route("/suite/<suite_name>")
def suite_details(suite_name):
    data_context: FileDataContext = get_context(
        context_root_dir="/app/great_expectations"
    )
    suites = data_context.list_expectation_suites()
    suite_names = [suite.expectation_suite_name for suite in suites]
    if suite_name not in suite_names:
        return f"Suite {suite_name} does not exist!"

    suite = data_context.get_expectation_suite(suite_name)

    return suite.to_json_dict()


@app.route("/suites")
def suites():
    data_context: FileDataContext = get_context(
        context_root_dir="/app/great_expectations"
    )
    suites = data_context.list_expectation_suites()
    suite_names = [suite.expectation_suite_name for suite in suites]

    return {"suites": suite_names}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
