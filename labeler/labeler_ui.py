import random

from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageTk

from labeler_helper import locate_chars


# create the main window
root = Tk()
root.title("Gimme Labels!")	
root.geometry("930x300")


CHAR_WIDTH = 14

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
        in_img_file_path = "../line_img/20191004-211826_L9.png"
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
            self.frame, text="Auto-locate letters",
            command=self.auto_locate_chars
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
        self.counter += 1
        self.cnt_label.config(
            text="Saved train examples: {}".format(self.counter)
        )

    def auto_locate_chars(self):
        text_entered = self.entry.get().strip()
        image = self.line_img
        # a list of tuples: (character, x_pos) ias (char, int)
        char_locations = locate_chars(image, text_entered)
        if not char_locations:
            mgbox = messagebox.showinfo(
                "Ooops",
                "Something is fishy!\n" +
                "Found words in image does not match the typed in text!"
        )
        else:
            # update the image shown with the one that locates words
            # first step: draw rectangles on line_img
            draw = ImageDraw.Draw(self.line_img)
            for char_loc in char_locations:
                draw.rectangle(
                    [char_loc[1] - 2, 1 + random.randint(1, 8),  # x0 y0
                    char_loc[1] + CHAR_WIDTH, 39 - random.randint(1, 8)],  #  x1 y1
                )

            # then update the PhotoImage object on hte shwn label:
            self.ph_img = ImageTk.PhotoImage(self.line_img)
            self.img_label.configure(image=self.ph_img)
            self.img_label.image = self.ph_img


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
