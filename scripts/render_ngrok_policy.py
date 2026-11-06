#!/usr/bin/env python3
"""Render the ignored local policy without logging or executing secret values."""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import tempfile

DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / 'ngrok-preprod-policy.yml'


def load_key(env_file=None):
    if env_file is None:
        value = os.environ.get('BETA_GATE_KEY', '')
    else:
        values = []
        for line in Path(env_file).read_text().splitlines():
            match = re.match(r'^\s*(?:export\s+)?BETA_GATE_KEY\s*=(.*)$', line)
            if match:
                try:
                    parts = shlex.split(match[1], comments=True)
                except ValueError:
                    raise ValueError('Invalid BETA_GATE_KEY assignment') from None
                if len(parts) != 1:
                    raise ValueError('Invalid BETA_GATE_KEY assignment')
                values.append(parts[0])
        if len(values) != 1:
            raise ValueError('Expected exactly one BETA_GATE_KEY assignment')
        value = values[0]
    if not re.fullmatch(r'[A-Za-z0-9_-]{32,128}', value):
        raise ValueError('BETA_GATE_KEY must contain 32–128 letters, digits, underscores or hyphens')
    return value


def render(key, output):
    # JSON is valid YAML. JSON encoding also safely quotes the CEL string literal.
    policy = {'on_http_request': [{
        'expressions': [f"getReqHeader('X-Beta-Key') != [{json.dumps(key)}]"],
        'actions': [{'type': 'deny', 'config': {'status_code': 401}}],
    }]}
    output = Path(output)
    if output.is_symlink():
        raise ValueError('Refusing to replace a symlink')
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=output.parent, delete=False) as stream:
            temporary = Path(stream.name)
            os.fchmod(stream.fileno(), 0o600)
            json.dump(policy, stream, indent=2)
            stream.write('\n')
        os.replace(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path, help='Read only BETA_GATE_KEY; never execute the file')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        render(load_key(args.env_file), args.output)
    except (ValueError, OSError):
        parser.exit(1, 'Policy generation failed: check the key, input file and output permissions.\n')
    print('Local policy generated. Restart ngrok to apply it.')


if __name__ == '__main__':
    main()
