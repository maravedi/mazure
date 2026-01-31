import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path
from mazure.sync.spec_sync import AzureSpecSyncEngine, SpecChangeType

class TestAzureSpecSyncEngine(unittest.IsolatedAsyncioTestCase):
    async def test_sync_no_repo(self):
        """Test sync when repo doesn't exist (should clone)"""
        with patch('mazure.sync.spec_sync.git.Repo') as mock_repo_cls:
            mock_repo = MagicMock()
            mock_repo_cls.clone_from.return_value = mock_repo

            # Setup commits to be same (no changes)
            commit = MagicMock()
            mock_repo.head.commit = commit
            mock_repo.remotes.origin.pull.return_value = None

            engine = AzureSpecSyncEngine(
                specs_repo_path=Path("dummy/specs"),
                mazure_root=Path("dummy/mazure")
            )

            # Verify path exists check
            with patch('pathlib.Path.exists', return_value=False):
                changes = await engine.sync()

            mock_repo_cls.clone_from.assert_called_once()
            assert changes == []

    async def test_sync_with_changes(self):
        with patch('mazure.sync.spec_sync.git.Repo') as mock_repo_cls:
            mock_repo = MagicMock()
            mock_repo_cls.return_value = mock_repo

            # Setup diff
            old_commit = MagicMock()
            new_commit = MagicMock()
            old_commit.hexsha = "old"
            new_commit.hexsha = "new"

            mock_repo.head.commit = old_commit

            def pull_side_effect(*args):
                mock_repo.head.commit = new_commit

            mock_repo.remotes.origin.pull.side_effect = pull_side_effect

            # Setup diff item
            diff_item = MagicMock()
            diff_item.new_file = False
            diff_item.deleted_file = False
            diff_item.b_path = "specification/compute/stable/2021-03-01/compute.json"
            diff_item.diff = b"some diff"

            old_commit.diff.return_value = [diff_item]

            engine = AzureSpecSyncEngine(
                specs_repo_path=Path("dummy/specs"),
                mazure_root=Path("dummy/mazure")
            )

            with patch('pathlib.Path.exists', return_value=True), \
                 patch('builtins.open', new_callable=MagicMock) as mock_open, \
                 patch('json.dump') as mock_json_dump, \
                 patch('json.load', return_value=[]):

                changes = await engine.sync()

            self.assertEqual(len(changes), 1)
            self.assertEqual(changes[0].change_type, SpecChangeType.MODIFIED)
            self.assertEqual(changes[0].provider, "compute")
            self.assertEqual(changes[0].resource_type, "compute")
            self.assertEqual(changes[0].api_version, "2021-03-01")
