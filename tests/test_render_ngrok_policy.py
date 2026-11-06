import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/render_ngrok_policy.py'
spec = importlib.util.spec_from_file_location('policy', SCRIPT)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class PolicyTest(unittest.TestCase):
    def test_missing_and_invalid_keys_are_rejected(self):
        for key in ['', 'short', 'x' * 129, 'x' * 32 + "'", '$(touch injected)']:
            with self.subTest(key_length=len(key)), patch.dict(os.environ, {'BETA_GATE_KEY': key}):
                with self.assertRaises(ValueError):
                    policy.load_key()

    def test_env_file_parsing_does_not_execute_shell(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / '.env'
            path.write_text('UNRELATED=$(exit 1)\nexport BETA_GATE_KEY="' + 'a' * 64 + '" # comment\n')
            self.assertEqual(policy.load_key(path), 'a' * 64)
            for content in ['', 'BETA_GATE_KEY=a\nBETA_GATE_KEY=b', 'BETA_GATE_KEY="unterminated']:
                path.write_text(content)
                with self.assertRaises(ValueError):
                    policy.load_key(path)

    def test_policy_requires_exactly_one_matching_header_and_is_private(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'policy.yml'
            output.write_text('old')
            output.chmod(0o644)
            policy.render('b' * 64, output)
            rule = json.loads(output.read_text())['on_http_request'][0]
            self.assertEqual(rule['expressions'], ["getReqHeader('X-Beta-Key') != [" + json.dumps('b' * 64) + ']'])
            self.assertEqual(rule['actions'], [{'type': 'deny', 'config': {'status_code': 401}}])
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            self.assertEqual(len(list(Path(folder).iterdir())), 1)

    def test_invalid_cli_input_preserves_policy_and_does_not_log_key(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'policy.yml'
            output.write_text('unchanged')
            invalid = 'do-not-log-this-key!'
            result = subprocess.run(
                [sys.executable, '-B', str(SCRIPT), '--output', str(output)],
                env={**os.environ, 'BETA_GATE_KEY': invalid},
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_text(), 'unchanged')
            self.assertNotIn(invalid, result.stdout + result.stderr)

    def test_symlink_is_rejected_without_changing_target(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'target'
            target.write_text('unchanged')
            output = Path(folder) / 'policy.yml'
            output.symlink_to(target)
            with self.assertRaises(ValueError):
                policy.render('c' * 64, output)
            self.assertEqual(target.read_text(), 'unchanged')


if __name__ == '__main__':
    unittest.main()
