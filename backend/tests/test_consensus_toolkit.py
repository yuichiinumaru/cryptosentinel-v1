import pytest
from backend.tools.consensus import ConsensusToolkit

@pytest.fixture
def consensus_toolkit():
    return ConsensusToolkit()

def test_majority_vote_basic(consensus_toolkit):
    votes = ["BULLISH", "BULLISH", "BEARISH"]
    assert consensus_toolkit.majority_vote(votes) == "BULLISH"

def test_majority_vote_tie(consensus_toolkit):
    votes = ["BULLISH", "BEARISH", "BULLISH", "BEARISH"]
    # In case of a tie, the first one encountered wins.
    assert consensus_toolkit.majority_vote(votes) == "BULLISH"

def test_majority_vote_empty(consensus_toolkit):
    votes = []
    assert consensus_toolkit.majority_vote(votes) == "NO_CONSENSUS"

def test_majority_vote_neutral(consensus_toolkit):
    votes = ["NEUTRAL", "NEUTRAL", "BULLISH"]
    assert consensus_toolkit.majority_vote(votes) == "NEUTRAL"

def test_majority_vote_all_same(consensus_toolkit):
    votes = ["BEARISH", "BEARISH", "BEARISH"]
    assert consensus_toolkit.majority_vote(votes) == "BEARISH"
