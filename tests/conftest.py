import os
import pytest


def pytest_generate_tests(metafunc):
    os.environ["STACK_EXPIRY_TAG"] = "STACK_EXPIRY"
    os.environ["STACK_RETENTION_TAG"] = "STACK_RETENTION"
    os.environ["CDK_DEFAULT_ACCOUNT"] = "9999999"
    os.environ["CDK_DEFAULT_REGION"] = "eu-west-1"
    os.environ["CF_STACK_DELETE_PREFIX"] = "*"
    os.environ["DESTROYER_SCHEDULE"] = "* * * * *"


def mock_empty_make_api_call(self, operation_name, kwarg):
    if operation_name == "DescribeStacks":
        return {"Stacks": []}
    return {}


@pytest.fixture(scope="class")
def empty_api_call():
    return mock_empty_make_api_call
