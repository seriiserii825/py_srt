#!/usr/bin/env python3
import re
import time
from pathlib import Path
from srtranslator import SrtFile
from srtranslator.translators.translatepy import TranslatePy


def make_output_name(inp: Path) -> Path:
    """
    Example:
    204 Section Intro.en_US.srt → 204 Section Intro.srt
    lesson.en.srt → lesson.srt
    """
    # remove language suffix (.en, .en_US, .en-GB)
    name = re.sub(r"\.en([-_][A-Z]{2})?\.srt$", "", inp.name, flags=re.IGNORECASE)
    return inp.with_name(name + ".srt")


def should_translate(f: Path) -> bool:
    """Only translate files ending with .en*.srt (ignore already .srt or .ru.srt)"""
    return (
        re.search(r"\.en([-_][A-Z]{2})?\.srt$", f.name, flags=re.IGNORECASE) is not None
    )


def main():
    cwd = Path(".")
    files = sorted(
        [p for p in cwd.iterdir() if p.is_file() and p.suffix.lower() == ".srt"],
        key=lambda x: x.name.lower(),
    )

    if not files:
        print("ℹ️ No .srt files found in current directory.")
        return

    tr = TranslatePy()

    for f in files:
        if not should_translate(f):
            continue

        out = make_output_name(f)
        print(f"🔄 Translating: {f.name} → {out.name}")
        try:
            s = SrtFile(f.as_posix())
            s.translate(tr, "en", "ru")
            s.save(out.as_posix())
            print(f"✅ Done: {out.name}")
            time.sleep(0.3)
        except Exception as e:
            print(f"⚠️ Error translating {f.name}: {e}")

    print("🎬 All translations completed.")


if __name__ == "__main__":
    main()
