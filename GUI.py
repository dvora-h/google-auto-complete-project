import complete
from complete import get_best_k_completions

from tkinter import *
from init import completion_data_struct


class MyApp:
    def __init__(self, tk_root):
        self._root = tk_root
        root.title("Auto Complete")
        self._base_frame = Frame(tk_root)
        self._base_frame.pack(side=TOP)
        self._label = Label(self._base_frame, text="Enter Your Text")
        self._label.pack(side=LEFT)
        self._entry = Entry(self._base_frame)
        self._entry.pack(side=LEFT)
        self._entry.bind("<Return>", self.run)
        self._search = Button(self._base_frame, text='search', command=self.run)
        self._search.pack(side=LEFT)
        self._results = Frame(tk_root)
        self._results.pack(side=BOTTOM)

    def run(self):
        for widget in self._results.winfo_children():
            widget.destroy()
        string_to_complete = self._entry.get()
        if string_to_complete[len(string_to_complete) - 1] != '#':
            best_k = get_best_k_completions(string_to_complete)
            self.print_match_completions(best_k)
            self._entry.icursor(len(string_to_complete))
        else:
            self._entry.delete(0, len(string_to_complete))

    def print_match_completions(self, best_k):
        lb = Listbox(self._results, width=100, height=6)
        for i in range(len(best_k)):
            lb.insert(i,
                      f'* {i} {best_k[i].completed_sentence}. ({best_k[i].source_text}, {best_k[i].offset}, score {best_k[i].score})')
        lb.pack(side=TOP)


root = Tk()
MyApp(root)
root.mainloop()
