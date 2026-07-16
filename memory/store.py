"""SQLite-backed memory store for user interaction history and preference summaries."""


class MemoryStore:
    """
    Wraps a SQLite database holding:
      - episodic memory: raw interaction history per user
      - long-term memory: rolling preference summary per user
    """

    def __init__(self, db_path="memory.db"):
        self.db_path = db_path
        raise NotImplementedError

    def log_interaction(self, user_id, item_id, clicked, dwell_time):
        raise NotImplementedError

    def get_history(self, user_id):
        raise NotImplementedError

    def update_summary(self, user_id, summary):
        raise NotImplementedError

    def get_summary(self, user_id):
        raise NotImplementedError
