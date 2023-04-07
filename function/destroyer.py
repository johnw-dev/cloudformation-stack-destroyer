import logging
from datetime import datetime, timedelta
from dateutil import parser

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

STATUS_FILTER = [
    "CREATE_FAILED",
    "CREATE_COMPLETE",
    "ROLLBACK_FAILED",
    "ROLLBACK_COMPLETE",
    "DELETE_FAILED",
    "UPDATE_COMPLETE",
    "UPDATE_FAILED",
    "UPDATE_ROLLBACK_FAILED",
    "UPDATE_ROLLBACK_COMPLETE",
    "IMPORT_COMPLETE",
    "IMPORT_ROLLBACK_FAILED",
    "IMPORT_ROLLBACK_COMPLETE",
]


class Destroyer:
    def __init__(self, cloudformation, expiry_tag, retention_tag):
        self.cf_client = cloudformation
        self.expiry_tag = expiry_tag
        self.retention_tag = retention_tag

    def delete_stack(self, stack):
        ### issue stack deletion command and delete sub resources ###
        logger.info(f"deleting stack {stack.get('StackName')}")
        try:
            self.cf_client.delete_stack(StackName=stack.get("StackName"))
        except Exception as e:
            logger.exception(e)
            return False
        logger.info(f"deleted stack {stack.get('StackName')}")
        return True

    def is_static_state(self, stack):
        if stack.get("StackStatus") in STATUS_FILTER:
            return True
        return False

    def is_tagged(self, stack):
        keys = list(map(lambda x: x.get("Key"), stack.get("Tags", [])))
        logger.debug(f"{stack} {self.expiry_tag} {self.retention_tag} {keys}")
        if self.expiry_tag in keys or self.retention_tag in keys:
            return True
        return False

    def is_deletable(self, stack):
        ### determine if stack should be deleted ###
        now = datetime.now()
        tags = stack.get("Tags", [])
        logger.debug(f"should delete stack based on tags? {tags}")
        for tag in tags:
            if tag.get("Key") == self.expiry_tag:
                try:
                    expiry = parser.parse(tag.get("Value"))
                    logger.debug(f"EXPIRY_TAG: {expiry} <= {now}")
                    if expiry.timestamp() <= now.timestamp():
                        return True
                except Exception as e:
                    logger.exception(e)
            if tag.get("Key") == self.retention_tag:
                try:
                    last_updated_time = stack.get("LastUpdatedTime", "")
                    retention = float(
                        tag.get(
                            "Value",
                        )
                    )
                    expiry = last_updated_time + timedelta(milliseconds=retention)
                    logger.debug(
                        f"RETENTION_TAG: {last_updated_time} + {retention}ms = {expiry} <= {now}"
                    )
                    if expiry.timestamp() <= now.timestamp():
                        return True
                except Exception as e:
                    logger.exception(e)
        return False

    def get_stacks(self):
        ### loop over stack lists ###
        response = self.cf_client.describe_stacks()
        stacks = response.get("Stacks", [])
        next_token = response.get("NextToken", None)

        # in case there are a serious number of stacks
        while next_token is not None:
            response = self.cf_client.describe_stacks(next_token)
            stacks = stacks + response.get("Stacks", [])
            next_token = response.get("NextToken", None)
        logger.info(stacks)
        return stacks

    def delete_all_stacks(self):
        stacks = list(filter(self.is_static_state, self.get_stacks()))
        tagged_stacks = list(filter(self.is_tagged, stacks))
        deletable_stacks = list(filter(self.is_deletable, tagged_stacks))
        deleted_stacks = list(filter(self.delete_stack, deletable_stacks))

        totals = {
            "total": len(stacks),
            "tagged": len(tagged_stacks),
            "deleting": len(deleted_stacks),
            "delete_failed": len(deletable_stacks) - len(deleted_stacks),
            "ignored": len(stacks) - len(deletable_stacks),
        }
        response = {
            "summary": totals,
        }
        return response
