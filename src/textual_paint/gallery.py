"""ANSI art gallery TUI"""

import argparse
import os

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import HorizontalScroll, Vertical
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

class GalleryItem(Vertical):
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

    TITLE = f"ANSI art gallery v{__version__}"

    CSS_PATH = "gallery.css"

    BINDINGS = [
        Binding("ctrl+q", "exit", _("Quit")),
        # dev helper
        # f5 would be more traditional, but I need something not bound to anything
        # in the context of the terminal in VS Code, and not used by this app, like Ctrl+R, and detectable in the terminal.
        # This isn't as important now that I have automatic reloading,
        # but I still use it regularly.
        Binding("f2", "reload", _("Reload")),
        # Temporary quick access to work on a specific dialog.
        # Can be used together with `--press f3` when using `textual run` to open the dialog at startup.
        # Would be better if all dialogs were accessible from the keyboard.
        # Binding("f3", "custom_zoom", _("Custom Zoom")),
        # Dev tool to inspect the widget tree.
        Binding("f12", "toggle_inspector", _("Toggle Inspector")),
        # Update screenshot on readme.
        # Binding("ctrl+j", "update_screenshot", _("Update Screenshot")),
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
        folder = args.folder
        if folder is None:
            folder = os.path.join(os.path.dirname(__file__), "../../samples")
        if not os.path.isdir(folder):
            raise Exception(f"Folder not found: {folder}")

        for filename in os.listdir(folder):
            if not filename.endswith(".ans"):
                continue
            path = os.path.join(folder, filename)
            # with open(path, "r", encoding="cp437") as f:
            with open(path, "r", encoding="utf8") as f:
                image = AnsiArtDocument.from_ansi(f.read())
            
            self.scroll.mount(GalleryItem(image, caption=filename))

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
