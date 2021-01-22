import json
import unittest
from rules_support.core_branch_info import CoreBranchInfo
from tests.utils import TestRepo


class TestCoreBranchInfo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_repo = TestRepo(prefix=cls.__name__)
        cls.test_repo.create_core_release_branch('1.2.3')
        cls.test_repo.create_feature_branch('XYZ_unittest_feature')

    def test_release_branch_name(self):
        self.test_repo.checkout_branch('release/1.2.3')
        test_obj = CoreBranchInfo(self.test_repo.directory)
        self.assertEqual(test_obj.version, '1.2.3')
        self.test_repo.checkout_branch('feature/XYZ_unittest_feature')
        test_obj = CoreBranchInfo(self.test_repo.directory)
        self.assertEqual(test_obj.version, 'XYZ_unittest_feature')

    def test_to_json(self):
        self.test_repo.checkout_branch('release/1.2.3')
        test_obj = CoreBranchInfo(self.test_repo.directory)
        json_str = test_obj.to_json()
        expect_dict = {"_folder": test_obj.folder, "_version": "1.2.3"}
        print(f'Saved core: f{json_str}')
        test_dict = json.loads(json_str)
        self.assertDictEqual(test_dict, expect_dict)

    def test_from_json(self):
        self.test_repo.checkout_branch('feature/XYZ_unittest_feature')
        test_cbinfo = CoreBranchInfo.from_json(
            json.dumps({'_folder': self.test_repo.directory}))
        self.assertEqual('XYZ_unittest_feature', test_cbinfo.version)
        self.assertEqual(self.test_repo.directory, test_cbinfo.folder)
        self.assertEqual('feature/XYZ_unittest_feature',
                         test_cbinfo.branch_name)

        self.test_repo.checkout_branch('release/1.2.3')
        test_cbinfo = CoreBranchInfo.from_json(
            json.dumps({'_folder': self.test_repo.directory}))
        self.assertEqual('1.2.3', test_cbinfo.version)
        self.assertEqual(self.test_repo.directory, test_cbinfo.folder)
        self.assertEqual('release/1.2.3', test_cbinfo.branch_name)

        self.test_repo.checkout_branch('master')
        test_cbinfo = CoreBranchInfo.from_json(
            json.dumps({'_folder': self.test_repo.directory}))
        self.assertEqual('latest', test_cbinfo.version)
        self.assertEqual(self.test_repo.directory, test_cbinfo.folder)
        self.assertEqual('master', test_cbinfo.branch_name)

    @classmethod
    def tearDownClass(cls):
        del cls.test_repo
