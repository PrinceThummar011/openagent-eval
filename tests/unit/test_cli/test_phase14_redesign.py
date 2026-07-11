"""Tests for Phase 14 TUI redesign components."""

from __future__ import annotations

import pytest

from openagent_eval.ui.theme import (
    DARK_THEME,
    LIGHT_THEME,
    Theme,
    ThemeName,
    format_metric_score,
    get_metric_color,
    get_theme,
)
from openagent_eval.ui.streaming import (
    StreamingManager,
    StreamingState,
    SPINNER_FRAMES,
    STATE_TRANSITIONS,
)
from openagent_eval.ui.components.spinner import SpinnerWidget, ROTATING_TIPS
from openagent_eval.ui.components.command_input import (
    Command,
    CommandSuggester,
    RichCommandInput,
)
from openagent_eval.ui.components.footer import StatusFooter
from openagent_eval.ui.components.message_list import Message, MessageList, MessageRole
from openagent_eval.ui.tools.eval import EvalResultPanel
from openagent_eval.ui.tools.audit import AuditResultPanel
from openagent_eval.ui.tools.diagnose import DiagnoseResultPanel


class TestThemeSystem:
    """Tests for the theme system."""

    def test_default_theme_is_dark(self):
        """Test that default theme is dark."""
        theme = get_theme()
        assert theme == DARK_THEME

    def test_get_theme_by_name(self):
        """Test getting theme by name."""
        theme = get_theme(ThemeName.LIGHT)
        assert theme == LIGHT_THEME

    def test_get_theme_by_string(self):
        """Test getting theme by string."""
        theme = get_theme("light")
        assert theme == LIGHT_THEME

    def test_theme_has_brand_color(self):
        """Test that theme has brand color."""
        assert DARK_THEME.brand == "rgb(79,140,255)"

    def test_theme_has_metric_colors(self):
        """Test that theme has metric colors."""
        assert DARK_THEME.metric_excellent == "rgb(80,200,120)"
        assert DARK_THEME.metric_good == "rgb(120,200,80)"
        assert DARK_THEME.metric_fair == "rgb(255,200,50)"
        assert DARK_THEME.metric_poor == "rgb(255,140,50)"
        assert DARK_THEME.metric_bad == "rgb(255,80,80)"

    def test_theme_has_diff_colors(self):
        """Test that theme has diff colors."""
        assert DARK_THEME.diff_added == "rgb(80,200,120)"
        assert DARK_THEME.diff_removed == "rgb(255,80,80)"

    def test_theme_is_frozen(self):
        """Test that theme is frozen (immutable)."""
        with pytest.raises(AttributeError):
            DARK_THEME.brand = "new_color"  # type: ignore

    def test_get_metric_color_excellent(self):
        """Test metric color for excellent score."""
        color = get_metric_color(0.95)
        assert color == DARK_THEME.metric_excellent

    def test_get_metric_color_good(self):
        """Test metric color for good score."""
        color = get_metric_color(0.75)
        assert color == DARK_THEME.metric_good

    def test_get_metric_color_fair(self):
        """Test metric color for fair score."""
        color = get_metric_color(0.55)
        assert color == DARK_THEME.metric_fair

    def test_get_metric_color_poor(self):
        """Test metric color for poor score."""
        color = get_metric_color(0.35)
        assert color == DARK_THEME.metric_poor

    def test_get_metric_color_bad(self):
        """Test metric color for bad score."""
        color = get_metric_color(0.15)
        assert color == DARK_THEME.metric_bad

    def test_format_metric_score(self):
        """Test formatting metric score with color."""
        formatted = format_metric_score(0.85)
        assert "85.0%" in formatted
        assert "rgb(120,200,80)" in formatted

    def test_all_themes_registered(self):
        """Test that all themes are registered."""
        assert ThemeName.DARK in [ThemeName.DARK, ThemeName.LIGHT, ThemeName.ANSI_DARK, ThemeName.ANSI_LIGHT]


