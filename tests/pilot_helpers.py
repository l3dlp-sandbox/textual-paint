"""Helper functions for Textual's app automation class, Pilot.

Ideally this functionality would be part of Pilot.
"""

from typing import Any

from textual.events import MouseDown, MouseMove, MouseUp
from textual.geometry import Offset
from textual.pilot import Pilot, _get_mouse_message_arguments
from textual.widget import Widget


async def click_widget(pilot: Pilot[Any], widget: Widget, shift: bool = False, meta: bool = False, control: bool = False) -> None:
    """Click on widget, by reference."""
    widget.add_class("pilot-click-target")
    await pilot.click(".pilot-click-target", shift=shift, meta=meta, control=control)
    widget.remove_class("pilot-click-target")


async def click_by_index(pilot: Pilot[Any], selector: str, index: int, shift: bool = False, meta: bool = False, control: bool = False) -> None:
    """Click on widget, query disambiguated by index"""
    # await pilot.pause(0.5)
    widget = pilot.app.query(selector)[index]
    await click_widget(pilot, widget, shift=shift, meta=meta, control=control)


async def drag(pilot: Pilot[Any], selector: str, offsets: list[Offset], shift: bool = False, meta: bool = False, control: bool = False) -> None:
    """Drag across the given points."""
    # await pilot.pause(0.5)
    target_widget = pilot.app.query(selector)[0]
    offset = offsets[0]
    message_arguments = _get_mouse_message_arguments(
        target_widget, offset, button=1, shift=shift, meta=meta, control=control
    )
    pilot.app.post_message(MouseDown(**message_arguments))
    await pilot.pause(0.1)
    for offset in offsets[1:]:
        message_arguments = _get_mouse_message_arguments(
            target_widget, offset, button=1, shift=shift, meta=meta, control=control
        )
        pilot.app.post_message(MouseMove(**message_arguments))
        await pilot.pause()
    pilot.app.post_message(MouseUp(**message_arguments))
    await pilot.pause(0.1)
    # pilot.app.post_message(Click(**message_arguments))
    # await pilot.pause(0.1)