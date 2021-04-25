import tkinter as tk

window = tk.Tk()
#greeting = tk.Label(text="Hello, Tkinter" , background="#34A2FE")
button = tk.Button(
    text="Click me!",
    width=25,
    height=5,
    bg="blue",
    fg="yellow",
)

button.pack()
window.mainloop()