class TestStreamingManager:
    """Tests for the streaming manager."""

    def test_initial_state(self):
        """Test initial state is idle."""
        manager = StreamingManager()
        assert manager.state == StreamingState.IDLE
        assert not manager.is_active

    def test_start_requesting(self):
        """Test starting request transitions to requesting."""
        manager = StreamingManager()
        result = manager.start_requesting("Test operation")
        assert manager.state == StreamingState.REQUESTING
        assert manager.is_active

    def test_transition_to_thinking(self):
        """Test transition to thinking state."""
        manager = StreamingManager()
        manager.start_requesting()
        manager.start_thinking()
        assert manager.state == StreamingState.THINKING

    def test_transition_to_evaluating(self):
        """Test transition to evaluating state."""
        manager = StreamingManager()
        manager.start_requesting()
        manager.start_evaluating("Evaluating...")
        assert manager.state == StreamingState.EVALUATING

    def test_transition_to_tool_input(self):
        """Test transition to tool input state."""
        manager = StreamingManager()
        manager.start_requesting()
        manager.start_evaluating()
        manager.start_tool_input("run")
        assert manager.state == StreamingState.TOOL_INPUT

    def test_transition_to_tool_use(self):
        """Test transition to tool use state."""
        manager = StreamingManager()
        manager.start_requesting()
        manager.start_evaluating()
        manager.start_tool_input("run")
        manager.start_tool_use("run")
        assert manager.state == StreamingState.TOOL_USE

    def test_finish(self):
        """Test finish transitions to idle."""
        manager = StreamingManager()
        manager.start_requesting()
        manager.finish()
        assert manager.state == StreamingState.IDLE
        assert not manager.is_active

    def test_invalid_transition(self):
        """Test invalid transition returns False."""
        manager = StreamingManager()
        result = manager.transition(StreamingState.THINKING)
        assert result is False
        assert manager.state == StreamingState.IDLE

    def test_spinner_frame(self):
        """Test spinner frame is valid."""
        manager = StreamingManager()
        manager.start_requesting()
        frame = manager.spinner_frame
        assert frame in SPINNER_FRAMES

    def test_advance_frame(self):
        """Test advancing frame changes spinner."""
        manager = StreamingManager()
        manager.start_requesting()
        frame1 = manager.spinner_frame
        frame2 = manager.advance_frame()
        # Frame should advance
        assert manager._frame_index == 1

    def test_increment_tokens(self):
        """Test incrementing token count."""
        manager = StreamingManager()
        manager.increment_tokens(10)
        assert manager._token_count == 10
        manager.increment_tokens(5)
        assert manager._token_count == 15

    def test_get_status(self):
        """Test getting status dictionary."""
        manager = StreamingManager()
        status = manager.get_status()
        assert "state" in status
        assert "elapsed" in status
        assert "spinner" in status
        assert "tokens" in status
        assert "operation" in status

    def test_listener_called(self):
        """Test that listeners are called on state change."""
        manager = StreamingManager()
        called_states = []
        manager.add_listener(lambda s: called_states.append(s))
        manager.start_requesting()
        assert StreamingState.REQUESTING in called_states


class TestSpinnerWidget:
    """Tests for the spinner widget."""

    def test_spinner_widget_exists(self):
        """Test that SpinnerWidget can be imported."""
        assert SpinnerWidget is not None

    def test_rotating_tips_exist(self):
        """Test that rotating tips are defined."""
        assert len(ROTATING_TIPS) > 0

    def test_spinner_frames_exist(self):
        """Test that spinner frames are defined."""
        assert len(SPINNER_FRAMES) == 10


class TestStatusFooter:
    """Tests for the status footer widget."""

    def test_status_footer_exists(self):
        """Test that StatusFooter can be imported."""
        assert StatusFooter is not None

    def test_default_values(self):
        """Test default values."""
        footer = StatusFooter()
        assert footer.model_name == "gpt-4"
        assert footer.cost == 0.0
        assert footer.elapsed == 0.0
        assert footer.token_count == 0
        assert footer.progress == 0


class TestToolRenderers:
    """Tests for tool-specific renderers."""

    def test_eval_panel_exists(self):
        """Test that EvalResultPanel can be imported."""
        assert EvalResultPanel is not None

    def test_audit_panel_exists(self):
        """Test that AuditResultPanel can be imported."""
        assert AuditResultPanel is not None

    def test_diagnose_panel_exists(self):
        """Test that DiagnoseResultPanel can be imported."""
        assert DiagnoseResultPanel is not None

    def test_eval_panel_default_title(self):
        """Test EvalResultPanel default title."""
        panel = EvalResultPanel()
        assert panel._title == "Evaluation Results"

    def test_audit_panel_default_title(self):
        """Test AuditResultPanel default title."""
        panel = AuditResultPanel()
        assert panel._title == "Audit Results"

    def test_diagnose_panel_default_title(self):
        """Test DiagnoseResultPanel default title."""
        panel = DiagnoseResultPanel()
        assert panel._title == "Blame Attribution"

    def test_eval_panel_update_metrics(self):
        """Test updating metrics on EvalResultPanel."""
        panel = EvalResultPanel()
        panel.update_metrics({"faithfulness": 0.85, "relevancy": 0.72})
        assert panel._metrics == {"faithfulness": 0.85, "relevancy": 0.72}

    def test_audit_panel_update_issues(self):
        """Test updating issues on AuditResultPanel."""
        panel = AuditResultPanel()
        issues = [{"type": "contradiction", "count": 2, "severity": "high", "status": "warning"}]
        panel.update_issues(issues)
        assert panel._issues == issues

    def test_diagnose_panel_update_components(self):
        """Test updating components on DiagnoseResultPanel."""
        panel = DiagnoseResultPanel()
        components = [{"component": "retrieval", "blame": 0.6, "confidence": 0.8, "recommendation": "Improve chunking"}]
        panel.update_components(components)
        assert panel._components == components


