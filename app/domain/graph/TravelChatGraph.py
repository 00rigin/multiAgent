from app.domain.graph.setup import GraphSetup


class TravelChatGraph:
    def __init__(self):
        self.graph = GraphSetup()

    def start(self):
        """Start the travel chat graph."""
        # Initialize the graph setup
        return self.graph.setup_graph()