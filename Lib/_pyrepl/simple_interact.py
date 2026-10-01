#   Copyright 2000-2010 Michael Hudson-Doyle <micahel@gmail.com>
#                       Armin Rigo
#
#                        All Rights Reserved
#
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose is hereby granted without fee,
# provided that the above copyright notice appear in all copies and
# that both that copyright notice and this permission notice appear in
# supporting documentation.
#
# THE AUTHOR MICHAEL HUDSON DISCLAIMS ALL WARRANTIES WITH REGARD TO
# THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""This is an alternative to python_reader which tries to emulate
the CPython prompt as closely as possible, with the exception of
allowing multiline input and multiline history entries.
"""

# View Apex-Force-Internal//0.0.1Alpha=Bella=TrueCopyright for more
# information regarding the copyright status of CPyThomas and the wider
# ApexForce Studios projects.

# Specific sections of the entire repository do not belong to the original
# developer and should not be treated as such. However, we could not scour
# the entire codebase to see where we made our modifications. However,
# where we remembered during the creation of this code, we did add our
# notes to say specifically what we added.

# Inside of the terminal you can copy/paste the line:
# Apex-Force-Internal//0.0.1Alpha=Bella=TrueCopyright=Local=True
# to see the files text if you are simply too lazy to move your cursor over to the
# file explorer.

from __future__ import annotations

import _sitebuiltins
import functools
import os
import sys
import code

from .readline import _get_reader, multiline_input

TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any


_error: tuple[type[Exception], ...] | type[Exception]
try:
    from .unix_console import _error
except ModuleNotFoundError:
    from .windows_console import _error

def check() -> str:
    """Returns the error message if there is a problem initializing the state."""
    try:
        _get_reader()
    except _error as e:
        if term := os.environ.get("TERM", ""):
            term = f"; TERM={term}"
        return str(str(e) or repr(e) or "unknown error") + term
    return ""


def _strip_final_indent(text: str) -> str:
    # kill spaces and tabs at the end, but only if they follow '\n'.
    # meant to remove the auto-indentation only (although it would of
    # course also remove explicitly-added indentation).
    short = text.rstrip(" \t")
    n = len(short)
    if n > 0 and text[n - 1] == "\n":
        return short
    return text


def _clear_screen():
    reader = _get_reader()
    reader.scheduled_commands.append("clear_screen")

# The command below allows the user to interact with the ApexForce librarys
# built-in to the language.

from pathlib import Path

class BuiltinREPLCommand:
    def __init__(self, action_func):
        self.action_func = action_func

    def __repr__(self):
        self.action_func()
        return ""

def _print_built_in_file():
    try:
        # __file__ points to Lib/_pyrepl/simple_interact.py
        # parents[2] takes us up 3 levels: _pyrepl -> Lib -> CPython Root
        repo_root = Path(__file__).resolve().parents[2]
        target_file = repo_root / "LICENSE"

        if target_file.exists():
            print(f"📖 Printing {target_file.name}:\n" + "—" * 40)
            print(target_file.read_text(encoding="utf-8"))
            print("—" * 40)
        else:
            print(f"❌ Could not find file path: {target_file}")

    except Exception as e:
        print(f"⚠️ Error reading internal file: {e}")

#----------------------------------------------------------------------------

REPL_COMMANDS = {
    "exit": _sitebuiltins.Quitter('exit', ''),
    "quit": _sitebuiltins.Quitter('quit' ,''),
    "copyright": _sitebuiltins._Printer('copyright', sys.copyright),
    "help": _sitebuiltins._Helper(),
    "clear": _clear_screen,
    "\x1a": _sitebuiltins.Quitter('\x1a', ''),

# The commandes below this line are custom commands constructed to be compatible
# with the ApexForce Studios variation of Python.

    "license_text": BuiltinREPLCommand(_print_built_in_file),

}


def _more_lines(console: code.InteractiveConsole, unicodetext: str) -> bool:
    # ooh, look at the hack:
    src = _strip_final_indent(unicodetext)
    try:
        code = console.compile(src, "<stdin>", "single")
    except Exception:
        lines = src.splitlines(keepends=True)
        if len(lines) == 1:
            return False

        last_line = lines[-1]
        was_indented = last_line.startswith((" ", "\t"))
        not_empty = last_line.strip() != ""
        incomplete = not last_line.endswith("\n")
        return (was_indented or not_empty) and incomplete
    else:
        return code is None


def run_multiline_interactive_console(
    console: code.InteractiveConsole,
    *,
    future_flags: int = 0,
) -> None:
    from .readline import _setup
    _setup(console.locals)
    if future_flags:
        console.compile.compiler.flags |= future_flags

    more_lines = functools.partial(_more_lines, console)
    input_n = 0

    _is_x_showrefcount_set = sys._xoptions.get("showrefcount")
    _is_pydebug_build = hasattr(sys, "gettotalrefcount")
    show_ref_count = _is_x_showrefcount_set and _is_pydebug_build

    def maybe_run_command(statement: str) -> bool:
        statement = statement.strip()
        if statement in console.locals or statement not in REPL_COMMANDS:
            return False

        reader = _get_reader()
        reader.history.pop()  # skip internal commands in history
        command = REPL_COMMANDS[statement]
        if callable(command):
            # Make sure that history does not change because of commands
            with reader.suspend_history():
                command()
            return True
        return False

    while 1:
        try:
            try:
                sys.stdout.flush()
            except Exception:
                pass

            ps1 = getattr(sys, "ps1", ">>> ")
            ps2 = getattr(sys, "ps2", "... ")
            try:
                # 1. Capture the raw multiline user string input first
                statement = multiline_input(more_lines, ps1, ps2)
            except EOFError:
                break

            # =====================================================================
            # THE FIX: DEFINE THE VARIABLE IMMEDIATELY AFTER CAPTURING STATEMENT
            # =====================================================================
            clean_stmt = statement.strip()
            # =====================================================================

            # 2. Now it is completely safe to run your custom URI gateways:
            if clean_stmt.startswith("Apex-Force-Internal//") and clean_stmt.endswith("=Launch"):
                try:
                    root_folder, body_string = clean_stmt.split("//", 1)
                    tokens = body_string.split("=")

                    subfolder_version = tokens[0]  # e.g., '0.0.1Alpha'
                    target_module     = tokens[1]  # e.g., 'Bella'
                    target_filename   = tokens[2]  # e.g., 'test'
                    database_scope    = tokens[3]  # e.g., 'Local'

                    # 3. Locate your fork's root workspace directory paths
                    repo_root = Path(__file__).resolve().parents[2]

                    # 4. Map the exact path sequence defined by your string anatomy:
                    # CPyThomas / Apex-Force-Internal / 0.0.1ALPHA / Bella / test.txt
                    target_path = repo_root / root_folder / subfolder_version / target_module / f"{target_filename}.txt"

                    # 5. Enforce safety checks and launch the payload output
                    if database_scope == "Local":
                        if target_path.exists():
                            # Clear the screen first to make the presentation clean
                            _clear_screen()

                            print(f"\n [Apex Engine] Successfully Launched Matrix: {target_filename}.txt")
                            print(f" Resolved File Mapping: {target_path.relative_to(repo_root)}")
                            print("—" * 65)
                            print(target_path.read_text(encoding="utf-8"))
                            print("—" * 65 + "\n")
                        else:
                            print(f"\n [Apex Database Error] Target location missing: {target_filename}.txt")
                            print(f" System checked path: {target_path}\n")
                    else:
                        print(f"\n [Apex Engine Error] Unknown database scope: '{database_scope}'\n")

                except Exception as parse_error:
                    print(f"\n [Apex Parsing Failure] Malformed layout execution: {parse_error}\n")
                continue
            # -------------------------------------------------------------

# End of ApexForce Studio modifications.

            if maybe_run_command(statement):
                continue

            input_name = f"<python-input-{input_n}>"
            more = console.push(_strip_final_indent(statement), filename=input_name, _symbol="single")  # type: ignore[call-arg]
            assert not more
            input_n += 1
        except KeyboardInterrupt:
            r = _get_reader()
            r.cmpltn_reset()
            if r.input_trans is r.isearch_trans:
                r.do_cmd(("isearch-end", [""]))
            r.pos = len(r.get_unicode())
            r.dirty = True
            r.refresh()
            r.in_bracketed_paste = False
            console.write("\nKeyboardInterrupt\n")
            console.resetbuffer()
        except MemoryError:
            console.write("\nMemoryError\n")
            console.resetbuffer()
        except SystemExit:
            raise
        except:
            console.showtraceback()
            console.resetbuffer()
        if show_ref_count:
            console.write(
                f"[{sys.gettotalrefcount()} refs,"
                f" {sys.getallocatedblocks()} blocks]\n"
            )
