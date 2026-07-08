import random

from humansim.content import ContentGen
from humansim.content.markov import Markov


def test_markov_generates_sentence():
    m = Markov(order=2, rng=random.Random(0))
    m.train(
        "The quick brown fox jumps over the lazy dog. The dog sleeps all day. "
        "The fox runs fast now. A calm river flows past the old bridge."
    )
    assert m.ready()
    s = m.sentence()
    assert isinstance(s, str) and len(s) > 0
    assert s[0].isupper()


def test_contentgen_all_kinds_non_empty():
    gen = ContentGen(rng=random.Random(0))
    for kind in gen.kinds:
        note = gen.make_note(kind)
        assert isinstance(note, str)
        assert "\n" in note and len(note) > 20
