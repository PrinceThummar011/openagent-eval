"""Main Textual App for OpenAgent Eval TUI dashboard."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.theme import Theme

from openagent_eval.ui.screens import (
    AuditScreen,
    DiagnoseScreen,
    EvaluateScreen,
    HelpScreen,
    MainDashboard,
)


class OAEvalDashboard(App):
    """Interactive evaluation dashboard for OpenAgent Eval.

    Launch with `oaeval ui` to explore evaluations, audit corpora,
    and diagnose component failures interactively.
    """

    TITLE = "OpenAgent Eval"
    SUB_TITLE = "RAG Evaluation Framework"

    CSS_PATH = str(Path(__file__).parent / "styles.tcss")

    # Custom theme for the dashboard
    THEME = "dark"

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("f1", "show_help", "Help"),
        ("1", "show_dashboard", "Dashboard"),
        ("2", "show_evaluate", "Evaluate"),
        ("3", "show_audit", "Audit"),
        ("4", "show_diagnose", "Diagnose"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]

    def __init__(self, config_path: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.config_path = config_path

    def compose(self) -> ComposeResult:
        """Compose the app's widget tree."""
        yield MainDashboard()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Register all screens
        self.register_screen("main", MainDashboard())
        self.register_screen("evaluate", EvaluateScreen())
        self.register_screen("audit", AuditScreen())
        self.register_screen("diagnose", DiagnoseScreen())
        self.register_screen("help", HelpScreen())

        # Show main dashboard
        self.push_screen("main")

    def action_show_help(self) -> None:
        """Show help screen."""
        self.push_screen("help")

    def action_show_dashboard(self) -> None:
        """Show main dashboard."""
        self.push_screen("main")

    def action_show_evaluate(self) -> None:
        """Show evaluate screen."""
        self.push_screen("evaluate")

    def action_show_audit(self) -> None:
        """Show audit screen."""
        self.push_screen("audit")

    def action_show_diagnose(self) -> None:
        """Show diagnose screen."""
        self.push_screen("diagnose")

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark


def run_ui(config_path: str | None = None) -> None:
    """Launch the TUI dashboard.

    Args:
        config_path: Optional path to configuration file.
    """
    # Check if textual is installed
    try:
        import textual  # noqa: F401
    except ImportError:
        from rich.console import Console

        console = Console(stderr=True)
        console.print(
            "[red]Error:[/red] Textual is required for the TUI dashboard.\n"
            "Install it with: [bold]pip install openagent-eval[ui][/bold]"
        )
        raise SystemExit(1)

    app = OAEvalDashboard(config_path=config_path)
    app.run()
