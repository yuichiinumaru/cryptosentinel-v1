from collections import Counter
from typing import List
from agno.tools.toolkit import Toolkit

class ConsensusToolkit(Toolkit):
    """A toolkit for achieving consensus from multiple agent outputs."""

    def __init__(self):
        super().__init__(
            name="consensus_toolkit",
            tools=[self.majority_vote]
        )

    def majority_vote(self, votes: List[str]) -> str:
        """
        Determines the most frequent vote from a list of votes.

        Args:
            votes: A list of strings representing votes.

        Returns:
            The most frequent vote. In case of a tie, the first one encountered wins.
            Returns "NO_CONSENSUS" if the list of votes is empty.
        """
        if not votes:
            return "NO_CONSENSUS"

        vote_counts = Counter(votes)
        # most_common(1) returns a list of (element, count) tuples
        most_common_vote = vote_counts.most_common(1)[0][0]
        return most_common_vote
