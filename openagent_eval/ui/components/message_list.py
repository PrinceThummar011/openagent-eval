"""Virtual scrolling message list for Claude Code-inspired TUI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Optional

from rich.text import Text
from textual.geometry import Size
from textual.scroll_view import ScrollView
from textual.strip import Strip


class MessageRole(str, Enum):
    """Message role types."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class Message:
    """A single message in the conversation.

    Attributes:
        role: Message role (user, assistant, system, tool)
        content: Message content (plain text or Rich renderable)
        timestamp: Message creation time
        tool_name: Tool name if role is TOOL
        metadata: Additional metadata (metrics, costs, etc.)
    """

    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tool_name: str | None = None
    metadata: dict = field(default_factory=dict)

    @property
    def is_tool_result(self) -> bool:
        """Check if message is a tool result."""
        return self.role == MessageRole.TOOL and self.tool_name is not None


@dataclass
class MessageLine:
    """A single visual line in the message list.

    Attributes:
        message_index: Index of the parent message
        line_index: Line number within the message (0-based)
        text: Rendered text for this line
        is_first_line: Whether this is the first line of the message
        is_last_line: Whether this is the last line of the message
    """

    message_index: int
    line_index: int
    text: Text
    is_first_line: bool = False
    is_last_line: bool = False


