from hoplink import synth
from hoplink.linkbudget import assess_pathway, atak_summary, fspl_db, link_margin


def test_fspl_increases_with_distance_and_freq():
    assert fspl_db(1500, 2000) > fspl_db(1500, 200)
    assert fspl_db(3000, 1000) > fspl_db(300, 1000)


def test_link_margin_closes_and_fails():
    strong = link_margin(43, 3, 30, 1500, 500, -110)
    weak = link_margin(10, 0, 0, 1500, 20000, -90)
    assert strong["closes"] is True
    assert weak["closes"] is False
    assert strong["margin_db"] > weak["margin_db"]


def test_assess_and_atak_summary():
    plan = synth.sample_plan()
    geom = {"tx_dbm": 43, "tx_gain_dbi": 3, "rx_gain_dbi": 30,
            "freq_mhz": 1500, "dist_km": 2000, "rx_sens_dbm": -110}
    a = assess_pathway(plan[0], geom)
    assert "link_budget" in a and "atak_capable" in a
    s = atak_summary(plan)
    # the high-bandwidth SATCOM tiers carry ATAK PLI; the ultra-low-rate PLB does not
    assert "P" in s["capable_tiers"]
    assert s["all_tiers_capable"] is False
