from unittest import TestCase

from mock import Mock
from function.destroyer import Destroyer


class IsStaticStateTest(TestCase):
    testee = Destroyer(Mock(), "STACK_EXPIRY", "STACK_RETENTION")

    def test_is_static_state_returns_true_when_state_is_static(self):
        test_stack = {
            "StackName": "ShouldDelete",
        }
        test_stack["StackStatus"] = "CREATE_COMPLETE"
        self.assertTrue(self.testee.is_static_state(test_stack))
        test_stack["StackStatus"] = "UPDATE_FAILED"
        self.assertTrue(self.testee.is_static_state(test_stack))

    def test_is_static_state_returns_false_when_state_is_in_progress(self):
        test_stack = {
            "StackName": "ShouldDelete",
        }
        test_stack["StackStatus"] = "CREATE_IN_PROGRESS"
        self.assertFalse(self.testee.is_static_state(test_stack))
        test_stack["StackStatus"] = "UPDATE_IN_PROGRESS"
        self.assertFalse(self.testee.is_static_state(test_stack))

    def test_is_static_state_returns_false_when_state_is_deleted(self):
        test_stack = {
            "StackName": "ShouldDelete",
        }
        test_stack["StackStatus"] = "DELETE_COMPLETE"
        self.assertFalse(self.testee.is_static_state(test_stack))
