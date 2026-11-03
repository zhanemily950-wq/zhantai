import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / 'scripts' / 'validate_brief.py'
spec = importlib.util.spec_from_file_location('validate_brief', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestBriefValidation(unittest.TestCase):
    def test_valid_dimensions_yield_area(self):
        doc = {'project_name': '测试', 'event_name': '测试展', 'venue': '展馆',
               'industry': '宠物', 'booth': {'width_m': 6, 'depth_m': 6,
               'open_sides': ['北', '东'], 'official_height_limit_m': None,
               'venue_manual_verified': False}, 'brand': {'name': '测试品牌'},
               'budget': {'ceiling_cny': 60000}, 'objectives': ['招商'], 'exhibits': [{'name':'样品'}]}
        errors, warnings, info = module.check(doc)
        self.assertEqual(errors, [])
        self.assertTrue(any('36.00㎡' in s for s in info))
        self.assertTrue(any('展商手册' in s for s in warnings))

    def test_bad_dimensions_are_errors(self):
        errors, _, _ = module.check({'booth': {'width_m': -2, 'depth_m': 'six', 'open_sides': []}})
        self.assertEqual(len([x for x in errors if '正数' in x]), 2)

    def test_missing_dimensions_are_warnings(self):
        errors, warnings, _ = module.check({'booth': {'width_m': None, 'depth_m': None, 'open_sides': []}})
        self.assertEqual(errors, [])
        self.assertTrue(any('宽度未填写' in s for s in warnings))


if __name__ == '__main__':
    unittest.main()
