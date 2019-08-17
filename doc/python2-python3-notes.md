# Modify to support Python 3

```
print "text"  new and old: print("text")
<>   new and old: !=
''.join(sound)  new:  b''.join(sound)    The b is mandatory now

Delete:
 from Tkinter import *
 from tkFileDialog import askopenfilename
 from tkFileDialog import asksaveasfilename 
 from tkSimpleDialog import askstring
 from tkMessageBox import *
And replace it by:
 from tkinter import *
 from tkinter import messagebox
 from tkinter import filedialog
 from tkinter import simpledialog
 from tkinter import font

tkFont.Font()  new:  font.Font()
showwarning()  new:  messagebox.showwarning()
showerror()   new:  messagebox.showerror()
showinfo()  new:  messagebox.showinfo()
askyesno()  new:  messagebox.askyesno() and new syntax!!! YES = "yes", NO = "no", OK = "ok"
askopenfilename()  new:  filedialog.askopenfilename()
asksaveasfilename()  new:  filedialog.asksaveasfilename()
askstring()  new:  simpledialog.askstring()
```