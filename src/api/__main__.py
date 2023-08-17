import flask
from dotenv import load_dotenv


from great_expectations.checkpoint.types.checkpoint_result import (
    CheckpointResult,
)
from great_expectations.data_context import FileDataContext
from great_expectations.util import get_context


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
        run_name=None,
    )

    return {"success": result["success"], "checkpoint_name": checkpoint_name}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
