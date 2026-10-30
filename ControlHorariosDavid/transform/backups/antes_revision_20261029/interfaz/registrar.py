import ttkbootstrap as ttkb

class PestanaRegistrar(ttkb.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.columnconfigure(0, weight=1)
