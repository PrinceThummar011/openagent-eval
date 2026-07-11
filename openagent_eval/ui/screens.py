"""Dashboard screens for OpenAgent Eval TUI."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, Rule, Static

from openagent_eval.ui.widgets import (
    BannerWidget,
    InfoPanel,
    MetricsSummaryWidget,
    ProgressWidget,
    QuickActions,
    ResultsTableWidget,
    StatusWidget,
)


class MainDashboard(Screen):
    """Main dashboard screen with overview."""

    DEFAULT_CSS = """
    MainDashboard {
        layout: vertical;
    }

    MainDashboard #top-section {
        height: auto;
        padding: 0 1;
    }

    MainDashboard #middle-section {
        height: 1fr;
        padding: 0 1;
    }

    MainDashboard #bottom-section {
        height: auto;
        padding: 0 1;
    }

    MainDashboard .grid {
        height: 1fr;
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1 2;
    }

    MainDashboard .metrics-grid {
        height: auto;
        layout: grid;
        grid-size: 2 1;
        grid-gutter: 1 2;
    }
    """

    BINDINGS = [
        ("1", "run_evaluation", "Run Eval"),
        ("2", "audit_corpus", "Audit"),
        ("3", "diagnose", "Diagnose"),
        ("q", "quit", "Quit"),
        ("h", "help", "Help"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        # Top section: Banner + Status
        with Vertical(id="top-section"):
            yield BannerWidget()
            yield StatusWidget(id="status")
            yield Rule()

        # Middle section: Main content grid
        with Vertical(id="middle-section"):
            with Horizontal(classes="metrics-grid"):
                yield MetricsSummaryWidget(
                    title="Retrieval Metrics",
                    id="retrieval-metrics"
                )
                yield MetricsSummaryWidget(
                    title="Generation Metrics",
                    id="generation-metrics"
                )

            with Horizontal(classes="grid"):
                yield ResultsTableWidget(
                    title="Recent Commands",
                    columns=["Command", "Status", "Duration", "Last Run"],
                    id="recent-table"
                )
                yield QuickActions(id="quick-actions")

        # Bottom section: Progress
        with Vertical(id="bottom-section"):
            yield ProgressWidget(label="Overall Progress", id="progress")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the dashboard on mount."""
        status = self.query_one("#status", StatusWidget)
        status.set_complete("Dashboard loaded")

        # Populate recent commands table
        table_widget = self.query_one("#recent-table", ResultsTableWidget)
        table_widget.add_row("run", "[bold]Idle[/bold]", "-", "-")
        table_widget.add_row("audit", "[bold]Idle[/bold]", "-", "-")
        table_widget.add_row("diagnose", "[bold]Idle[/bold]", "-", "-")

    def action_run_evaluation(self) -> None:
        """Switch to evaluation screen."""
        self.app.push_screen(EvaluateScreen())

    def action_audit_corpus(self) -> None:
        """Switch to audit screen."""
        self.app.push_screen(AuditScreen())

    def action_diagnose(self) -> None:
        """Switch to diagnose screen."""
        self.app.push_screen(DiagnoseScreen())

    def action_help(self) -> None:
        """Show help screen."""
        self.app.push_screen(HelpScreen())


