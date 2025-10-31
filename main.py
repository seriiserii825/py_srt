import sys
import time
from pathlib import Path
from srtranslator import SrtFile
from srtranslator.translators.translatepy import TranslatePy


def ask_postfixes():
    print("Examples:")
    print("  _en.srt   ->  _ru.srt")
    print("  .en_US.srt -> _ru.srt")
    old_pf = input("Old postfix (exact ending, e.g. '_en.srt' or '.en_US.srt'): ").strip()
    new_pf = input("New postfix (e.g. '_ru.srt' or '.srt'): ").strip()

    if not old_pf or not new_pf:
        print("❌ Both postfixes are required.")
        sys.exit(1)
    if not old_pf.lower().endswith(".srt") or not new_pf.lower().endswith(".srt"):
        print("❌ Postfixes must end with '.srt'.")
        sys.exit(1)
    return old_pf, new_pf


def should_translate(file_name: str, old_pf_lower: str) -> bool:
    return file_name.lower().endswith(old_pf_lower)


def make_output_name(inp: Path, old_pf: str, new_pf: str) -> Path:
    """
    Replace the exact ending 'old_pf' with 'new_pf', case-insensitively.
    """
    name = inp.name
    lo_name = name.lower()
    lo_old  = old_pf.lower()
    if not lo_name.endswith(lo_old):
        return inp  # shouldn't happen if caller checked
    base = name[: len(name) - len(old_pf)]
    return inp.with_name(base + new_pf)


def main():
    # choose mapping
    old_pf, new_pf = ask_postfixes()
    old_pf_lower = old_pf.lower()

    cwd = Path(".")
    files = sorted([p for p in cwd.iterdir() if p.is_file() and p.suffix.lower() == ".srt"],
                   key=lambda x: x.name.lower())

    if not files:
        print("ℹ️ No .srt files found in current directory.")
        return

    tr = TranslatePy()

    any_done = False
    for f in files:
        if not should_translate(f.name, old_pf_lower):
            continue

        out = make_output_name(f, old_pf, new_pf)
        if out.exists():
            print(f"⏭️  Skip (already exists): {out.name}")
            continue

        print(f"🔄 Translating: {f.name} → {out.name}")
        try:
            s = SrtFile(f.as_posix())
            # Always EN -> RU
            s.translate(tr, "en", "ru")
            s.save(out.as_posix())
            print(f"✅ Done: {out.name}")
            any_done = True
            time.sleep(0.3)
        except Exception as e:
            print(f"⚠️ Error translating {f.name}: {e}")

    if any_done:
        print("🎬 All translations completed.")
    else:
        print("ℹ️ Nothing to do (no files matched the selected postfix).")


if __name__ == "__main__":
    main()
