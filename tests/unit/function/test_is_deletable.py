from datetime import datetime, timedelta
from unittest import TestCase

from mock import Mock
from function.destroyer import Destroyer


class IsDeletableTest(TestCase):
    testee = Destroyer(Mock(), "STACK_EXPIRY", "STACK_RETENTION")

    def test_is_deleteable_returns_true_when_passed_expiry(self):
        test_stack = {
            "StackName": "ShouldDelete",
            "Tags": [
                {
                    "Key": "STACK_EXPIRY",
                    "Value": (datetime.now() - timedelta(seconds=2)).isoformat(),
                }
            ],
        }
        self.assertTrue(self.testee.is_deletable(test_stack))

    def test_is_deleteable_returns_true_when_passed_retention(self):
        test_stack = {
            "StackName": "ShouldDelete",
            "LastUpdatedTime": (datetime.now() - timedelta(seconds=2)),
            "Tags": [{"Key": "STACK_RETENTION", "Value": "0"}],
        }
        self.assertTrue(self.testee.is_deletable(test_stack))

    def test_is_deleteable_returns_false_when_expiry_not_passed(self):
        test_stack = {
            "StackName": "ShouldDelete",
            "Tags": [
                {
                    "Key": "STACK_EXPIRY",
                    "Value": (datetime.now() + timedelta(seconds=5)).isoformat(),
                }
            ],
        }
        self.assertFalse(self.testee.is_deletable(test_stack))

    def test_is_deleteable_returns_false_when_passed_retention(self):
        test_stack = {
            "StackName": "ShouldDelete",
            "LastUpdatedTime": datetime.now().timestamp(),
            "Tags": [{"Key": "STACK_RETENTION", "Value": "5000"}],
        }
        self.assertFalse(self.testee.is_deletable(test_stack))

    def test_is_deletable_returns_false_when_retention_tag_invalid(self):
        test_stack = {
            "StackName": "ShouldDelete",
            "LastUpdatedTime": (datetime.now() - timedelta(seconds=2)).timestamp(),
            "Tags": [{"Key": "STACK_RETENTION", "Value": "foobar"}],
        }
        self.assertFalse(self.testee.is_deletable(test_stack))

    def test_is_deletable_returns_false_when_expiry_tag_invalid(self):
        test_stack = {
            "StackName": "ShouldDelete",
            "LastUpdatedTime": (datetime.now() - timedelta(seconds=2)).timestamp(),
            "Tags": [{"Key": "STACK_EXPIRY", "Value": "foobar"}],
        }
        self.assertFalse(self.testee.is_deletable(test_stack))

    def test_is_deletable_returns_false_when_retention_tag_none(self):
        test_stack = {
            "StackName": "ShouldDelete",
            "LastUpdatedTime": (datetime.now() - timedelta(seconds=2)).timestamp(),
            "Tags": [{"Key": "STACK_RETENTION", "Value": None}],
        }
        self.assertFalse(self.testee.is_deletable(test_stack))

    def test_is_deletable_returns_false_when_expiry_tag_none(self):
        test_stack = {
            "StackName": "ShouldDelete",
            "LastUpdatedTime": (datetime.now() - timedelta(seconds=2)).timestamp(),
            "Tags": [{"Key": "STACK_EXPIRY", "Value": None}],
        }
        self.assertFalse(self.testee.is_deletable(test_stack))

    def test_should_delete_stack_with_no_tag(self):
        test_stack1 = {"StackName": "ShouldDelete", "Tags": []}
        self.assertFalse(self.testee.is_deletable(test_stack1))
        test_stack2 = {
            "StackName": "ShouldDelete",
            "Tags": [{"Key": "FOOBAR", "Value": "FOOBAR"}],
        }
        self.assertFalse(self.testee.is_deletable(test_stack2))
