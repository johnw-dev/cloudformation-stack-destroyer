from unittest import TestCase

from function.destroyer import Destroyer


class Mock2NextTokensCFClient:
    def describe_stacks(self, next_token: str = None):
        if next_token and next_token == "2":
            return {"Stacks": [{"StackName": "Stack5"}, {"StackName": "Stack6"}]}
        elif next_token and next_token == "1":
            return {
                "Stacks": [{"StackName": "Stack3"}, {"StackName": "Stack4"}],
                "NextToken": "2",
            }
        else:
            return {
                "Stacks": [{"StackName": "Stack1"}, {"StackName": "Stack2"}],
                "NextToken": "1",
            }


class MockNoNextTokensCFClient:
    def describe_stacks(self, next_token: str = None):
        return {"Stacks": [{"StackName": "Stack1"}, {"StackName": "Stack2"}]}


class GetStacksTest(TestCase):
    def test_get_stacks_returns_all_stacks_with_2_next_token_loops(self):
        testee = Destroyer(Mock2NextTokensCFClient(), "STACK_EXPIRY", "STACK_RETENTION")
        stacks = testee.get_stacks()
        self.assertEqual(6, len(stacks))

    def test_get_stacks_returns_all_stacks_with_no_next_token_loops(self):
        testee = Destroyer(
            MockNoNextTokensCFClient(), "STACK_EXPIRY", "STACK_RETENTION"
        )
        stacks = testee.get_stacks()
        self.assertEqual(2, len(stacks))
