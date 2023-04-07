from function.handler import handler
from unittest import TestCase
from mock import patch
from datetime import datetime, timedelta

mocked_describe_response = []


def mock_empty_make_api_call(self, operation_name, kwarg):
    if operation_name == "DescribeStacks":
        return {"Stacks": mocked_describe_response}
    elif operation_name == "DeleteStack":
        return {}
    return {}


def generate_stack(
    name: str,
    expiry: datetime = None,
    retention: int = -1,
    status: str = "CREATE_COMPLETE",
):
    stack_json = {
        "StackName": name,
        "Tags": [{"Key": "FOO", "Value": "BAR"}],
        "LastUpdatedTime": datetime.now(),
        "StackStatus": status,
    }
    if expiry:
        stack_json["Tags"].append({"Key": "STACK_EXPIRY", "Value": expiry.isoformat()})
    if retention >= 0:
        stack_json["Tags"].append({"Key": "STACK_RETENTION", "Value": retention})
    return stack_json


class HandlerTest(TestCase):
    def assert_handler_response(self, response, totals):
        self.assertEqual(totals[0], response.get("summary").get("total"))
        self.assertEqual(totals[1], response.get("summary").get("tagged"))
        self.assertEqual(totals[2], response.get("summary").get("deleting"))
        self.assertEqual(totals[3], response.get("summary").get("delete_failed"))
        self.assertEqual(totals[4], response.get("summary").get("ignored"))

    def test_handler_response_when_no_stacks_found(self):
        global mocked_describe_response
        mocked_describe_response = []
        with patch(
            "botocore.client.BaseClient._make_api_call", new=mock_empty_make_api_call
        ):
            response = handler({}, {})
            self.assert_handler_response(response, [0, 0, 0, 0, 0])

    def test_handler_response_when_no_deletable_stacks_found(self):
        global mocked_describe_response
        mocked_describe_response = [
            generate_stack("Stay1"),
            generate_stack("Stay2"),
        ]
        with patch(
            "botocore.client.BaseClient._make_api_call", new=mock_empty_make_api_call
        ):
            response = handler({}, {})
            self.assert_handler_response(response, [2, 0, 0, 0, 2])

    def test_handler_response_when_no_stacks_in_correct_state(self):
        global mocked_describe_response
        mocked_describe_response = [
            generate_stack("Stay1", expiry=datetime.now(), status="CREATE_IN_PROGRESS"),
            generate_stack("Stay2", retention=0, status="UPDATE_IN_PROGRESS"),
        ]
        with patch(
            "botocore.client.BaseClient._make_api_call", new=mock_empty_make_api_call
        ):
            response = handler({}, {})
            self.assert_handler_response(response, [0, 0, 0, 0, 0])

    def test_handler_response_when_some_deletable_stacks_found(self):
        global mocked_describe_response
        mocked_describe_response = [
            generate_stack("Stay1"),
            generate_stack("Go1", expiry=(datetime.now() - timedelta(seconds=2))),
            generate_stack("Go2", retention=0),
        ]
        with patch(
            "botocore.client.BaseClient._make_api_call", new=mock_empty_make_api_call
        ):
            response = handler({}, {})
            self.assert_handler_response(response, [3, 2, 2, 0, 1])
