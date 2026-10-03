from __future__ import annotations

import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
CONTROLLER_TEMPLATE = (
    ROOT_DIR
    / "mod_builder/templates/common/scripted_effects/bca_resource_planet_controller.txt.j2"
)
DESIGNATION_TRIGGERS = (
    ROOT_DIR / "common/scripted_triggers/bca_colony_designation_triggers.txt"
)
SCRIPTED_LOC = ROOT_DIR / "common/scripted_loc/bca_scripted_loc.txt"
GUI_LOCALISATIONS = [
    ROOT_DIR / f"localisation/{language}/bca_gui_l_{language}.yml"
    for language in ("english", "simp_chinese", "japanese", "russian")
]


class NomadFortressDistrictPlanningTests(unittest.TestCase):
    def test_arkship_fortresses_are_eligible_for_auto_district_management(self):
        triggers = DESIGNATION_TRIGGERS.read_text(encoding="utf-8")
        auto_district_manage = triggers.split(
            "bca_has_auto_district_manage = {", 1
        )[1].split("bca_auto_district_manage_enabled = {", 1)[0]

        self.assertIn("has_designation = col_nomad_fortress", auto_district_manage)

    def test_arkship_fortresses_plan_d3_to_its_build_limit(self):
        template = CONTROLLER_TEMPLATE.read_text(encoding="utf-8")
        fortress_plan = template.split(
            "# Nomad Arkship fortress designations devote every available district to d3.",
            1,
        )[1].split("{% for i in range(3) %}", 1)[0]

        self.assertIn("has_designation = col_nomad_fortress", fortress_plan)
        self.assertIn("bca_auto_district_manage_enabled = yes", fortress_plan)
        self.assertIn(
            "which = {{ v.var_district_num_plan('z3') }}\n            value = 0",
            fortress_plan,
        )
        self.assertIn(
            "which = {{ v.var_district_num_plan('z4') }}\n            value = 0",
            fortress_plan,
        )
        self.assertIn(
            "which = {{ v.var_district_num_plan('z5') }}"
            "\n            value = value:bca_district_max_build_d3",
            fortress_plan,
        )
        self.assertNotIn("value = value:bca_potential_max_districts", fortress_plan)

    def test_arkship_fortress_plan_is_skipped_when_demolition_is_disabled(self):
        template = CONTROLLER_TEMPLATE.read_text(encoding="utf-8")
        generic_plan = template.split(
            "bca_resource_planet_controller_district_only = {", 1
        )[1].split(
            "# Nomad Arkship fortress designations devote every available district to d3.",
            1,
        )[0]
        fortress_plan = template.split(
            "# Nomad Arkship fortress designations devote every available district to d3.",
            1,
        )[1].split("{% for i in range(3) %}", 1)[0]

        self.assertIn(
            "NOT = { has_carrier_flag = bca_pf_disable_planet_auto_destruction_district }",
            fortress_plan,
        )
        self.assertIn(
            "has_carrier_flag = bca_pf_disable_planet_auto_destruction_district",
            generic_plan,
        )
        self.assertIn("has_designation = col_nomad_fortress", generic_plan)
        self.assertNotIn("bca_clamp_district_plan_to_current_layout = yes", fortress_plan)

    def test_arkship_fortress_auto_district_management_uses_a_defense_icon(self):
        scripted_loc = SCRIPTED_LOC.read_text(encoding="utf-8")

        self.assertIn("has_designation = col_nomad_fortress", scripted_loc)
        icon_key = "bca_planet_setting_auto_district_management_fortress"
        self.assertIn(f'localization_key = "{icon_key}"', scripted_loc)
        for path in GUI_LOCALISATIONS:
            with self.subTest(path=path):
                localisation = path.read_text(encoding="utf-8-sig")
                self.assertIn(f'{icon_key}: "£defense_army£"', localisation)

    def test_japanese_auto_district_management_uses_standard_icon_tokens(self):
        japanese_localisation = GUI_LOCALISATIONS[2].read_text(encoding="utf-8-sig")

        expected_icons = {
            "mining": "minerals",
            "farming": "food",
            "generator": "energy",
        }
        for designation, icon in expected_icons.items():
            with self.subTest(designation=designation):
                self.assertIn(
                    "bca_planet_setting_auto_district_management_"
                    f'{designation}: "£{icon}£"',
                    japanese_localisation,
                )