class TestStateTransitions:
    """Tests for state transition validity."""

    def test_idle_to_requesting(self):
        """Test IDLE -> REQUESTING is valid."""
        assert StreamingState.REQUESTING in STATE_TRANSITIONS[StreamingState.IDLE]

    def test_requesting_to_thinking(self):
        """Test REQUESTING -> THINKING is valid."""
        assert StreamingState.THINKING in STATE_TRANSITIONS[StreamingState.REQUESTING]

    def test_requesting_to_evaluating(self):
        """Test REQUESTING -> EVALUATING is valid."""
        assert StreamingState.EVALUATING in STATE_TRANSITIONS[StreamingState.REQUESTING]

    def test_evaluating_to_tool_input(self):
        """Test EVALUATING -> TOOL_INPUT is valid."""
        assert StreamingState.TOOL_INPUT in STATE_TRANSITIONS[StreamingState.EVALUATING]

    def test_tool_input_to_tool_use(self):
        """Test TOOL_INPUT -> TOOL_USE is valid."""
        assert StreamingState.TOOL_USE in STATE_TRANSITIONS[StreamingState.TOOL_INPUT]

    def test_tool_use_to_evaluating(self):
        """Test TOOL_USE -> EVALUATING is valid."""
        assert StreamingState.EVALUATING in STATE_TRANSITIONS[StreamingState.TOOL_USE]

    def test_all_states_can_return_to_idle(self):
        """Test all states can transition to IDLE."""
        for state, transitions in STATE_TRANSITIONS.items():
            if state != StreamingState.IDLE:
                assert StreamingState.IDLE in transitions, f"{state} cannot return to IDLE"


class TestMessage:
    """Tests for the Message dataclass."""

    def test_message_creation(self):
        """Test creating a message."""
        msg = Message(role=MessageRole.USER, content="Hello")
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"
        assert msg.timestamp is not None

    def test_message_with_tool_name(self):
        """Test creating a tool message with tool name."""
        msg = Message(role=MessageRole.TOOL, content="Result", tool_name="eval")
        assert msg.tool_name == "eval"
        assert msg.is_tool_result

    def test_message_without_tool_name(self):
        """Test that non-tool messages are not tool results."""
        msg = Message(role=MessageRole.ASSISTANT, content="Response")
        assert msg.is_tool_result is False

    def test_message_metadata(self):
        """Test message with metadata."""
        msg = Message(
            role=MessageRole.TOOL,
            content="Result",
            metadata={"cost": 0.01, "tokens": 100}
        )
        assert msg.metadata["cost"] == 0.01
        assert msg.metadata["tokens"] == 100


