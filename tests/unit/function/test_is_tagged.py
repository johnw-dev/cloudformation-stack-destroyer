from unittest import TestCase

from mock import Mock
from function.destroyer import Destroyer


class IsTaggedTest(TestCase):
    testee = Destroyer(Mock(), "STACK_EXPIRY", "STACK_RETENTION")

    def test_is_tagged_returns_true_when_tags_present(self):
        test_stack = {
            "StackName": "ShouldDelete",
        }
        test_stack["Tags"] = [{"Key": "STACK_RETENTION", "Value": "something"}]
        self.assertTrue(self.testee.is_tagged(test_stack))
        test_stack["Tags"] = [{"Key": "STACK_EXPIRY", "Value": "something"}]
        self.assertTrue(self.testee.is_tagged(test_stack))

    def test_is_tagged_returns_false_when_tags_not_present(
        self,
    ):
        test_stack = {"StackName": "ShouldDelete", "Tags": []}
        self.assertFalse(self.testee.is_tagged(test_stack))
