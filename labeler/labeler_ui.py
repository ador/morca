from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

from labeler_helper import word_pos_finder


# create the main window
root = Tk()
root.title("Gimme Labels!")	
root.geometry("930x300")


class MyMenu:
    def __init__(self, root_element):
        self.main_menu = Menu(root_element)
        self.file_menu = Menu(self.main_menu)
        self.file_menu.add_command(label="Open...(todo)", command=self.open)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Open next (todo)", command=self.open_next)
        self.main_menu.add_cascade(
            label="File", menu=self.file_menu)

        self.edit_menu = Menu(self.main_menu)
        self.main_menu.add_cascade(
            label="Edit", menu=self.edit_menu
        )
        root_element.config(menu=self.main_menu)

    def open(self):
        print("OPEN...")

    def open_next(self):
        print("open next")



class Labeler:
    def __init__(self, root_element):
        self.frame = Frame(root_element)
        # TODO image path should come from clicking "Open" menu item
        in_img_file_path = "../test_data/20191004-211826_L7.png"
        # we need a PIL image object for char detection
        self.line_img = Image.open(in_img_file_path)
        # and a PhotoImage object to show on GUI
        self.ph_img = ImageTk.PhotoImage(self.line_img)

        self.img_label = Label(self.frame, image=self.ph_img)
        self.img_label.pack()
        self.img_label.bind("<Button-1>", self.clickhandler)
        # input box to type or paste in the text content of hte line image
        self.entry = Entry(root_element, width=80)
        self.entry.focus_set()
        self.entry.pack()
        self.print_button = Button(
            self.frame, text="Auto-locate letters", command=self.locate_words
        )
        self.print_button.pack()
        self.counter = 0  # just for testing how things work
        self.cnt_label = Label(
            self.frame, text=str(self.counter)
        )
        self.cnt_label.pack()

        self.frame.pack()

    def clickhandler(self, event):
        click_x = event.x
        click_y = event.y
        print("click was at {} {}".format(click_x, click_y))

    def keyhandler(self, event):
        print("key: {}".format(event.char))
        self.counter += 1
        self.cnt_label.config(
            text="Saved train examples: {}".format(self.counter)
        )

    def locate_words(self):
        text_from_entry = self.entry.get().strip()
        words_entered = text_from_entry.split(" ")
        words_xmin_xmax_list, new_img = word_pos_finder(
            self.line_img, underline_in_img=True
        )
        self.line_img = new_img
        self.ph_img = ImageTk.PhotoImage(self.line_img)
        self.img_label.configure(image=self.ph_img)
        self.img_label.image = self.ph_img
        if len(words_xmin_xmax_list) != len(words_entered): 
            mgbox = messagebox.showinfo(
                "Ooops",
                "Something is fishy!\n" +
                "Found words in image: {} vs typed in: {}".format(
                    len(words_xmin_xmax_list), len(words_entered)
                )
            )


my_menu = MyMenu(root)
labeler = Labeler(root)
root.bind("<Key>", labeler.keyhandler)

# After setup: run the gui-evenlistener loop
root.mainloop()


# not used, just code example
def myfunc():
    print("clicked")
    if button1.cget("bg") == "lightblue":
        button1.config(bg="darkblue")
    else:
        button1.config(bg="lightblue")
    new_text = entry.get()
    print("e was {}".format(new_text))
    button1.config(text=new_text)
