#!/usr/bin/env python3
import re
import time
from pathlib import Path
from srtranslator import SrtFile
from srtranslator.translators.translatepy import TranslatePy


def make_output_name(inp: Path) -> Path:
    """Удаляет .en, .en_US, .en-GB и добавляет .ru_RU.srt"""
    name = inp.name
    name = re.sub(r'\.en([-_][A-Z]{2})?\.srt$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\.srt$', '', name, flags=re.IGNORECASE)
    return inp.with_name(name + ".ru_RU.srt")


def is_russian_sub(name: str) -> bool:
    """Проверяет, что файл уже русский (ru, ru_RU, ru-RU)."""
    return re.search(r'\.ru([-_][A-Z]{2})?\.srt$', name, flags=re.IGNORECASE) is not None


def main():
    cwd = Path(".")
    files = sorted([p for p in cwd.iterdir() if p.is_file() and p.suffix.lower() == ".srt"],
                   key=lambda x: x.name.lower())

    if not files:
        print("ℹ️ В текущей папке нет .srt файлов.")
        return

    tr = TranslatePy()

    for f in files:
        if is_russian_sub(f.name):
            continue
        out = make_output_name(f)
        print(f"🔄 Перевод: {f.name} → {out.name}")
        try:
            s = SrtFile(f.as_posix())
            s.translate(tr, "en", "ru")
            s.save(out.as_posix())
            print(f"✅ Готово: {out.name}")
            time.sleep(0.3)
        except Exception as e:
            print(f"⚠️ Ошибка перевода {f.name}: {e}")

    print("🎬 Всё готово.")


if __name__ == "__main__":
    main()
