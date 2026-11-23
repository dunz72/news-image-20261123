#!/usr/bin/env python3
"""Copy the finished front page to the harness output directory.

The entry image (entry.png) is stored in this repository, already drawn.
This program does nothing but copy it byte-for-byte to the output
directory the grader expects.

Standard library only: no third-party packages, no fonts, no network,
no clock, no randomness. The grader runs this in a bare sandbox with
no Pillow installed, so nothing here may import anything beyond the
standard library.
"""

import hashlib
import os
import sys

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
SOURCE_NAME = "entry.png"


def sha256_hex(data):
    """SHA-256 of bytes, as a hex string."""
    return hashlib.sha256(data).hexdigest()


def find_source():
    """Locate entry.png next to this script, or under MAKEFUN_BOT_DIR."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(here, SOURCE_NAME)
    if os.path.isfile(candidate):
        return candidate
    bot_dir = os.environ.get("MAKEFUN_BOT_DIR")
    if bot_dir:
        candidate = os.path.join(bot_dir, SOURCE_NAME)
        if os.path.isfile(candidate):
            return candidate
    raise FileNotFoundError(
        "%s not found next to %s" % (SOURCE_NAME, __file__)
        + (" or under MAKEFUN_BOT_DIR=%s" % bot_dir if bot_dir else "")
    )


def main():
    source_path = find_source()
    with open(source_path, "rb") as handle:
        data = handle.read()

    if data[: len(PNG_SIGNATURE)] != PNG_SIGNATURE:
        raise ValueError("%s: not a PNG file (bad signature)" % source_path)
    if len(data) > MAX_BYTES:
        raise ValueError(
            "%s: %d bytes exceeds limit %d"
            % (source_path, len(data), MAX_BYTES)
        )

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, SOURCE_NAME)
    with open(out_path, "wb") as handle:
        handle.write(data)

    # Verify the copy byte-for-byte before reporting success: a
    # truncated or corrupted write must fail loudly, not silently.
    with open(out_path, "rb") as handle:
        written = handle.read()
    if sha256_hex(written) != sha256_hex(data):
        raise ValueError("%s: written copy does not match source" % out_path)

    print(
        "wrote %s (%d bytes, sha256 %s)"
        % (out_path, len(data), sha256_hex(data)[:16])
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
