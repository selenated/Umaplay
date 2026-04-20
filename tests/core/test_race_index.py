from core.utils.race_index import RaceIndex


def test_ambiguity_group_asahi_hanshin():
    group_asahi = RaceIndex.ambiguity_group("Asahi Hai Futurity Stakes")
    group_hanshin = RaceIndex.ambiguity_group("Hanshin Juvenile Fillies")

    canon_asahi = RaceIndex.canonicalize("Asahi Hai Futurity Stakes")
    canon_hanshin = RaceIndex.canonicalize("Hanshin Juvenile Fillies")

    assert canon_asahi in group_asahi
    assert canon_hanshin in group_asahi
    assert group_asahi[0] == canon_asahi
    assert group_hanshin == group_asahi


def test_banner_templates_for_group_asahi_hanshin():
    templates = RaceIndex.banner_templates_for_group("Asahi Hai Futurity Stakes")
    names = {tmpl["name"] for tmpl in templates}

    assert "Asahi Hai Futurity Stakes" in names
    assert "Hanshin Juvenile Fillies" in names


def test_ambiguity_group_falls_back_to_self_when_not_configured():
    name = "Junior Make Debut"
    group = RaceIndex.ambiguity_group(name)
    canon = RaceIndex.canonicalize(name)

    assert group == [canon]


def test_banner_templates_for_group_single_member_when_not_configured():
    name = "Junior Make Debut"
    templates = RaceIndex.banner_templates_for_group(name)
    names = {tmpl["name"] for tmpl in templates}

    assert name in names
