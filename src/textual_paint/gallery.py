"""ANSI art gallery TUI"""

import argparse
import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import HorizontalScroll, ScrollableContainer
from textual.widgets import Footer, Header, Static

from .__init__ import __version__
from .auto_restart import restart_on_changes, restart_program
from .paint import AnsiArtDocument

parser = argparse.ArgumentParser(description='ANSI art gallery', usage='%(prog)s [folder]', prog="python -m src.textual_paint.gallery")
parser.add_argument('folder', nargs='?', default=None, help='Path to a folder containing ANSI art.')

dev_options = parser.add_argument_group('development options')
dev_options.add_argument('--inspect-layout', action='store_true', help='Enables DOM inspector (F12) and middle click highlight')
dev_options.add_argument('--restart-on-changes', action='store_true', help='Restart the app when the source code is changed')

args = parser.parse_args()

def _(text: str) -> str:
    """Placeholder for localization function."""
    return text

class GalleryItem(ScrollableContainer):
    """An image with a caption."""

    def __init__(self, image: AnsiArtDocument, caption: str):
        """Initialise the gallery item."""
        super().__init__()
        self.image = image
        self.caption = caption

    def compose(self) -> ComposeResult:
        """Add widgets to the layout."""
        text = self.image.get_renderable()
        text.no_wrap = True
        yield Static(text, classes="image")
        yield Static(self.caption, classes="caption")

class GalleryApp(App[None]):
    """ANSI art gallery TUI"""

    TITLE = "ANSI art gallery"

    CSS_PATH = "gallery.css"

    BINDINGS = [
        Binding("ctrl+q", "quit", _("Quit"), priority=True),
        Binding("ctrl+d", "toggle_dark", _("Toggle Dark Mode")),
        Binding("left,pageup", "previous", _("Previous"), priority=True),
        Binding("right,pagedown", "next", _("Next"), priority=True),
        Binding("home", "scroll_to_start", _("First"), priority=True, show=False),
        Binding("end", "scroll_to_end", _("Last"), priority=True, show=False),
        # dev helper
        # f5 would be more traditional, but I need something not bound to anything
        # in the context of the terminal in VS Code, and not used by this app, like Ctrl+R, and detectable in the terminal.
        # This shouldn't be important now that I have automatic reloading,
        # but I still use it regularly, since restart_program isn't working!
        Binding("f2", "reload", _("Reload"), show=False),
        # Dev tool to inspect the widget tree.
        Binding("f12", "toggle_inspector", _("Toggle Inspector"), show=False),
    ]

    def compose(self) -> ComposeResult:
        """Add widgets to the layout."""
        yield Header(show_clock=True)

        self.scroll = HorizontalScroll()
        yield self.scroll

        yield Footer()

        if not args.inspect_layout:
            return
        # importing the inspector adds instrumentation which can slow down startup
        from .inspector import Inspector
        inspector = Inspector()
        inspector.display = False
        yield inspector


    def on_mount(self) -> None:
        """Called when the app is mounted to the DOM."""
        self._load()

    def _load(self) -> None:
        """Load the folder specified on the command line."""
        if args.folder is None:
            gallery_folder = Path(os.path.dirname(__file__), "../../samples")
        else:
            gallery_folder = Path(args.folder)

        if not gallery_folder.exists():
            self.exit(None, f"Folder not found: {gallery_folder}")

        if not gallery_folder.is_dir():
            self.exit(None, f"Not a folder: {gallery_folder}")

        exts = (".ans", ".txt")

        for path in gallery_folder.rglob("**/*"):
            if path.suffix not in exts:
                continue
            # with open(path, "r", encoding="cp437") as f:
            with open(path, "r", encoding="utf8") as f:
                image = AnsiArtDocument.from_ansi(f.read())
            
            self.scroll.mount(GalleryItem(image, caption=path.name))
        
        if len(self.scroll.children) == 0:
            self.exit(None, f"No ANSI art ({', '.join(f'*{ext}' for ext in exts)}) found in folder: {gallery_folder}")

    def _scroll_to_adjacent_item(self, delta_index: int = 0) -> None:
        """Scroll to the next/previous item."""
        # try:
        #     index = self.scroll.children.index(self.app.focused)
        # except ValueError:
        #     return
        widget, _ = self.app.get_widget_at(self.screen.region.width // 2, self.screen.region.height // 2)
        while widget is not None and not isinstance(widget, GalleryItem):
            widget = widget.parent
        if widget is None:
            index = 0
        else:
            index = self.scroll.children.index(widget)
        index += delta_index
        index = max(0, min(index, len(self.scroll.children) - 1))
        target = self.scroll.children[index]
        target.focus()
        self.scroll.scroll_to_widget(target)

    def action_next(self) -> None:
        """Scroll to the next item."""
        self._scroll_to_adjacent_item(1)

    def action_previous(self) -> None:
        """Scroll to the previous item."""
        self._scroll_to_adjacent_item(-1)

    def action_scroll_to_start(self) -> None:
        """Scroll to the first item."""
        self.scroll.scroll_to_widget(self.scroll.children[0])

    def action_scroll_to_end(self) -> None:
        """Scroll to the last item."""
        self.scroll.scroll_to_widget(self.scroll.children[-1])

    def action_reload(self) -> None:
        """Reload the program."""
        restart_program()

    def action_toggle_inspector(self) -> None:
        if not args.inspect_layout:
            return
        # importing the inspector adds instrumentation which can slow down startup
        from .inspector import Inspector
        inspector = self.query_one(Inspector)
        inspector.display = not inspector.display
        if not inspector.display:
            inspector.picking = False


app = GalleryApp()

if args.restart_on_changes:
    restart_on_changes(app)

if __name__ == "__main__":
    app.run()
