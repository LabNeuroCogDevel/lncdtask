#!/usr/bin/env python3
from lncdtask.dollarreward import DollarReward, ttl, ttl_wrap
from lncdtask.externalcom import ParallelPortEEG
from psychopy import visual
import pytest
from unittest import mock

def test_ttl():
    # rew
    v = ttl(1, 'dot', 'rew', -.97)
    assert v == 200 + 40 + 1

    # neu
    v = ttl(1, 'ring', 'neu', -.97)
    assert v == 100 + 20 + 1
    v = ttl(1, 'cue', 'neu', -.97)
    assert v == 100 + 30 + 1
    v = ttl(1, 'dot', 'neu', -.97)
    assert v == 100 + 40 + 1

    ## iti
    v = ttl(1, 'iti', None, None)
    assert v == 10

    v = ttl(1, 'iti', 'iti', None)
    assert v == 10



@pytest.fixture
def mock_window():
    m = mock.MagicMock()
    #m.size = (800,600)
    m.callOnFlip = lambda func, *args, **kargs: func(*args, **kargs)
    return m

@pytest.fixture
def dr_with_mocks(mock_window):
    # TODO: find actual location of wait_until and replace_image. want to patch that so we can use onset=
    #mock.patch("lncdtask.screen.wait_until"),
    #mock.patch("lncdtask.dollarreward.wait_until"),
    with mock.patch("lncdtask.dollarreward.visual.TextStim"), \
         mock.patch("lncdtask.dollarreward.visual.ImageStim"), \
         mock.patch("lncdtask.dollarreward.visual.Circle"), \
         mock.patch("lncdtask.dollarreward.visual.BufferImageStim"), \
         mock.patch("lncdtask.dollarreward.visual.ElementArrayStim"), \
         mock.patch("lncdtask.dollarreward.wait_until"), \
         mock.patch("dollarreward.replace_img"):
        dr = DollarReward(win=mock_window)
        dr.img.win.size=(800,600) # TODO: remove when replace_image is mocked
        dr.trialnum = 1  # example trial
        return dr

def test_external_ET_messages(dr_with_mocks):
    eyelink = mock.MagicMock()
    eyelink.eyelink = mock.MagicMock()
    eyelink.event = mock.MagicMock()
    dr_with_mocks.eyelink = eyelink
    dr_with_mocks.externals = mock.MagicMock()

    # start 5s: first trial (set above) iti
    flip_time = dr_with_mocks.iti(onset=0)
    dr_with_mocks.externals.event.assert_called_with("1 iti")

    # jump to  ring. should increment trialnum
    flip_time2 = dr_with_mocks.ring(0,'neu',-0.97)
    assert dr_with_mocks.trialnum == 2
    dr_with_mocks.externals.event.assert_called_with("2 ring neu -0.97")
    dr_with_mocks.eyelink.eyelink.trial_start.assert_called_with(2)


def first_param_called(call_args_list):
    "Return first argument in repeated Mock call list"
    return [x[0][0] for x in call_args_list]

def test_external_EEG_marks(dr_with_mocks):
    dr_with_mocks.eyelink = None # disable eyelink
    with mock.patch("psychopy.parallel.ParallelPort"):
        lpt = ParallelPortEEG(99, lookup_func=ttl_wrap)
        lpt.port.setData = mock.MagicMock()
        #lpt.zeroTTL = False
    dr_with_mocks.externals.append(lpt)

    # iti start
    flip_time = dr_with_mocks.iti(onset=0)
    call_list = first_param_called(lpt.port.setData.call_args_list)
    assert call_list == [10, 0]

    # ring, prep, dot
    flip_time2 = dr_with_mocks.ring(0,'neu',-0.97)
    assert dr_with_mocks.trialnum == 2
    call_list = first_param_called(lpt.port.setData.call_args_list)[-2:]
    assert call_list == [ttl(2, 'ring', 'neu', -0.97) , 0] # 141

    flip_time = dr_with_mocks.prep(0,'neu',-0.97)
    call_list = first_param_called(lpt.port.setData.call_args_list)[-2:]
    assert call_list == [ttl(2, 'cue', 'neu', -0.97), 0]

    flip_time = dr_with_mocks.dot(0,'neu',-0.97)
    call_list = first_param_called(lpt.port.setData.call_args_list)[-2:]
    assert call_list == [ttl(2, 'dot', 'neu', -0.97), 0]
