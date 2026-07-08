from humansim.safety.control import Control


def test_wait_completes_when_running():
    c = Control()
    assert c.wait(0.01) is True


def test_wait_returns_false_when_stopped():
    c = Control()
    c.stop()
    assert c.wait(0.5) is False


def test_stop_unblocks_pause():
    c = Control()
    c.pause()
    c.stop()  # stop must break out of a paused wait
    assert c.wait(0.5) is False


def test_injection_bookkeeping():
    c = Control()
    assert not c.injecting
    c.begin_injection()
    assert c.injecting
    c.end_injection()
    assert not c.injecting
    assert c.last_injection > 0
