"""Rich command input with autocomplete and vim mode for Claude Code-inspired TUI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from rich.text import Text
from textual import events
from textual.suggester import SuggestFromList, Suggester
from textual.widgets import Input


@dataclass
class Command:
    """A command definition.

    Attributes:
        name: Command name (e.g., "eval")
        description: Command description
        aliases: Command aliases (e.g., ["e", "run"])
        args: Command arguments description
    """

    name: str
    description: str
    aliases: list[str] = field(default_factory=list)
    args: str = ""


class CommandSuggester(Suggester):
    """Custom suggester for commands with fuzzy matching."""

    def __init__(
        self,
        commands: list[Command],
        case_sensitive: bool = False,
    ) -> None:
        """Initialize the command suggester.

        Args:
            commands: List of available commands
            case_sensitive: Whether matching is case-sensitive
        """
        super().__init__(use_cache=True, case_sensitive=case_sensitive)
        self._commands = commands
        self._command_names: list[str] = []
        self._update_command_names()

    def _update_command_names(self) -> None:
        """Update the list of command names and aliases."""
        self._command_names = []
        for cmd in self._commands:
            self._command_names.append(cmd.name)
            self._command_names.extend(cmd.aliases)

    def update_commands(self, commands: list[Command]) -> None:
        """Update the list of commands.

        Args:
            commands: New list of commands
        """
        self._commands = commands
        self._update_command_names()

    async def get_suggestion(self, value: str) -> str | None:
        """Get suggestion for the current input value.

        Args:
            value: Current input value

        Returns:
            Suggestion string or None
        """
        if not value:
            return None

        # Find matching commands
        matches = self._fuzzy_match(value)

        if matches:
            # Return the first match
            return matches[0].name

        return None

    def _fuzzy_match(self, value: str) -> list[Command]:
        """Fuzzy match commands against input value.

        Args:
            value: Input value to match

        Returns:
            List of matching commands, sorted by relevance
        """
        matches: list[tuple[int, Command]] = []
        value_lower = value.lower()

        for cmd in self._commands:
            # Check exact prefix match
            if cmd.name.lower().startswith(value_lower):
                matches.append((0, cmd))
                continue

            # Check alias match
            for alias in cmd.aliases:
                if alias.lower().startswith(value_lower):
                    matches.append((1, cmd))
                    break

            # Check substring match
            if value_lower in cmd.name.lower():
                matches.append((2, cmd))

        # Sort by match type (lower is better)
        matches.sort(key=lambda x: x[0])

        return [cmd for _, cmd in matches]

    def get_command(self, name: str) -> Command | None:
        """Get command by name or alias.

        Args:
            name: Command name or alias

        Returns:
            Command or None if not found
        """
        for cmd in self._commands:
            if cmd.name == name:
                return cmd
            if name in cmd.aliases:
                return cmd
        return None


class RichCommandInput(Input):
    """Rich command input with autocomplete, history, and vim mode.

    Features:
    - Command autocomplete with fuzzy matching
    - Command history navigation (up/down arrows)
    - Vim mode (i, a, o, dd, yy, p)
    - Persistent history
    - Command suggestions dropdown

    Usage:
        input = RichCommandInput(
            commands=[
                Command("eval", "Run evaluation", ["e", "run"]),
                Command("audit", "Check config", ["a", "check"]),
            ],
            placeholder="Type a command..."
        )
    """

    def __init__(
        self,
        commands: list[Command] | None = None,
        placeholder: str = "Type a command...",
        max_history: int = 100,
        **kwargs,
    ) -> None:
        """Initialize the rich command input.

        Args:
            commands: List of available commands
            placeholder: Input placeholder text
            max_history: Maximum history entries to keep
        """
        self._commands = commands or []
        self._max_history = max_history
        self._history: list[str] = []
        self._history_index: int = -1
        self._temp_value: str = ""
        self._vim_mode: bool = False
        self._vim_command: str = ""

        # Create suggester
        self._suggester = CommandSuggester(self._commands)

        super().__init__(
            placeholder=placeholder,
            suggester=self._suggester,
            **kwargs,
        )

    @property
    def commands(self) -> list[Command]:
        """Return the list of commands."""
        return self._commands

    @property
    def history(self) -> list[str]:
        """Return the command history."""
        return self._history.copy()

    @property
    def vim_mode(self) -> bool:
        """Return whether vim mode is enabled."""
        return self._vim_mode

    def set_commands(self, commands: list[Command]) -> None:
        """Update the list of commands.

        Args:
            commands: New list of commands
        """
        self._commands = commands
        self._suggester.update_commands(commands)

    def add_command(self, command: Command) -> None:
        """Add a command to the list.

        Args:
            command: Command to add
        """
        self._commands.append(command)
        self._suggester.update_commands(self._commands)

    def add_to_history(self, text: str) -> None:
        """Add an entry to history.

        Args:
            text: Text to add to history
        """
        if text.strip() and text not in self._history:
            self._history.append(text)
            # Trim history if needed
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]

    def clear_history(self) -> None:
        """Clear the command history."""
        self._history.clear()
        self._history_index = -1
        self._temp_value = ""

    def navigate_history(self, direction: int) -> None:
        """Navigate through command history.

        Args:
            direction: Direction to navigate (-1 for up, 1 for down)
        """
        if not self._history:
            return

        if self._history_index == -1:
            self._temp_value = self.value

        new_index = self._history_index + direction

        if new_index < -1:
            return
        elif new_index >= len(self._history):
            return

        self._history_index = new_index

        if self._history_index == -1:
            self.value = self._temp_value
        else:
            self.value = self._history[-(self._history_index + 1)]

    def toggle_vim_mode(self) -> None:
        """Toggle vim mode on/off."""
        self._vim_mode = not self._vim_mode
        self._vim_command = ""

    def on_key(self, event: events.Key) -> None:
        """Handle key events.

        Args:
            event: Key event
        """
        # History navigation with up/down arrows
        if event.key == "up":
            self.navigate_history(-1)
            event.prevent_default()
            return
        elif event.key == "down":
            self.navigate_history(1)
            event.prevent_default()
            return

        # Add to history on enter
        elif event.key == "enter":
            if self.value.strip():
                self.add_to_history(self.value)
                self._history_index = -1

        # Vim mode handling
        if self._vim_mode:
            self._handle_vim_key(event)

        # Call parent handler
        super().on_key(event)

    def _handle_vim_key(self, event: events.Key) -> None:
        """Handle vim mode key events.

        Args:
            event: Key event
        """
        # Exit vim mode with Escape
        if event.key == "escape":
            self._vim_mode = False
            self._vim_command = ""
            return

        # Normal mode commands
        if not self._vim_command:
            if event.key == "i":
                # Insert mode (just a marker, Input is already in insert mode)
                pass
            elif event.key == "a":
                # Move cursor right one position
                if self.cursor_position < len(self.value):
                    self.cursor_position += 1
            elif event.key == "o":
                # Open new line (submit current and clear)
                if self.value.strip():
                    self.add_to_history(self.value)
                self.value = ""
            elif event.key == "d":
                self._vim_command = "d"
            elif event.key == "y":
                self._vim_command = "y"
            elif event.key == "p":
                # Paste (if we had a register, but for now just a placeholder)
                pass
        else:
            # Complete vim command
            if self._vim_command == "d":
                if event.key == "d":
                    # dd: delete line
                    self.value = ""
                    self._vim_command = ""
                elif event.key == "w":
                    # dw: delete word
                    self._delete_word()
                    self._vim_command = ""
            elif self._vim_command == "y":
                if event.key == "y":
                    # yy: yank line (copy to register)
                    # For now, just a placeholder
                    self._vim_command = ""

    def _delete_word(self) -> None:
        """Delete the current word."""
        pos = self.cursor_position
        text = self.value

        # Find start of current word
        start = pos
        while start > 0 and text[start - 1] != " ":
            start -= 1

        # Delete word
        self.value = text[:start] + text[pos:]
        self.cursor_position = start

    def get_command_by_name(self, name: str) -> Command | None:
        """Get a command by name or alias.

        Args:
            name: Command name or alias

        Returns:
            Command or None if not found
        """
        return self._suggester.get_command(name)

    def get_suggestions(self, value: str) -> list[Command]:
        """Get command suggestions for input value.

        Args:
            value: Input value

        Returns:
            List of matching commands
        """
        return self._suggester._fuzzy_match(value)
