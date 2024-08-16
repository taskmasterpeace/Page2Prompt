import gradio as gr
from gradio.events import Dependency

class HighlightedTextLabelDefault(gr.Textbox):
    def __init__(self, value=None, *args, **kwargs):
        self.default_label = kwargs.pop('default_label', 'highlighted')
        self.color_map = kwargs.pop('color_map', {"highlighted": "yellow"})
        super().__init__(*args, **kwargs)
        self.value = value if value is not None else [("", None)]
        self.interactive = kwargs.get('interactive', True)

    def preprocess(self, x):
        return x

    def postprocess(self, y):
        return y