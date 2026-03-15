"""
Native terminal bindings for Python.
Provides SSH-compatible terminal I/O similar to Node.js/Bun.
"""

import sys
import os
import select
import fcntl
import termios
import tty
import signal
from typing import Callable, Optional, List


class Terminal:
    """Native terminal handler that works in SSH."""

    def __init__(self, stdin=None, stdout=None):
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self._old_settings: Optional[tuple] = None
        self._old_flags: Optional[int] = None
        self._is_raw = False
        self._data_callbacks: List[Callable[[str], None]] = []
        self._running = False

    def isatty(self) -> bool:
        """Check if we have a TTY."""
        return self.stdin.isatty()

    def get_size(self) -> tuple:
        """Get current terminal size. Returns (width, height)."""
        try:
            size = os.get_terminal_size()
            return (size.columns, size.lines)
        except OSError:
            return (80, 24)

    def setup(self) -> bool:
        """Set up terminal for raw mode. Returns True if successful."""
        try:
            if self.stdin.isatty():
                self._old_settings = termios.tcgetattr(self.stdin.fileno())
                raw = list(termios.tcgetattr(self.stdin.fileno()))
                raw[3] = raw[3] & ~(termios.ICANON | termios.ECHO | termios.ISIG)
                raw[6][termios.VMIN] = 0
                raw[6][termios.VTIME] = 0
                termios.tcsetattr(self.stdin.fileno(), termios.TCSADRAIN, raw)
                self._is_raw = True
                return True
        except:
            pass
        return False

    def cleanup(self) -> None:
        """Restore terminal to original settings."""
        if self._old_settings:
            try:
                termios.tcsetattr(self.stdin.fileno(), termios.TCSADRAIN, self._old_settings)
            except:
                pass
        self._is_raw = False
        self.restore_flags()

        if self._old_settings:
            try:
                termios.tcsetattr(self.stdin.fileno(), termios.TCSADRAIN, self._old_settings)
            except:
                pass
        self._is_raw = False

        self.restore_flags()

        try:
            subprocess.run(
                ["reset", "-q"],
                stdin=self.stdin,
                stdout=self.stdout,
                stderr=subprocess.DEVNULL,
                timeout=0.5,
            )
        except:
            pass

    def set_raw_mode(self, enabled: bool) -> bool:
        """Enable/disable raw mode. Returns True if successful."""
        if enabled:
            return self.setup()
        else:
            self.cleanup()
            return True

    def make_nonblocking(self) -> bool:
        """Make stdin non-blocking. Returns True if successful."""
        try:
            flags = fcntl.fcntl(self.stdin.fileno(), fcntl.F_GETFL)
            self._old_flags = flags
            fcntl.fcntl(self.stdin.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)
            return True
        except:
            return False

    def restore_flags(self) -> None:
        """Restore original file flags."""
        if self._old_flags is not None:
            try:
                fcntl.fcntl(self.stdin.fileno(), fcntl.F_SETFL, self._old_flags)
            except:
                pass

    def read_char(self, timeout: float = 0.01) -> Optional[str]:
        """Read a single character. Returns None if no input."""
        try:
            import errno

            fd = self.stdin.fileno()
            while True:
                try:
                    ch = os.read(fd, 1)
                    if ch:
                        return ch.decode("utf-8", errors="replace")
                except OSError as e:
                    if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                        if timeout > 0:
                            import time

                            time.sleep(0.001)
                            timeout -= 0.001
                            if timeout <= 0:
                                return None
                            continue
                        return None
                    else:
                        return None
        except:
            pass
        return None

    def read_sequence(self, timeout: float = 0.01) -> Optional[str]:
        """Read an ANSI escape sequence. Returns None if no input."""
        ch = self.read_char(timeout)
        if not ch:
            return None

        if ord(ch) == 27:
            seq = ch
            for _ in range(10):
                more = self.read_char(0.002)
                if more:
                    seq += more
                    if more.isalpha() or more in "~[]()":
                        break
                else:
                    break
            return seq
        return ch

    def read_key(self, timeout: float = 0.01) -> Optional[dict]:
        """Read a key with proper escape handling. Returns None if no input."""
        ch = self.read_char(timeout)
        if not ch:
            return None

        if ord(ch) == 27:
            return {"type": "key", "name": "escape", "raw": ch}

        if ch == "\x1b[":
            seq = ch
            for _ in range(10):
                more = self.read_char(0.002)
                if more:
                    seq += more
                    if more.isalpha() or more in "~[]()":
                        break
                else:
                    break
            codes = {
                "A": "up",
                "B": "down",
                "C": "right",
                "D": "left",
                "H": "home",
                "F": "end",
                "P": "f1",
                "Q": "f2",
                "R": "f3",
                "S": "f4",
                "15~": "f5",
                "17~": "f6",
                "18~": "f7",
                "19~": "f8",
                "20~": "f9",
                "21~": "f10",
                "23~": "f11",
                "24~": "f12",
            }
            suffix = seq[2:]
            for code, name in codes.items():
                if suffix == code:
                    return {"type": "key", "name": name, "raw": seq}
            if suffix.startswith(("1;", "2;", "3;", "4;", "5;", "6;")):
                parts = suffix.split(";")
                if len(parts) >= 2:
                    mod = (
                        parts[0]
                        .replace("1;", "")
                        .replace("2;", "shift-")
                        .replace("3;", "alt-")
                        .replace("4;", "shift-alt-")
                    )
                    base = parts[1]
                    if base in codes:
                        return {"type": "key", "name": mod + codes[base], "raw": seq}
            return {"type": "key", "raw": seq}

        key_map = {"\r": "enter", "\n": "enter", "\t": "tab", "\x7f": "backspace", " ": "space"}
        name = key_map.get(ch, ch)
        return {"type": "key", "name": name, "char": ch, "raw": ch}

    def read_available(self, timeout: float = 0.01) -> str:
        """Read all available input. Returns empty string if none."""
        result = ""
        try:
            while select.select([self.stdin], [], [], timeout)[0]:
                data = self.stdin.read(4096)
                if data:
                    result += data
                else:
                    break
        except (IOError, OSError):
            pass
        return result

    def on_data(self, callback: Callable[[str], None]) -> None:
        """Register a callback for input data."""
        self._data_callbacks.append(callback)

    def poll(self, timeout: float = 0.05) -> List[str]:
        """Poll for input and return list of sequences."""
        sequences = []

        # Try to read with escape sequence parsing
        while True:
            seq = self.read_sequence(0.001)
            if seq:
                sequences.append(seq)
                for cb in self._data_callbacks:
                    cb(seq)
            else:
                break

        return sequences

    def write(self, data: str) -> None:
        """Write to stdout."""
        try:
            self.stdout.write(data)
        except:
            pass

    def flush(self) -> None:
        """Flush stdout."""
        try:
            self.stdout.flush()
        except:
            pass

    def write_bytes(self, data: bytes) -> None:
        """Write bytes to stdout."""
        try:
            os.write(self.stdout.fileno(), data)
        except:
            pass

    def home_cursor(self) -> None:
        """Move cursor to home position."""
        self.write("\033[H")

    def set_cursor(self, row: int, col: int) -> None:
        """Set cursor position."""
        self.write(f"\033[{row};{col}H")

    def clear_screen(self) -> None:
        """Clear the screen."""
        self.write("\033[2J")

    def set_background_color(self, r: int, g: int, b: int) -> None:
        """Set background color using RGB."""
        self.write(f"\033[48;2;{r};{g};{b}m")

    def disable_line_wrap(self) -> None:
        """Disable line wrapping."""
        self.write("\033[?7l")

    def enable_line_wrap(self) -> None:
        """Enable line wrapping."""
        self.write("\033[?7h")

    def show_cursor(self) -> None:
        """Show cursor."""
        self.write("\033[?25h")

    def hide_cursor(self) -> None:
        """Hide cursor."""
        self.write("\033[?25l")

    def enter_alternate_screen(self) -> None:
        """Enter alternate screen buffer."""
        self.write("\033[?1049h")

    def exit_alternate_screen(self) -> None:
        """Exit alternate screen buffer."""
        self.write("\033[?1049l")

    def enable_mouse_tracking(self) -> None:
        """Enable mouse tracking."""
        self.write("\033[?1000h")
        self.write("\033[?1002h")
        self.write("\033[?1015h")
        self.write("\033[?1006h")

    def disable_mouse_tracking(self) -> None:
        """Disable mouse tracking."""
        self.write("\033[?1000l")
        self.write("\033[?1002l")
        self.write("\033[?1015l")
        self.write("\033[?1006l")

    def reset(self) -> None:
        """Reset terminal."""
        self.write("\033[0m")
        self.write("\033c")

    def setup_screen(self, r: int = 0, g: int = 0, b: int = 0) -> None:
        """Set up screen for rendering - alternate screen, background, clear."""
        self.enter_alternate_screen()
        self.set_background_color(r, g, b)
        self.clear_screen()
        self.disable_line_wrap()
        self.flush()

    def restore_screen(self) -> None:
        """Restore screen to normal - exit alternate screen, reset."""
        self.enable_line_wrap()
        self.reset()
        self.exit_alternate_screen()
        self.flush()


