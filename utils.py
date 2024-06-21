# used for display
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import RadioList, Label
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import prompt


def promptAsk(text, multiline=True) -> str:

 
    kb = KeyBindings()
    if multiline:
        # type "enter" to add a new line
        @kb.add("enter")
        def _(event):
            event.current_buffer.insert_text("\n")

    # Send the message by pressing Shift + Right Arrow
    @kb.add("s-right")
    def _(event):
        event.current_buffer.validate_and_handle()

    return prompt(
        text,
        multiline=multiline,
        prompt_continuation=_promptContinuation,
        key_bindings=kb,
    )

def _promptContinuation(width, line_number, wrap_count):

   if wrap_count > 0:
        return " " * (width - 3) + "-> "
   text = ("- %i - " % (line_number + 1)).rjust(width)
   return HTML("<strong>%s</strong>") % text



def promptSelect(title="", values=None, style=None, async_=False):
    
    # Add exit key binding.
    bindings = KeyBindings()

    # press Ctrl-d call exit_ and kill the app
    @bindings.add("c-d")
    def exit_(event):
        event.app.exit()
    # Press Shift + Right arrow exit app and send value
    @bindings.add("s-right")
    def exit_with_value(event):
        event.app.exit(result=radio_list.current_value)
    # Instructions
    instructions = """\
    click on [Shift + right arrow] to select you choice
    """
    radio_list = RadioList(values)
    application = Application(
        layout=Layout(HSplit([Label(title + instructions), radio_list])),
        key_bindings=merge_key_bindings([load_key_bindings(), bindings]),
        mouse_support=True,
        style=style,
        full_screen=False,
    )

    return application.run_async() if async_ else application.run()