class TestMessageList:
    """Tests for the MessageList widget."""

    def test_message_list_exists(self):
        """Test that MessageList can be imported."""
        assert MessageList is not None

    def test_message_list_creation(self):
        """Test creating a MessageList."""
        ml = MessageList()
        assert ml.message_count == 0
        assert ml.line_count == 0

    def test_message_list_max_messages(self):
        """Test max messages limit."""
        ml = MessageList(max_messages=3)
        for i in range(5):
            ml.add_message(Message(role=MessageRole.USER, content=f"Msg {i}"))
        assert ml.message_count == 3

    def test_add_message(self):
        """Test adding a message."""
        ml = MessageList()
        ml.add_message(Message(role=MessageRole.USER, content="Hello"))
        assert ml.message_count == 1

    def test_add_messages_batch(self):
        """Test adding multiple messages."""
        ml = MessageList()
        messages = [
            Message(role=MessageRole.USER, content=f"Msg {i}")
            for i in range(10)
        ]
        ml.add_messages(messages)
        assert ml.message_count == 10

    def test_clear_messages(self):
        """Test clearing messages."""
        ml = MessageList()
        ml.add_message(Message(role=MessageRole.USER, content="Hello"))
        ml.clear()
        assert ml.message_count == 0
        assert ml.line_count == 0

    def test_get_message(self):
        """Test getting a message by index."""
        ml = MessageList()
        msg = Message(role=MessageRole.USER, content="Hello")
        ml.add_message(msg)
        retrieved = ml.get_message(0)
        assert retrieved is not None
        assert retrieved.content == "Hello"

    def test_get_message_invalid_index(self):
        """Test getting message with invalid index."""
        ml = MessageList()
        retrieved = ml.get_message(0)
        assert retrieved is None

    def test_message_role_prefixes(self):
        """Test that different roles have different prefixes."""
        ml = MessageList()
        ml.add_message(Message(role=MessageRole.USER, content="Hello"))
        ml.add_message(Message(role=MessageRole.ASSISTANT, content="Hi"))
        ml.add_message(Message(role=MessageRole.SYSTEM, content="System msg"))
        ml.add_message(Message(role=MessageRole.TOOL, content="Tool result", tool_name="eval"))
        assert ml.message_count == 4

    def test_multi_line_message(self):
        """Test message with multiple lines."""
        ml = MessageList()
        ml.add_message(Message(role=MessageRole.USER, content="Line 1\nLine 2\nLine 3"))
        assert ml.message_count == 1
        # Multi-line message should have more lines
        assert ml.line_count > 1

    def test_iter_messages(self):
        """Test iterating over messages."""
        ml = MessageList()
        for i in range(5):
            ml.add_message(Message(role=MessageRole.USER, content=f"Msg {i}"))
        messages = list(ml)
        assert len(messages) == 5

    def test_len_messages(self):
        """Test len() returns message count."""
        ml = MessageList()
        for i in range(3):
            ml.add_message(Message(role=MessageRole.USER, content=f"Msg {i}"))
        assert len(ml) == 3

    def test_getitem_messages(self):
        """Test indexing messages."""
        ml = MessageList()
        ml.add_message(Message(role=MessageRole.USER, content="First"))
        ml.add_message(Message(role=MessageRole.USER, content="Second"))
        assert ml[0].content == "First"
        assert ml[1].content == "Second"

    def test_auto_scroll_default(self):
        """Test auto_scroll is enabled by default."""
        ml = MessageList()
        assert ml._auto_scroll is True

    def test_set_auto_scroll(self):
        """Test setting auto_scroll."""
        ml = MessageList()
        ml.set_auto_scroll(False)
        assert ml._auto_scroll is False


class TestCommand:
    """Tests for the Command dataclass."""

    def test_command_creation(self):
        """Test creating a command."""
        cmd = Command(name="eval", description="Run evaluation")
        assert cmd.name == "eval"
        assert cmd.description == "Run evaluation"
        assert cmd.aliases == []
        assert cmd.args == ""

    def test_command_with_aliases(self):
        """Test creating a command with aliases."""
        cmd = Command(
            name="eval",
            description="Run evaluation",
            aliases=["e", "run"],
            args="--config FILE"
        )
        assert cmd.aliases == ["e", "run"]
        assert cmd.args == "--config FILE"


class TestCommandSuggester:
    """Tests for the CommandSuggester."""

    def test_suggester_creation(self):
        """Test creating a suggester."""
        commands = [
            Command(name="eval", description="Run evaluation"),
            Command(name="audit", description="Check config"),
        ]
        suggester = CommandSuggester(commands)
        assert suggester._commands == commands

    def test_fuzzy_match_prefix(self):
        """Test fuzzy matching with prefix."""
        commands = [
            Command(name="eval", description="Run evaluation"),
            Command(name="audit", description="Check config"),
        ]
        suggester = CommandSuggester(commands)
        matches = suggester._fuzzy_match("ev")
        assert len(matches) == 1
        assert matches[0].name == "eval"

    def test_fuzzy_match_alias(self):
        """Test fuzzy matching with alias."""
        commands = [
            Command(name="eval", description="Run evaluation", aliases=["e"]),
            Command(name="audit", description="Check config", aliases=["a"]),
        ]
        suggester = CommandSuggester(commands)
        matches = suggester._fuzzy_match("e")
        assert len(matches) >= 1
        assert any(cmd.name == "eval" for cmd in matches)

    def test_fuzzy_match_substring(self):
        """Test fuzzy matching with substring."""
        commands = [
            Command(name="eval", description="Run evaluation"),
            Command(name="evaluate", description="Run eval"),
        ]
        suggester = CommandSuggester(commands)
        matches = suggester._fuzzy_match("alu")
        assert len(matches) == 1
        assert matches[0].name == "evaluate"

    def test_get_command_by_name(self):
        """Test getting command by name."""
        commands = [
            Command(name="eval", description="Run evaluation"),
            Command(name="audit", description="Check config"),
        ]
        suggester = CommandSuggester(commands)
        cmd = suggester.get_command("eval")
        assert cmd is not None
        assert cmd.name == "eval"

    def test_get_command_by_alias(self):
        """Test getting command by alias."""
        commands = [
            Command(name="eval", description="Run evaluation", aliases=["e"]),
        ]
        suggester = CommandSuggester(commands)
        cmd = suggester.get_command("e")
        assert cmd is not None
        assert cmd.name == "eval"

    def test_get_command_not_found(self):
        """Test getting command that doesn't exist."""
        commands = [
            Command(name="eval", description="Run evaluation"),
        ]
        suggester = CommandSuggester(commands)
        cmd = suggester.get_command("nonexistent")
        assert cmd is None

    def test_update_commands(self):
        """Test updating commands."""
        commands = [
            Command(name="eval", description="Run evaluation"),
        ]
        suggester = CommandSuggester(commands)
        new_commands = [
            Command(name="audit", description="Check config"),
        ]
        suggester.update_commands(new_commands)
        assert suggester._commands == new_commands


