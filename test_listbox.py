import tkinter as tk
from tkinter import ttk
root = tk.Tk()
root.geometry("300x200")
frame = ttk.Frame(root)
frame.pack(fill='both', expand=True)
lb = tk.Listbox(frame, height=5)
lb.pack(fill='both', expand=True, side='left')
sb = ttk.Scrollbar(frame, orient='vertical', command=lb.yview)
sb.pack(fill='y', side='right')
lb.config(yscrollcommand=sb.set)
for i in range(10):
    lb.insert('end', f'Item {i}')
lb.selection_set(0)
root.mainloop()