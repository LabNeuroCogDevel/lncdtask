from lncdtask.dollarreward import DollarReward, ttl
from psychopy import visual


def test_ttl():
    v = ttl(1, 'dot', 'rew', 7)
    assert v == 200 + 40 + 1

    v = ttl(1, 'iti', None, None)
    assert v == 15

    v = ttl(1, 'iti', 'iti', None)
    assert v == 15
