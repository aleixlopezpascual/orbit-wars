import analyze_replays_helper as ar


def _planet(pid, owner, x, y, ships, prod=3, radius=2.0):
    return [pid, owner, x, y, radius, ships, prod]


def _fleet(fid, owner, x, y, angle, frm, ships):
    return [fid, owner, x, y, angle, frm, ships]


def test_iter_board_states_extracts_planets_and_fleets():
    replay = {
        "steps": [
            [{"observation": {"planets": [_planet(0, 0, 10, 50, 20)], "fleets": []}}],
            [{"observation": {"planets": [_planet(0, 0, 10, 50, 18)],
                              "fleets": [_fleet(5, 0, 12, 50, 0.0, 0, 7)]}}],
        ]
    }
    states = ar.iter_board_states(replay)
    assert len(states) == 2
    assert states[1]["fleets"][0][0] == 5


def test_infer_fleet_target_picks_planet_along_heading():
    # Fleet launched from planet 0 at (10,50) heading angle 0 (east) toward planet 1 at (90,50)
    planets = [_planet(0, 0, 10, 50, 5), _planet(1, -1, 90, 50, 3),
               _planet(2, -1, 10, 90, 3)]
    fleet = _fleet(5, 0, 11, 50, 0.0, 0, 4)
    assert ar.infer_fleet_target(fleet, planets) == 1


def test_detect_launches_flags_new_fleets_only():
    s0 = {"planets": [_planet(0, 0, 10, 50, 20), _planet(1, -1, 90, 50, 3)],
          "fleets": []}
    s1 = {"planets": [_planet(0, 0, 10, 50, 16), _planet(1, -1, 90, 50, 3)],
          "fleets": [_fleet(5, 0, 12, 50, 0.0, 0, 4)]}
    s2 = {"planets": [_planet(0, 0, 10, 50, 16), _planet(1, -1, 90, 50, 3)],
          "fleets": [_fleet(5, 0, 30, 50, 0.0, 0, 4)]}  # same fleet moved, not new
    launches = ar.detect_launches([s0, s1, s2])
    assert len(launches) == 1
    assert launches[0]["turn"] == 1
    assert launches[0]["owner"] == 0
    assert launches[0]["from_planet_id"] == 0
    assert launches[0]["target_planet_id"] == 1


def test_count_focus_fire_events_needs_two_distinct_sources_same_target():
    # Two launches by owner 0 from planets 0 and 2, both targeting planet 1, within window.
    launches = [
        {"turn": 5, "owner": 0, "from_planet_id": 0, "target_planet_id": 1, "ships": 4},
        {"turn": 6, "owner": 0, "from_planet_id": 2, "target_planet_id": 1, "ships": 4},
        {"turn": 5, "owner": 1, "from_planet_id": 9, "target_planet_id": 7, "ships": 4},
    ]
    assert ar.count_focus_fire_events(launches, owner=0, window=2, min_sources=2) == 1
    assert ar.count_focus_fire_events(launches, owner=1, window=2, min_sources=2) == 0


def test_count_focus_fire_ignores_same_source_repeat():
    launches = [
        {"turn": 5, "owner": 0, "from_planet_id": 0, "target_planet_id": 1, "ships": 4},
        {"turn": 6, "owner": 0, "from_planet_id": 0, "target_planet_id": 1, "ships": 4},
    ]
    assert ar.count_focus_fire_events(launches, owner=0, window=2, min_sources=2) == 0


def test_find_seat_by_name():
    replay = {"info": {"TeamNames": ["Jeki", "Aleix López", "Dapp", "ysd"]}}
    assert ar.find_seat_by_name(replay, "Aleix López") == 1
    assert ar.find_seat_by_name(replay, "Nobody") is None


def _two_seat_replay():
    # Seat 1 (us) loses; seat 0 wins and uses a 2-source focus-fire strike on planet 2.
    def planet(pid, owner, x, y, ships):
        return [pid, owner, x, y, 2.0, ships, 3]

    def fleet(fid, owner, x, y, ang, frm, ships):
        return [fid, owner, x, y, ang, frm, ships]

    p_src0 = planet(0, 0, 10, 50, 30)   # our enemy's source A
    p_src1 = planet(1, 0, 50, 10, 30)   # enemy source B
    p_tgt = planet(2, -1, 50, 50, 5)    # contested neutral target
    p_us = planet(3, 1, 90, 90, 30)     # our planet
    steps = [
        [{"observation": {"planets": [p_src0, p_src1, p_tgt, p_us], "fleets": []}}],
        # turn 1: two enemy fleets launch from planets 0 and 1 toward planet 2
        [{"observation": {"planets": [p_src0, p_src1, p_tgt, p_us],
                          "fleets": [fleet(10, 0, 12, 50, 0.0, 0, 6),
                                     fleet(11, 0, 50, 12, 1.5708, 1, 6)]}}],
    ]
    return {
        "steps": steps,
        "rewards": [1, -1],
        "info": {"TeamNames": ["Enemy", "Aleix López"]},
    }


def test_episode_report_identifies_our_loss_and_ff_gap():
    rep = ar.episode_report(_two_seat_replay(), our_name="Aleix López")
    assert rep["our_seat"] == 1
    assert rep["our_won"] is False
    assert rep["our_focus_fire"] == 0
    assert rep["winner_seat"] == 0
    assert rep["winner_focus_fire"] == 1
