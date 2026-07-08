import random

from humansim.config import MouseSettings
from humansim.humanize.mouse import plan_move, random_point, screen_rect


def test_lands_exactly_on_target():
    cfg = MouseSettings()
    plan = plan_move((0, 0), (500, 300), cfg, random.Random(1))
    assert plan[-1][0] == 500
    assert plan[-1][1] == 300


def test_delays_non_negative_and_bounded_count():
    cfg = MouseSettings()
    plan = plan_move((0, 0), (800, 600), cfg, random.Random(2))
    assert all(dt >= 0 for _, _, dt in plan)
    assert 8 <= len(plan) <= 200


def test_curved_not_straight_line():
    # A curved path should deviate from the straight segment somewhere.
    cfg = MouseSettings(tremor_px=0.0, overshoot_chance=0.0)
    plan = plan_move((0, 0), (1000, 0), cfg, random.Random(3))
    max_dev = max(abs(y) for _, y, _ in plan[:-1])
    assert max_dev > 1  # bows away from the y=0 straight line


def test_tiny_move_is_single_step():
    plan = plan_move((10, 10), (11, 11), MouseSettings(), random.Random(0))
    assert plan[-1][:2] == (11, 11)


def test_helpers():
    rect = screen_rect((1920, 1080), margin=0.1)
    x, y = random_point(rect, random.Random(0))
    assert rect[0] <= x <= rect[2]
    assert rect[1] <= y <= rect[3]
