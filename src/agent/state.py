# src/agent/state.py

class ConversationState:
    """
    Store information needed across multiple turns
    of the movie assistant conversation.
    """

    def __init__(self):
        self.current_movie = None
        self.current_query = None
        self.last_answer = None
        self.last_retrieved_sources = []
        self.pending_clarification = None

    def set_request(self, movie, query):
        """
        Store the movie and query from the current request.
        """
        self.current_movie = movie
        self.current_query = query

    def set_answer(self, answer):
        """
        Store the most recent generated answer.
        """
        self.last_answer = answer

    def set_sources(self, sources):
        """
        Store the evidence used to generate the answer.
        """
        self.last_retrieved_sources = sources

    def set_clarification(self, question):
        """
        Store a clarification question that is waiting
        for a user response.
        """
        self.pending_clarification = question

    def clear_clarification(self):
        """
        Clear the pending clarification after the user
        provides the required information.
        """
        self.pending_clarification = None

    def clear(self):
        """
        Reset the entire conversation state.
        """
        self.current_movie = None
        self.current_query = None
        self.last_answer = None
        self.last_retrieved_sources = []
        self.pending_clarification = None

    def get_state(self):
        """
        Return the current conversation state as a dictionary.
        """
        return {
            "current_movie": self.current_movie,
            "current_query": self.current_query,
            "last_answer": self.last_answer,
            "last_retrieved_sources": self.last_retrieved_sources,
            "pending_clarification": self.pending_clarification,
        }