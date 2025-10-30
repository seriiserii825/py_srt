# main.py
import sys
import subprocess
import time
import re
from pathlib import Path

REQS = ["srtranslator", "translatepy"]


def ensure_deps():
    """Проверяет и устанавливает зависимости в ~/.local, если их нет."""
    missing = []
    for pkg in REQS:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if not missing:
        return

    print(f"🔧 Устанавливаю зависимости: {' '.join(missing)}")
    # Пытаемся установить в пользовательский каталог
    try:
        cmd = [sys.executable, "-m", "pip", "install", "--user", *missing]
        subprocess.check_call(cmd)
        # после установки пробуем импортировать ещё раз
        for pkg in missing:
            __import__(pkg)
    except Exception as e:
        print("❌ Не удалось установить зависимости через pip.")
        print("   Убедитесь, что установлен python-pip (Arch): sudo pacman -S python-pip")
        print(f"   Детали: {e}")
        sys.exit(1)


def make_output_name(inp: Path) -> Path:
    """
    Удаляет хвосты .en, .en_US, .en-GB и т.п. перед .srt
    и возвращает имя с суффиксом .ru_RU.srt
    """
    name = inp.name
    # срежем ".en", ".en_US", ".en-GB" перед ".srt"
    name = re.sub(r'\.en([-_][A-Z]{2})?\.srt$', '', name, flags=re.IGNORECASE)
    # уберём ".srt" на всякий случай
    name = re.sub(r'\.srt$', '', name, flags=re.IGNORECASE)
    return inp.with_name(name + ".ru_RU.srt")


def is_russian_sub(name: str) -> bool:
    """Проверяет, что файл уже русский: *.ru.srt, *.ru_RU.srt, *.ru-RU.srt"""
    return re.search(r'\.ru([-_][A-Z]{2})?\.srt$', name, flags=re.IGNORECASE) is not None


def translate_all_here():
    ensure_deps()
    from srtranslator import SrtFile
    from srtranslator.translators.translatepy import TranslatePy

    cwd = Path(".")
    files = sorted([p for p in cwd.iterdir() if p.is_file() and p.suffix.lower() == ".srt"],
                   key=lambda p: p.name.lower())

    if not files:
        print("ℹ️ В текущей папке нет .srt файлов.")
        return

    tr = TranslatePy()  # лёгкий онлайн-бэкенд (без ключей/моделей)

    any_done = False
    for p in files:
        if is_russian_sub(p.name):
            continue
        out = make_output_name(p)
        print(f"🔄 Перевод: {p.name} → {out.name}", flush=True)
        try:
            s = SrtFile(p.as_posix())
            s.translate(tr, "en", "ru")
            s.save(out.as_posix())
            print(f"✅ Готово: {out.name}", flush=True)
            any_done = True
            time.sleep(0.3)  # чуть замедлим, чтобы не ловить лимиты
        except Exception as e:
            print(f"⚠️ Ошибка перевода {p.name}: {e}", flush=True)

    if not any_done:
        print("ℹ️ Подходящих файлов для перевода не найдено (возможно, только русские).")


if __name__ == "__main__":
    translate_all_here()
