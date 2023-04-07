from unittest import TestCase

from unittest.mock import Mock
from function.destroyer import Destroyer


class DeleteStackTest(TestCase):
    def test_delete_stack_returns_true_when_delete_succeeds(self):
        cf_client_mock = Mock()
        cf_client_mock.delete_stack = Mock(return_value={})
        testee = Destroyer(cf_client_mock, "STACK_EXPIRY", "STACK_RETENTION")
        test_stack = {
            "StackName": "ShouldDelete",
        }
        self.assertTrue(testee.delete_stack(test_stack))

    def test_delete_stack_returns_false_when_delete_fails(self):
        test_stack = {
            "StackName": "ShouldFail",
        }
        cf_client_mock = Mock()
        cf_client_mock.delete_stack = Mock(side_effect=Exception("Fail"))
        testee = Destroyer(cf_client_mock, "STACK_EXPIRY", "STACK_RETENTION")
        self.assertFalse(testee.delete_stack(test_stack))