class EvaluateScreen(Screen):
    """Evaluation screen for running RAG evaluations."""

    DEFAULT_CSS = """
    EvaluateScreen {
        layout: vertical;
        padding: 1;
    }

    EvaluateScreen #screen-header {
        height: auto;
        padding: 0 1;
    }

    EvaluateScreen #config-section {
        height: 8;
        padding: 1;
        border: solid $primary;
        background: $surface;
    }

    EvaluateScreen #results-section {
        height: 1fr;
        padding: 1;
        border: solid $secondary;
        background: $surface;
    }

    EvaluateScreen #progress-section {
        height: auto;
        padding: 1;
    }

    EvaluateScreen .config-grid {
        height: auto;
        layout: grid;
        grid-size: 3 1;
        grid-gutter: 1 2;
    }

    EvaluateScreen .config-item {
        height: 1;
    }
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("r", "run_eval", "Run"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        # Screen header
        with Vertical(id="screen-header"):
            yield Static("[bold]Evaluation Runner[/bold]")
            yield Rule()

        # Configuration panel
        with Vertical(id="config-section"):
            yield Static("[bold]Configuration[/bold]")
            yield Rule()
            with Horizontal(classes="config-grid"):
                yield Label("[dim]Config:[/dim] [bold]config.yaml[/bold]", classes="config-item")
                yield Label("[dim]Metrics:[/dim] [bold]faithfulness, relevancy[/bold]", classes="config-item")
                yield Label("[dim]Provider:[/dim] [bold]openai[/bold]", classes="config-item")

        # Results section
        with Vertical(id="results-section"):
            yield ResultsTableWidget(
                title="Evaluation Results",
                columns=["Metric", "Score", "Status", "Details"],
                id="eval-results"
            )

        # Progress section
        with Vertical(id="progress-section"):
            yield ProgressWidget(label="Evaluation Progress", total=100, id="eval-progress")

        yield Footer()

    def action_go_back(self) -> None:
        """Go back to main dashboard."""
        self.app.pop_screen()

    def action_run_eval(self) -> None:
        """Trigger evaluation run."""
        progress = self.query_one("#eval-progress", ProgressWidget)
        progress.update_progress(50)


class AuditScreen(Screen):
    """Corpus audit screen."""

    DEFAULT_CSS = """
    AuditScreen {
        layout: vertical;
        padding: 1;
    }

    AuditScreen #screen-header {
        height: auto;
        padding: 0 1;
    }

    AuditScreen #audit-config {
        height: 8;
        padding: 1;
        border: solid $primary;
        background: $surface;
    }

    AuditScreen #audit-results {
        height: 1fr;
        padding: 1;
        border: solid $secondary;
        background: $surface;
    }

    AuditScreen #audit-summary {
        height: auto;
        padding: 1;
    }

    AuditScreen .config-grid {
        height: auto;
        layout: grid;
        grid-size: 2 1;
        grid-gutter: 1 2;
    }

    AuditScreen .config-item {
        height: 1;
    }
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("r", "run_audit", "Run Audit"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        # Screen header
        with Vertical(id="screen-header"):
            yield Static("[bold]Corpus Health Audit[/bold]")
            yield Rule()

        # Configuration panel
        with Vertical(id="audit-config"):
            yield Static("[bold]Audit Configuration[/bold]")
            yield Rule()
            with Horizontal(classes="config-grid"):
                yield Label("[dim]Corpus:[/dim] [bold]./knowledge_base/[/bold]", classes="config-item")
                yield Label("[dim]Checks:[/dim] [bold]contradiction, staleness, duplicate, coverage[/bold]", classes="config-item")

        # Results section
        with Vertical(id="audit-results"):
            yield ResultsTableWidget(
                title="Audit Results",
                columns=["Issue Type", "Count", "Severity", "Status"],
                id="audit-table"
            )

        # Summary section
        with Vertical(id="audit-summary"):
            yield MetricsSummaryWidget(
                title="Health Score",
                id="health-score"
            )

        yield Footer()

    def action_go_back(self) -> None:
        """Go back to main dashboard."""
        self.app.pop_screen()

    def action_run_audit(self) -> None:
        """Trigger corpus audit."""
        table = self.query_one("#audit-table", ResultsTableWidget)
        table.clear_rows()
        table.add_row("contradiction", "0", "[bold]None[/bold]", "[bold]OK[/bold]")
        table.add_row("staleness", "0", "[bold]None[/bold]", "[bold]OK[/bold]")
        table.add_row("duplicate", "0", "[bold]None[/bold]", "[bold]OK[/bold]")
        table.add_row("coverage_gap", "0", "[bold]None[/bold]", "[bold]OK[/bold]")


class DiagnoseScreen(Screen):
    """Component diagnosis screen."""

    DEFAULT_CSS = """
    DiagnoseScreen {
        layout: vertical;
        padding: 1;
    }

    DiagnoseScreen #screen-header {
        height: auto;
        padding: 0 1;
    }

    DiagnoseScreen #diag-config {
        height: 8;
        padding: 1;
        border: solid $primary;
        background: $surface;
    }

    DiagnoseScreen #diag-results {
        height: 1fr;
        padding: 1;
        border: solid $secondary;
        background: $surface;
    }

    DiagnoseScreen #diag-summary {
        height: auto;
        padding: 1;
    }

    DiagnoseScreen .config-grid {
        height: auto;
        layout: grid;
        grid-size: 3 1;
        grid-gutter: 1 2;
    }

    DiagnoseScreen .config-item {
        height: 1;
    }
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("r", "run_diagnose", "Run Diagnosis"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        # Screen header
        with Vertical(id="screen-header"):
            yield Static("[bold]Component Diagnosis[/bold]")
            yield Rule()

        # Configuration panel
        with Vertical(id="diag-config"):
            yield Static("[bold]Diagnosis Configuration[/bold]")
            yield Rule()
            with Horizontal(classes="config-grid"):
                yield Label("[dim]Report:[/dim] [bold]reports/latest.json[/bold]", classes="config-item")
                yield Label("[dim]Threshold:[/dim] [bold]0.5[/bold]", classes="config-item")
                yield Label("[dim]Mode:[/dim] [bold]blame_attribution[/bold]", classes="config-item")

        # Results section
        with Vertical(id="diag-results"):
            yield ResultsTableWidget(
                title="Blame Attribution",
                columns=["Component", "Blame %", "Confidence", "Recommendation"],
                id="blame-table"
            )

        # Summary section
        with Vertical(id="diag-summary"):
            yield ProgressWidget(label="Diagnosis Progress", id="diag-progress")

        yield Footer()

    def action_go_back(self) -> None:
        """Go back to main dashboard."""
        self.app.pop_screen()

    def action_run_diagnose(self) -> None:
        """Trigger diagnosis."""
        table = self.query_one("#blame-table", ResultsTableWidget)
        table.clear_rows()
        table.add_row("retrieval", "0%", "[dim]-[/dim]", "[dim]-[/dim]")
        table.add_row("generation", "0%", "[dim]-[/dim]", "[dim]-[/dim]")
        table.add_row("chunking", "0%", "[dim]-[/dim]", "[dim]-[/dim]")


class HelpScreen(Screen):
    """Help screen with keyboard shortcuts."""

    DEFAULT_CSS = """
    HelpScreen {
        layout: vertical;
        padding: 2;
        align: center middle;
    }

    HelpScreen #help-content {
        width: 60;
        height: auto;
        padding: 2;
        border: solid $primary;
        background: $surface;
    }

    HelpScreen .section-title {
        text-style: bold;
        padding-bottom: 1;
    }

    HelpScreen .shortcut-row {
        height: 1;
        padding: 0 2;
    }

    HelpScreen .divider {
        height: 1;
    }
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("q", "go_back", "Close"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical(id="help-content"):
            yield Static("[bold]OpenAgent Eval TUI - Keyboard Shortcuts[/bold]", classes="section-title")
            yield Rule()

            yield Static("[bold]Global[/bold]", classes="section-title")
            yield Label("  [bold]q[/bold] / [bold]ctrl+c[/bold]    Quit the application", classes="shortcut-row")
            yield Label("  [bold]escape[/bold]         Go back / Close screen", classes="shortcut-row")
            yield Label("  [bold]h[/bold]              Show this help", classes="shortcut-row")
            yield Rule(classes="divider")

            yield Static("[bold]Main Dashboard[/bold]", classes="section-title")
            yield Label("  [bold]1[/bold]              Run Evaluation", classes="shortcut-row")
            yield Label("  [bold]2[/bold]              Audit Corpus", classes="shortcut-row")
            yield Label("  [bold]3[/bold]              Diagnose", classes="shortcut-row")
            yield Rule(classes="divider")

            yield Static("[bold]Evaluate Screen[/bold]", classes="section-title")
            yield Label("  [bold]r[/bold]              Run evaluation", classes="shortcut-row")
            yield Label("  [bold]escape[/bold]         Back to dashboard", classes="shortcut-row")
            yield Rule(classes="divider")

            yield Static("[bold]Audit Screen[/bold]", classes="section-title")
            yield Label("  [bold]r[/bold]              Run audit", classes="shortcut-row")
            yield Label("  [bold]escape[/bold]         Back to dashboard", classes="shortcut-row")
            yield Rule(classes="divider")

            yield Static("[bold]Diagnose Screen[/bold]", classes="section-title")
            yield Label("  [bold]r[/bold]              Run diagnosis", classes="shortcut-row")
            yield Label("  [bold]escape[/bold]         Back to dashboard", classes="shortcut-row")
            yield Rule(classes="divider")

            yield Label("[dim]Press escape or q to close this help[/dim]")

        yield Footer()

    def action_go_back(self) -> None:
        """Go back to main dashboard."""
        self.app.pop_screen()
