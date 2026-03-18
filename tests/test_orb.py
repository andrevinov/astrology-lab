from astrolab.core.math.orb import get_orb  # type: ignore


def test_get_orb_known_aspects():
    assert get_orb("conjunction") == 8.0
    assert get_orb("opposition") == 8.0
    assert get_orb("trine") == 6.0
    assert get_orb("square") == 6.0
    assert get_orb("sextile") == 4.0


def test_get_orb_unknown_aspect():
    try:
        get_orb("quincunx")
    except ValueError as e:
        assert "Unknown aspect type" in str(e)
    else:
        assert False, "Expected ValueError for unknown aspect"