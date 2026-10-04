# src/agent/state.py

class ConversationState:
    def __init__(self):
        self.current_movie = None
        self.current_query = None
        self.last_answer = None
        self.last_retrieved_sources = []
        self.pending_clarification = None
        self.pending_action = None

    def set_request(self, movie, query):
        self.current_movie = movie
        self.current_query = query

    def set_answer(self, answer):
        self.last_answer = answer

    def set_sources(self, sources):
        self.last_retrieved_sources = sources

    def set_clarification(self, question):
        self.pending_clarification = question

    def clear_clarification(self):
        self.pending_clarification = None

    def set_pending_action(self, action):
        self.pending_action = action

    def clear_pending_action(self):
        self.pending_action = None

    def clear(self):
        self.current_movie = None
        self.current_query = None
        self.last_answer = None
        self.last_retrieved_sources = []
        self.pending_clarification = None
        self.pending_action = None

    def get_state(self):
        return {
            "current_movie": self.current_movie,
            "current_query": self.current_query,
            "last_answer": self.last_answer,
            "last_retrieved_sources": self.last_retrieved_sources,
            "pending_clarification": self.pending_clarification,
            "pending_action": self.pending_action,
        }