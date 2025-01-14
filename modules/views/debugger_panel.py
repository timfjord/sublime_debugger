from __future__ import annotations
from ..typecheck import *

from ..import ui
from ..import dap
from . import css

from .input_list_view import InputListView

if TYPE_CHECKING:
	from ..debugger import Debugger


class DebuggerPanel(ui.div):
	def __init__(self, debugger: 'Debugger', breakpoints: ui.div) -> None:
		super().__init__()
		self.debugger = debugger
		self.breakpoints = breakpoints
		self.debugger.sessions.updated.add(lambda session, state: self.dirty())
		self.debugger.sessions.on_selected.add(self.on_selected_session)
		self.debugger.sessions.on_added_session.add(self.on_selected_session)
		self.last_active_adapter = None

	def on_selected_session(self, session: dap.Session):
		self.last_active_adapter = session.adapter_configuration
		self.dirty()

	def render(self) -> ui.div.Children:
		buttons = [] #type: list[ui.span]

		items = [
			DebuggerCommandButton(self.debugger.on_settings, ui.Images.shared.settings, 'Settings'),
			DebuggerCommandButton(self.debugger.on_play, ui.Images.shared.play, 'Start'),
		]


		if self.debugger.is_stoppable():
			items.append(DebuggerCommandButton(self.debugger.on_stop, ui.Images.shared.stop, 'Stop'))
		else:
			items.append(DebuggerCommandButton(self.debugger.on_stop, ui.Images.shared.stop_disable, 'Stop (Disabled)'))

		if self.debugger.is_running():
			items.append(DebuggerCommandButton(self.debugger.on_pause, ui.Images.shared.pause, 'Pause'))
		elif self.debugger.is_paused():
			items.append(DebuggerCommandButton(self.debugger.on_resume, ui.Images.shared.resume, 'Continue'))
		else:
			items.append(DebuggerCommandButton(self.debugger.on_pause, ui.Images.shared.pause_disable, 'Pause (Disabled)'))

		if self.debugger.is_paused():
			items.extend([
				DebuggerCommandButton(self.debugger.on_step_over, ui.Images.shared.down, 'Step Over'),
				DebuggerCommandButton(self.debugger.on_step_out, ui.Images.shared.left, 'Step Out'),
				DebuggerCommandButton(self.debugger.on_step_in, ui.Images.shared.right, 'Step In'),
			])
		else:
			items.extend([
				DebuggerCommandButton(self.debugger.on_step_over, ui.Images.shared.down_disable, 'Step Over (Disabled)'),
				DebuggerCommandButton(self.debugger.on_step_out, ui.Images.shared.left_disable, 'Step Out (Disabled)'),
				DebuggerCommandButton(self.debugger.on_step_in, ui.Images.shared.right_disable, 'Step In (Disabled)'),
			])

		# looks like
		# current status
		# breakpoints ...

		if self.debugger.sessions.has_active:
			self.last_active_adapter = self.debugger.sessions.active.adapter_configuration or self.last_active_adapter

		panel_items = []
		if self.debugger.sessions.has_active:
			session = self.debugger.sessions.active
			status = session.status
			if status:
				panel_items.append(ui.div(height=css.row_height)[
					ui.text(status, css=css.label_secondary)
				])

		if self.last_active_adapter:
			settings = self.last_active_adapter.settings(self.debugger.sessions)
			for setting in settings:
				panel_items.append(InputListView(setting))

			div = self.last_active_adapter.ui(self.debugger.sessions)
			if div: panel_items.append(div)


		panel_items.append(self.breakpoints)

		return [
			ui.div()[
				ui.div(height=css.header_height)[items],
				ui.div(width=27, height=1000, css=css.rounded_panel)[
					panel_items
				],
			]
		]


class DebuggerCommandButton (ui.span):
	def __init__(self, callback: Callable[[], None], image: ui.Image, title: str) -> None:
		super().__init__()

		self.image = image
		self.callback = callback
		self.title = title

	def render(self) -> ui.span.Children:
		return [
			ui.span(css=css.padding)[
				ui.click(self.callback, title=self.title)[
					ui.icon(self.image),
				]
			]
		]
