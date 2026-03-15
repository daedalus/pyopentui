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

    def setup(self) -> bool:
        """Set up terminal for raw mode. Returns True if successful."""
        import sys as _sys

        _sys.stderr.write("    Terminal.setup() start\n")

        try:
            # Save old settings
            _sys.stderr.write("    tcgetattr... ")
            self._old_settings = termios.tcgetattr(self.stdin.fileno())
            _sys.stderr.write("ok\n")

            # Set raw mode using tty.setraw
            _sys.stderr.write("    setraw... ")
            tty.setraw(self.stdin.fileno())
            self._is_raw = True
            _sys.stderr.write("ok\n")
            return True
        except Exception as e:
            _sys.stderr.write(f"ERROR: {e}\n")
            # Fall back to cbreak mode
            try:
                _sys.stderr.write("    fallback setcbreak... ")
                self._old_settings = termios.tcgetattr(self.stdin.fileno())
                tty.setcbreak(self.stdin.fileno())
                self._is_raw = True
                _sys.stderr.write("ok\n")
                return True
            except Exception as e2:
                _sys.stderr.write(f"ERROR2: {e2}\n")
                return False

    def cleanup(self) -> None:
        """Restore terminal to original settings."""
        if self._old_settings:
            try:
                termios.tcsetattr(self.stdin.fileno(), termios.TCSADRAIN, self._old_settings)
            except:
                pass
        self._is_raw = False

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
            if select.select([self.stdin], [], [], timeout)[0]:
                ch = self.stdin.read(1)
                if ch:
                    return ch
        except (IOError, OSError):
            pass
        return None

    def read_sequence(self, timeout: float = 0.01) -> Optional[str]:
        """Read an ANSI escape sequence. Returns None if no input."""
        ch = self.read_char(timeout)
        if not ch:
            return None

        # Check for escape sequence
        if ord(ch) == 27:
            seq = ch
            # Read more bytes for the sequence
            while True:
                more = self.read_char(0.001)
                if more:
                    seq += more
                    # Sequence ends when we get a letter (final char)
                    if more.isalpha() or more in "~[]()":
                        break
                else:
                    break
            return seq
        return ch

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
            self.stdout.flush()
        except:
            pass

    def write_bytes(self, data: bytes) -> None:
        """Write bytes to stdout."""
        try:
            os.write(self.stdout.fileno(), data)
        except:
            pass

    def clear_screen(self) -> None:
        """Clear the screen."""
        self.write("\033[2J")

    def home_cursor(self) -> None:
        """Move cursor to home position."""
        self.write("\033[H")

    def set_cursor(self, row: int, col: int) -> None:
        """Set cursor position."""
        self.write(f"\033[{row};{col}H")

    def show_cursor(self) -> None:
        """Show cursor."""
        self.write("\033[?25h")

    def hide_cursor(self) -> None:
        """Hide cursor."""
        self.write("\033[?25l")

    def enter_alternate_screen(self) -> None:
        """Enter alternate screen buffer."""
        try:
            self.write("\033[?1049h")
        except Exception as e:
            import sys as _sys

            _sys.stderr.write(f"enter_alternate_screen error: {e}\n")

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
