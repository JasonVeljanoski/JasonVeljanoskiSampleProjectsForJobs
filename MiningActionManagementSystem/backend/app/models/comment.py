from .base import BaseID


class Comment(BaseID):
    user_id: int = None
    comment: str = None


class Action_Comment(Comment):
    action_id: int = None


class Feedback_Comment(Comment):
    feedback_id: int = None