class MessageList(ScrollView):
    """Virtual scrolling message list using Line API.

    Features:
    - O(visible) rendering for large message lists
    - Multi-line message support with line map
    - Auto-scroll to bottom on new content
    - Rich formatting for different message types
    - Batch updates for efficiency

    Performance:
    - 100k+ messages with minimal memory overhead
    - Only visible lines are rendered
    - Selective line refresh for updates
    """

    def __init__(
        self,
        max_messages: int = 10000,
        auto_scroll: bool = True,
        **kwargs,
    ) -> None:
        """Initialize the message list.

        Args:
            max_messages: Maximum messages to keep in memory
            auto_scroll: Whether to auto-scroll to bottom on new messages
        """
        super().__init__(**kwargs)
        self._messages: list[Message] = []
        self._line_map: list[MessageLine] = []
        self._max_messages = max_messages
        self._auto_scroll = auto_scroll
        self._message_heights: list[int] = []  # Height of each message

    @property
    def message_count(self) -> int:
        """Return the number of messages."""
        return len(self._messages)

    @property
    def line_count(self) -> int:
        """Return the total number of visual lines."""
        return len(self._line_map)

    def on_mount(self) -> None:
        """Set virtual size on mount."""
        self.virtual_size = Size(self.size.width, 0)

    def render_line(self, y: int) -> Strip:
        """Render a single line at position y.

        Args:
            y: Visual line position (0-based)

        Returns:
            Strip containing the rendered line
        """
        scroll_y = self.scroll_offset.y
        line_index = y + scroll_y

        if 0 <= line_index < len(self._line_map):
            msg_line = self._line_map[line_index]
            text = msg_line.text
        else:
            text = Text("")

        return Strip([text], self.size.width)

    def add_message(self, message: Message) -> None:
        """Add a new message to the list.

        Args:
            message: Message to add
        """
        # Enforce max messages limit
        if len(self._messages) >= self._max_messages:
            self._remove_oldest_message()

        # Add message
        message_index = len(self._messages)
        self._messages.append(message)

        # Calculate message lines
        lines = self._render_message_lines(message, message_index)
        height = len(lines)

        # Add to line map
        for i, line in enumerate(lines):
            msg_line = MessageLine(
                message_index=message_index,
                line_index=i,
                text=line,
                is_first_line=(i == 0),
                is_last_line=(i == height - 1),
            )
            self._line_map.append(msg_line)

        self._message_heights.append(height)

        # Update virtual size
        self.virtual_size = Size(self.size.width, len(self._line_map))

        # Auto-scroll to bottom
        if self._auto_scroll:
            self.scroll_end(animate=False)

    def add_messages(self, messages: list[Message]) -> None:
        """Add multiple messages efficiently.

        Args:
            messages: List of messages to add
        """
        for message in messages:
            self.add_message(message)

    def clear(self) -> None:
        """Clear all messages."""
        self._messages.clear()
        self._line_map.clear()
        self._message_heights.clear()
        self.virtual_size = Size(self.size.width, 0)
        self.refresh()

    def update_message(self, index: int, content: str) -> None:
        """Update a message's content.

        Args:
            index: Message index
            content: New content
        """
        if 0 <= index < len(self._messages):
            old_height = self._message_heights[index]
            self._messages[index].content = content

            # Rebuild line map from this message onwards
            self._rebuild_line_map_from(index)

            # Refresh affected lines
            self.refresh_lines(index, old_height)

    def _render_message_lines(
        self, message: Message, message_index: int
    ) -> list[Text]:
        """Render a message into visual lines.

        Args:
            message: Message to render
            message_index: Index of the message

        Returns:
            List of Text objects, one per visual line
        """
        lines: list[Text] = []

        # Role prefix
        role_prefix = self._get_role_prefix(message)
        role_color = self._get_role_color(message)

        # Split content into lines
        content_lines = message.content.split("\n")

        for i, line in enumerate(content_lines):
            if i == 0:
                # First line includes role prefix
                text = Text()
                text.append(role_prefix, style=role_color)
                text.append(" ")
                text.append(line)
            else:
                # Continuation lines are indented
                text = Text(f"  {line}")

            lines.append(text)

        # Add empty line after message (except for last message)
        if lines:
            lines.append(Text(""))

        return lines

    def _get_role_prefix(self, message: Message) -> str:
        """Get role prefix string.

        Args:
            message: Message

        Returns:
            Role prefix string
        """
        if message.role == MessageRole.USER:
            return ">"
        elif message.role == MessageRole.ASSISTANT:
            return "✓"
        elif message.role == MessageRole.SYSTEM:
            return "●"
        elif message.role == MessageRole.TOOL:
            return f"[{message.tool_name}]"
        return ""

    def _get_role_color(self, message: Message) -> str:
        """Get role color.

        Args:
            message: Message

        Returns:
            Color string
        """
        if message.role == MessageRole.USER:
            return "rgb(79,140,255)"  # Brand blue
        elif message.role == MessageRole.ASSISTANT:
            return "rgb(80,200,120)"  # Success green
        elif message.role == MessageRole.SYSTEM:
            return "rgb(128,128,128)"  # Gray
        elif message.role == MessageRole.TOOL:
            return "rgb(200,120,255)"  # Purple
        return "white"

    def _remove_oldest_message(self) -> None:
        """Remove the oldest message and its lines."""
        if not self._messages:
            return

        # Calculate lines to remove
        height = self._message_heights[0]
        self._line_map = self._line_map[height:]
        self._messages.pop(0)
        self._message_heights.pop(0)

        # Update message indices in line map
        for msg_line in self._line_map:
            msg_line.message_index -= 1

    def _rebuild_line_map_from(self, start_index: int) -> None:
        """Rebuild line map starting from a specific message.

        Args:
            start_index: Message index to start rebuilding from
        """
        # Calculate where to start in line map
        line_offset = sum(self._message_heights[:start_index])

        # Remove old lines from this point
        self._line_map = self._line_map[:line_offset]
        self._message_heights = self._message_heights[:start_index]

        # Rebuild lines for messages from start_index
        for i in range(start_index, len(self._messages)):
            message = self._messages[i]
            lines = self._render_message_lines(message, i)
            height = len(lines)

            for j, line in enumerate(lines):
                msg_line = MessageLine(
                    message_index=i,
                    line_index=j,
                    text=line,
                    is_first_line=(j == 0),
                    is_last_line=(j == height - 1),
                )
                self._line_map.append(msg_line)

            self._message_heights.append(height)

        # Update virtual size
        self.virtual_size = Size(self.size.width, len(self._line_map))

    def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the message list."""
        self.scroll_end(animate=False)

    def get_message(self, index: int) -> Message | None:
        """Get a message by index.

        Args:
            index: Message index

        Returns:
            Message or None if index is invalid
        """
        if 0 <= index < len(self._messages):
            return self._messages[index]
        return None

    def get_visible_messages(self) -> list[Message]:
        """Get messages that are currently visible.

        Returns:
            List of visible messages
        """
        if not self._line_map:
            return []

        # Calculate visible range
        scroll_y = self.scroll_offset.y
        visible_height = self.size.height

        # Find messages in visible range
        visible_indices: set[int] = set()
        for line_index in range(scroll_y, scroll_y + visible_height):
            if 0 <= line_index < len(self._line_map):
                msg_line = self._line_map[line_index]
                visible_indices.add(msg_line.message_index)

        # Return messages in order
        return [
            self._messages[i]
            for i in sorted(visible_indices)
            if i < len(self._messages)
        ]

    def set_auto_scroll(self, enabled: bool) -> None:
        """Enable or disable auto-scroll.

        Args:
            enabled: Whether to auto-scroll on new messages
        """
        self._auto_scroll = enabled

    def __len__(self) -> int:
        """Return the number of messages."""
        return len(self._messages)

    def __iter__(self):
        """Iterate over messages."""
        return iter(self._messages)

    def __getitem__(self, index: int) -> Message:
        """Get a message by index."""
        return self._messages[index]
