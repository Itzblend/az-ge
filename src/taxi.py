import great_expectations as ge
from great_expectations.core.batch import BatchRequest, RuntimeBatchRequest
from great_expectations.data_context import FileDataContext
from great_expectations.util import get_context
from great_expectations.core.expectation_configuration import ExpectationConfiguration


from ruamel import yaml


def get_azure_datastore_config() -> dict:
    return {
        "name": "taxi_azure_datastore",
        "class_name": "Datasource",
        "execution_engine": {
            "class_name": "PandasExecutionEngine",
            "azure_options": {"conn_str": "${AZURE_STORAGE_CONNECTION_STRING}"},
        },
        "data_connectors": {
            "azure_data_connector": {
                "class_name": "ConfiguredAssetAzureDataConnector",
                "azure_options": {"conn_str": "${AZURE_STORAGE_CONNECTION_STRING}"},
                "container": "nyctaxi",  # Correct
                "name_starts_with": "taxidata/",  # Directory name, NOT REGEX
                "default_regex": {
                    "group_names": ["taxi"],  # DOESNT MATTER
                    "pattern": "taxidata/yellow_tripdata_(.*)\.csv",  # ACTUAL REGEX FOR THE FILES
                },
                "assets": {"taxi_asset": None},
            }
        },
    }


def get_checkpoint_config() -> dict:
    return {
        "name": "taxi_checkpoint",
        "config_version": 1.0,
        "class_name": "Checkpoint",
        "runtime_configuration": {
            "result_format": "COMPLETE",
            "partial_unexpected_count": 20,
            "run_name_template": "{run_name}-{run_time}",
        },
        "action_list": [
            {
                "name": "store_validation_result",
                "action": {"class_name": "StoreValidationResultAction"},
            },
            {
                "name": "store_evaluation_params",
                "action": {"class_name": "StoreEvaluationParametersAction"},
            },
            {
                "name": "update_data_docs",
                "action": {"class_name": "UpdateDataDocsAction"},
            },
        ],
    }


def get_azure_batch_request():
    batch_request = BatchRequest(
        datasource_name="taxi_azure_datastore",
        data_connector_name="azure_data_connector",
        data_asset_name="taxi_asset",
        batch_spec_passthrough={
            "reader_method": "read_csv",
            "reader_options": {"header": 0, "sep": ","},
        },
    )
    return batch_request


def add_expectations_to_suite(suite):
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_table_row_count_to_be_between",
            kwargs={
                "min_value": 1,
                "max_value": 5000,
            },
        )
    )
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_dateutil_parseable",
            kwargs={
                "column": "tpep_pickup_datetime",
            },
        )
    )

    return suite


def add_batch_request_to_checkpoint(checkpoint_config, batch_request, suite_name):
    imputed = False

    if "validations" not in checkpoint_config:
        checkpoint_config["validations"] = []

    for validation in checkpoint_config["validations"]:
        if validation["expecation_suite_name"] == suite_name:
            validation["batch_request"] = batch_request
            imputed = True

    if not imputed:
        checkpoint_config["validations"].append(
            {
                "batch_request": batch_request,
                "expectation_suite_name": suite_name,
            }
        )

    return checkpoint_config


def create_taxi_config():
    context = get_context()

    # Datasource
    datasource_config = get_azure_datastore_config()

    context.test_yaml_config(yaml.dump(datasource_config))
    context.add_or_update_datasource(**datasource_config)
    # Checkpoint
    checkpoint_config = get_checkpoint_config()

    context.add_or_update_expectation_suite("taxi_suite")
    suite = context.get_expectation_suite("taxi_suite")

    suite = add_expectations_to_suite(suite)
    batch_request = get_azure_batch_request()

    context.save_expectation_suite(suite)

    checkpoint_config = add_batch_request_to_checkpoint(
        checkpoint_config, batch_request, "taxi_suite"
    )

    context.add_or_update_datasource(**datasource_config)

    context.test_yaml_config(yaml.dump(checkpoint_config))
    context.add_or_update_checkpoint(**checkpoint_config)

    context.run_checkpoint("taxi_checkpoint")


def main():
    create_taxi_config()


if __name__ == "__main__":
    main()
