from __future__ import annotations

import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPT_VALUES = ROOT_DIR / "common/script_values/bca_sv.txt"
SCRIPTED_TRIGGERS = ROOT_DIR / "common/scripted_triggers/bt_st_tool.txt"
PANEL_EFFECTS = ROOT_DIR / "common/button_effects/bca_planet_setting_panel.txt"
STATIC_MODIFIERS = ROOT_DIR / "common/static_modifiers/static_modifiers_automation.txt"
CONFIRMATION_EVENT = ROOT_DIR / "events/bac_colony_transform_events.txt"
MONTHLY_EVENT_TEMPLATE = (
    ROOT_DIR / "mod_builder/templates/events/bac_gen_colony_transform_events.txt.j2"
)
DECISION_TEMPLATE = (
    ROOT_DIR / "mod_builder/templates/common/decisions/bca_arkship_upgrade.txt.j2"
)


class ArkshipUpgradeTests(unittest.TestCase):
    def test_cost_values_use_the_native_arkship_upgrade_modifier(self):
        values = SCRIPT_VALUES.read_text(encoding="utf-8-sig")
        cost_block = values.split("bca_arkship_upgrade_cost_mult = {", 1)[1].split(
            "bca_free_jobs_main = {", 1
        )[0]

        self.assertIn("modifier:starbase_arkship_upgrades_cost_mult", cost_block)
        self.assertIn("bca_arkship_upgrade_alloys_cost", cost_block)
        self.assertIn("base = 5000", cost_block)
        self.assertIn("bca_arkship_upgrade_influence_cost", cost_block)
        self.assertIn("base = 250", cost_block)
        self.assertIn("bca_arkship_upgrade_required_alloys", cost_block)
        self.assertIn("bca_arkship_upgrade_required_influence", cost_block)
        self.assertIn("add = bca_reserve_alloys_amount", cost_block)
        self.assertIn("add = bca_reserve_influence_amount", cost_block)
        self.assertNotIn("starbase_upgrade_cost_mult", cost_block)

    def test_arkship_eligibility_is_only_tier_and_technology_based(self):
        triggers = SCRIPTED_TRIGGERS.read_text(encoding="utf-8-sig")
        tier_2 = triggers.split("bca_can_upgrade_arkship_to_tier_2 = {", 1)[1].split(
            "bca_can_upgrade_arkship_to_tier_3 = {", 1
        )[0]
        tier_3 = triggers.split("bca_can_upgrade_arkship_to_tier_3 = {", 1)[1].split(
            "bca_has_resource_for_arkship_upgrade = {", 1
        )[0]

        self.assertIn("has_technology = tech_arkship_tier_2", tier_2)
        self.assertIn("has_technology = tech_arkship_tier_3", tier_3)
        for arkship_type in ("civilian", "science", "military"):
            self.assertIn(f"is_ship_size = {arkship_type}_arkship_tier_1", tier_2)
            self.assertIn(f"is_ship_size = {arkship_type}_arkship_tier_2", tier_3)
        self.assertNotIn("can_be_upgraded", tier_2)
        self.assertNotIn("can_be_upgraded", tier_3)
        self.assertNotIn("carrier = {", tier_2)
        self.assertNotIn("carrier = {", tier_3)

    def test_resource_reserve_check_uses_the_discounted_costs(self):
        triggers = SCRIPTED_TRIGGERS.read_text(encoding="utf-8-sig")
        resource_check = triggers.split(
            "bca_has_resource_for_arkship_upgrade = {", 1
        )[1].split("bca_has_build_plan = {", 1)[0]

        self.assertIn("resource = alloys", resource_check)
        self.assertIn("value:bca_arkship_upgrade_required_alloys", resource_check)
        self.assertIn("resource = influence", resource_check)
        self.assertIn("value:bca_arkship_upgrade_required_influence", resource_check)
        self.assertNotIn("bca_value_add", resource_check)

    def test_decisions_queue_the_native_tier_mappings_with_discounted_costs(self):
        template = DECISION_TEMPLATE.read_text(encoding="utf-8-sig")

        tier_2 = template.split("bca_arkship_upgrade_tier_2 = {", 1)[1].split(
            "bca_arkship_upgrade_tier_3 = {", 1
        )[0]
        tier_3 = template.split("bca_arkship_upgrade_tier_3 = {", 1)[1]

        self.assertIn("enactment_time = 900", tier_2)
        self.assertIn("enactment_time = 1080", tier_3)
        for decision in (tier_2, tier_3):
            self.assertIn("icon = decision_reactor", decision)
            self.assertIn("alloys = 5000", decision)
            self.assertIn("influence = 250", decision)
            self.assertIn("mult = owner.value:bca_arkship_upgrade_cost_mult", decision)
            self.assertIn("bca_has_resource_for_arkship_upgrade = yes", decision)
            self.assertIn("fleet = {", decision)
            self.assertNotIn("carrier = {", decision)
        for arkship_type in ("civilian", "science", "military"):
            self.assertIn(
                f"set_starbase_size = {arkship_type}_arkship_tier_2", tier_2
            )
            self.assertIn(
                f"set_starbase_size = {arkship_type}_arkship_tier_3", tier_3
            )

    def test_world_transform_candidate_flow_keeps_arcology_and_arkship_separate(self):
        panel = PANEL_EFFECTS.read_text(encoding="utf-8-sig")
        modifiers = STATIC_MODIFIERS.read_text(encoding="utf-8-sig")
        monthly_event = MONTHLY_EVENT_TEMPLATE.read_text(encoding="utf-8-sig")
        confirmation_event = CONFIRMATION_EVENT.read_text(encoding="utf-8-sig")

        self.assertIn("bca_pm_arkship_upgrade_candidate = {", modifiers)
        self.assertIn("bca_planet_setting_world_transform_candidate = {", panel)
        self.assertIn("bca_can_be_arcology_project_candidate = yes", panel)
        self.assertIn("bca_can_upgrade_arkship_to_tier_2 = yes", panel)
        self.assertIn("bca_can_upgrade_arkship_to_tier_3 = yes", panel)
        self.assertIn("add_modifier = { modifier = \"bca_pm_arkship_upgrade_candidate\"", panel)

        self.assertIn("bca_world_transform_candidate_planet_count", monthly_event)
        self.assertIn("has_modifier = bca_pm_arcology_project_candidate", monthly_event)
        self.assertIn("has_modifier = bca_pm_arkship_upgrade_candidate", monthly_event)
        self.assertIn("bca_has_resource_for_arkship_upgrade = yes", monthly_event)

        self.assertIn("select_decision = { name = bca_arkship_upgrade_tier_2 }", confirmation_event)
        self.assertIn("select_decision = { name = bca_arkship_upgrade_tier_3 }", confirmation_event)
        self.assertIn("remove_modifier = bca_pm_arkship_upgrade_candidate", confirmation_event)
        self.assertIn("bca_secondary_zone_setting_set_by_current_zones = yes", confirmation_event)

    def test_all_localisations_warn_about_concurrent_native_arkship_upgrades(self):
        for language in ("english", "simp_chinese", "japanese", "russian"):
            with self.subTest(language=language):
                gui = (
                    ROOT_DIR / f"localisation/{language}/bca_gui_l_{language}.yml"
                ).read_text(encoding="utf-8-sig")
                main = (
                    ROOT_DIR / f"localisation/{language}/bt_main_3_l_{language}.yml"
                ).read_text(encoding="utf-8-sig")
                event_template = (
                    ROOT_DIR
                    / "mod_builder/templates/localisation"
                    / language
                    / f"bac_colony_transform_events_l_{language}.yml.j2"
                ).read_text(encoding="utf-8-sig")

                self.assertIn("BCA_PLANET_SETTING_ARKSHIP_UPGRADE_CANDIDATE", gui)
                self.assertIn("BCA_PLANET_SETTING_WORLD_TRANSFORM_CANDIDATE", gui)
                self.assertIn("bca_pm_arkship_upgrade_candidate", main)
                self.assertIn("bca_arkship_upgrade_tier_2", main)
                self.assertIn("bca_no_enough_resources_for_arkship_upgrade", event_template)


if __name__ == "__main__":
    unittest.main()
