# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
"""
Вспомогательные функции для монтирования телефона через adbfs-rootless.
Скрипты находятся в ~/PhoneAsExtStorage/adbfs-rootless/.
"""

import os
import subprocess

_SCRIPTS_DIR = os.path.expanduser("~/PhoneAsExtStorage/adbfs-rootless")
_MOUNT_SCRIPT = os.path.join(_SCRIPTS_DIR, "mount-phone.sh")
_UNMOUNT_SCRIPT = os.path.join(_SCRIPTS_DIR, "unmount-phone.sh")
_PHONE_MOUNT_POINT = os.path.expanduser("~/Phone")


def is_mounted() -> bool:
    """Проверяет, смонтирован ли телефон (внутренняя память ~/Phone)."""
    try:
        result = subprocess.run(
            ["mount"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return _PHONE_MOUNT_POINT + " " in result.stdout or \
               result.stdout.endswith(_PHONE_MOUNT_POINT)
    except Exception:
        return False


def _run_script(script_path: str, *args) -> tuple:
    """
    Запускает скрипт и ждёт завершения (скрипты быстрые, ~4с).
    Возвращает (stdout, stderr, returncode).
    """
    cmd = ["/bin/bash", script_path] + list(args)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Скрипт не завершился за 30 секунд", 1
    except FileNotFoundError:
        return "", f"Скрипт не найден: {script_path}", 1
    except Exception as e:
        return "", str(e), 1


def mount_phone() -> tuple:
    """
    Монтирует внутреннюю память телефона в ~/Phone (и SD в ~/Phone-SD).
    Finder открывается автоматически скриптом.
    Возвращает (success: bool, message: str).
    """
    stdout, stderr, code = _run_script(_MOUNT_SCRIPT)
    if code == 0:
        return True, stdout.strip() or "Телефон успешно смонтирован в ~/Phone"
    else:
        return False, stderr.strip() or stdout.strip() or "Ошибка монтирования"


def mount_phone_system() -> tuple:
    """
    Монтирует системный раздел телефона в ~/Phone-System.
    Возвращает (success: bool, message: str).
    """
    stdout, stderr, code = _run_script(_MOUNT_SCRIPT, "system")
    if code == 0:
        return True, stdout.strip() or "Системный раздел смонтирован в ~/Phone-System"
    else:
        return False, stderr.strip() or stdout.strip() or "Ошибка монтирования системного раздела"


def unmount_phone() -> tuple:
    """
    Размонтирует все точки монтирования телефона.
    Возвращает (success: bool, message: str).
    """
    stdout, stderr, code = _run_script(_UNMOUNT_SCRIPT)
    if code == 0:
        return True, stdout.strip() or "Телефон успешно размонтирован"
    else:
        return False, stderr.strip() or stdout.strip() or "Ошибка размонтирования"