class EventEmitter:
    """Simple event emitter for terminal events."""

    def __init__(self):
        self._listeners: dict = {}

    def on(self, event: str, callback: Callable) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def off(self, event: str, callback: Callable) -> None:
        if event in self._listeners:
            self._listeners[event] = [cb for cb in self._listeners[event] if cb != callback]

    def emit(self, event: str, *args, **kwargs) -> None:
        if event in self._listeners:
            for cb in self._listeners[event]:
                cb(*args, **kwargs)


class InputReader:
    """Enhanced input reader with key parsing."""

    def __init__(self, terminal: Terminal):
        self.terminal = terminal
        self._key_map = {
            "\r": "enter",
            "\n": "enter",
            "\t": "tab",
            "\x7f": "backspace",
            "\x1b": "escape",
            " ": "space",
        }

    def read_key(self) -> Optional[dict]:
        """Read a key and return key info dict."""
        seq = self.terminal.read_sequence(0.01)
        if not seq:
            return None

        # Parse the sequence
        if seq == "\x1b":
            return {"type": "key", "name": "escape", "raw": seq}

        # Function keys
        if seq.startswith("\x1b["):
            codes = {
                "A": "up",
                "B": "down",
                "C": "right",
                "D": "left",
                "H": "home",
                "F": "end",
                "P": "f1",
                "Q": "f2",
                "R": "f3",
                "S": "f4",
                "15~": "f5",
                "17~": "f6",
                "18~": "f7",
                "19~": "f8",
                "20~": "f9",
                "21~": "f10",
                "23~": "f11",
                "24~": "f12",
            }
            suffix = seq[2:]
            for code, name in codes.items():
                if suffix == code:
                    return {"type": "key", "name": name, "raw": seq}

            # Arrow keys with modifiers
            if suffix.startswith(("1;", "2;", "3;", "4;", "5;", "6;")):
                mod = (
                    suffix.split(";")[0]
                    .replace("1;", "")
                    .replace("2;", "shift-")
                    .replace("3;", "alt-")
                    .replace("4;", "shift-alt-")
                )
                base = suffix.split(";")[1] if ";" in suffix else suffix
                if base in codes:
                    return {"type": "key", "name": mod + codes[base], "raw": seq}

        # Regular character
        if len(seq) == 1:
            name = self._key_map.get(seq, seq)
            return {"type": "key", "name": name, "char": seq, "raw": seq}

        return {"type": "key", "raw": seq}


def get_terminal_size() -> tuple:
    """Get terminal size. Returns (width, height)."""
    try:
        size = os.get_terminal_size()
        return (size.columns, size.lines)
    except OSError:
        return (80, 24)


def detect_ssh() -> bool:
    """Detect if running in SSH."""
    return (
        os.environ.get("SSH_CLIENT")
        or os.environ.get("SSH_TTY")
        or os.environ.get("SSH_CONNECTION")
    )


def detect_terminal() -> str:
    """Detect terminal type."""
    return os.environ.get("TERM", "unknown")