class TestRichCommandInput:
    """Tests for the RichCommandInput widget."""

    def test_command_input_exists(self):
        """Test that RichCommandInput can be imported."""
        assert RichCommandInput is not None

    def test_command_input_creation(self):
        """Test creating a RichCommandInput."""
        commands = [
            Command(name="eval", description="Run evaluation"),
        ]
        input_widget = RichCommandInput(commands=commands)
        assert input_widget.commands == commands

    def test_command_input_default_placeholder(self):
        """Test default placeholder."""
        input_widget = RichCommandInput()
        assert input_widget.placeholder == "Type a command..."

    def test_add_to_history(self):
        """Test adding to history."""
        input_widget = RichCommandInput()
        input_widget.add_to_history("eval --config test.yaml")
        assert len(input_widget.history) == 1
        assert input_widget.history[0] == "eval --config test.yaml"

    def test_add_to_history_no_duplicates(self):
        """Test that history doesn't contain duplicates."""
        input_widget = RichCommandInput()
        input_widget.add_to_history("eval")
        input_widget.add_to_history("eval")
        assert len(input_widget.history) == 1

    def test_add_to_history_no_empty(self):
        """Test that empty strings aren't added to history."""
        input_widget = RichCommandInput()
        input_widget.add_to_history("")
        input_widget.add_to_history("   ")
        assert len(input_widget.history) == 0

    def test_clear_history(self):
        """Test clearing history."""
        input_widget = RichCommandInput()
        input_widget.add_to_history("eval")
        input_widget.clear_history()
        assert len(input_widget.history) == 0

    def test_max_history(self):
        """Test max history limit."""
        input_widget = RichCommandInput(max_history=3)
        for i in range(5):
            input_widget.add_to_history(f"cmd{i}")
        assert len(input_widget.history) == 3
        assert input_widget.history[0] == "cmd2"

    def test_vim_mode_default_off(self):
        """Test vim mode is off by default."""
        input_widget = RichCommandInput()
        assert input_widget.vim_mode is False

    def test_toggle_vim_mode(self):
        """Test toggling vim mode."""
        input_widget = RichCommandInput()
        input_widget.toggle_vim_mode()
        assert input_widget.vim_mode is True
        input_widget.toggle_vim_mode()
        assert input_widget.vim_mode is False

    def test_set_commands(self):
        """Test setting commands."""
        input_widget = RichCommandInput()
        commands = [
            Command(name="eval", description="Run evaluation"),
        ]
        input_widget.set_commands(commands)
        assert input_widget.commands == commands

    def test_add_command(self):
        """Test adding a command."""
        input_widget = RichCommandInput()
        cmd = Command(name="eval", description="Run evaluation")
        input_widget.add_command(cmd)
        assert len(input_widget.commands) == 1
        assert input_widget.commands[0] == cmd

    def test_get_command_by_name(self):
        """Test getting command by name."""
        commands = [
            Command(name="eval", description="Run evaluation"),
        ]
        input_widget = RichCommandInput(commands=commands)
        cmd = input_widget.get_command_by_name("eval")
        assert cmd is not None
        assert cmd.name == "eval"

    def test_get_suggestions(self):
        """Test getting suggestions."""
        commands = [
            Command(name="eval", description="Run evaluation"),
            Command(name="audit", description="Check config"),
        ]
        input_widget = RichCommandInput(commands=commands)
        suggestions = input_widget.get_suggestions("ev")
        assert len(suggestions) == 1
        assert suggestions[0].name == "eval"
