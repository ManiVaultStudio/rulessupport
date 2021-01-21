import unittest
from rules_support.plugin_branch_info import PluginBranchInfo
from tests.utils import TestRepo

class TestPluginBranchInfo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a test repo for the plugin with the following example branches
            1) master (or main)
            2) feature/XYZ_unittest_feature (core does not exist)
            3) feature/test_ci_cd (core does exist)
            3) feature/core_0.1/ABC_unittest_feature
            3) release/core_0.1/1.0

        core release/0.1 exists in the artifactory
        """
        cls.test_repo = TestRepo(prefix=cls.__name__)
        cls.test_repo.create_core_release_branch('1.2.3')
        cls.test_repo.create_feature_branch('XYZ_unittest_feature')
        cls.test_repo.create_feature_branch('test_ci_cd')
        cls.test_repo.create_plugin_feature_core_release_branch('ABC_unittest_feature', '0.1')
        cls.test_repo.create_plugin_release_branch('1.0', '0.1')

    def test_master_branch(self):
        self.test_repo.checkout_branch('master')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        self.assertEqual(test_obj.version, 'latest')
        self.assertEqual(test_obj.core_version, 'latest')

    def test_feature_branch_core_latest(self):
        self.test_repo.checkout_branch('feature/XYZ_unittest_feature')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        self.assertEqual(test_obj.version, 'XYZ_unittest_feature')
        self.assertEqual(test_obj.core_version, 'latest')

    def test_feature_branch_core_feature(self):
        self.test_repo.checkout_branch('feature/test_ci_cd')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        self.assertEqual(test_obj.version, 'test_ci_cd')
        self.assertEqual(test_obj.core_version, 'test_ci_cd')

    def test_feature_core_release(self):
        self.test_repo.checkout_branch('feature/core_0.1/ABC_unittest_feature')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        self.assertEqual(test_obj.version, 'ABC_unittest_feature')
        self.assertEqual(test_obj.core_version, '0.1')

    def test_release_branch(self):
        self.test_repo.checkout_branch('release/core_0.1/1.0')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        self.assertEqual(test_obj.version, '1.0')
        self.assertEqual(test_obj.core_version, '0.1')

    @classmethod
    def tearDownClass(cls):
        del cls.test_repo
