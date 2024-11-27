import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
def create_image_gallery(root, folder):
    image_list = []
    time_stamps = []

    for im_path in os.listdir(folder):
        fin_path = os.path.join(folder, im_path)
        time_stamps.append(fin_path.strip(".jpeg"))
        image = ImageTk.PhotoImage(Image.open(fin_path).resize((950, 650)))
        image_list.append(image)

    image1 = image_list[0]
    first_stamp = time_stamps[0]
    counter = 1

    my_label = tk.Label(root, image=image1)
    my_label.grid(row=0, column=0, columnspan=3, pady=8, padx=12, sticky='nsew')

    time_stamp_label = tk.Label(root, text=first_stamp, font=("Helvetica", 20), bg="black", fg="white")
    time_stamp_label.grid(row=1, column=0, columnspan=3, pady=10, padx=10, sticky='nsew')

    infoLabel = tk.Label(root, text="Image " + str(counter) + " of " +  str(len(image_list)), font = ("Helvetica", 20), bg="blue", fg="white")
    infoLabel.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky='nsew')

    def see_next(image_number):
        nonlocal counter, my_label, infoLabel
        if counter == len(image_list):
            counter -= 1
        counter += 1
        my_label.config(image=image_list[counter - 1])
        time_stamp_label.config(text=time_stamps[counter - 1])
        infoLabel.config(text="Image " + str(counter) + " of " + str(len(image_list)), bg="blue", fg="white")
    def see_previous(image_number):
        nonlocal counter, my_label, infoLabel
        if counter == 1:
            counter += 1
        counter -= 1
        my_label.config(image=image_list[counter - 1])
        time_stamp_label.config(text=time_stamps[counter - 1])
        infoLabel.config(text="Image " + str(counter) + " of " + str(len(image_list)), bg="blue", fg="white")

    button_back = tk.Button(root, text="See previous image", command=lambda: see_previous(counter))
    button_back.grid(row=2, column=0, pady=10, padx=10)

    button_exit = tk.Button(root, text="Exit Program", command=root.quit)
    button_exit.grid(row=2, column=1, pady=10, padx=10)

    button_forward = tk.Button(root, text="See next image", command=lambda: see_next(counter))
    button_forward.grid(row=2, column=2, pady=10, padx=10)

    if len(image_list) == 1:
        button_forward.config(state=tk.DISABLED)
        button_back.config(state=tk.DISABLED)
def select_tab(index):
    """Hides all tab frames and shows the selected one."""
    for tab in notebook_tabs:
        tab.pack_forget()
    notebook_tabs[index].pack(expand=True, fill='both')
# Main function
def main():
    global notebook_tabs
    root = tk.Tk()
    root.title("Crowdhydrology Image Gallery")
    root.state('zoomed')
    root.geometry("800x600")
    root.iconbitmap("crowd-hydroicon.png")
    folder_list = []
    restricted = [".idea", ".venv", ".git", "coco.names", "crowd-hydroicon.png", "cvdetectorv3.py", "dropdown2.py", "face_detection.jpg", "test_newdrop.py", "testfil.py", "yolov4.cfg", "yolov4.weights", "__pycache__", "store_tokens.py", "dropdownv4.py", "has_people.zip"]
    parent = r"C:\Users\faraz\PycharmProjects\testIDE"
    for folder in os.listdir(parent):
        if folder in restricted or not os.listdir(folder) or len(folder) > 100:
            continue
        else:
            folder_list.append(folder)

    notebook_tabs = []

    # Create a main frame to hold the left menu and the main content area
    main_frame = ttk.Frame(root)
    main_frame.pack(expand=True, fill='both')

    # Create a frame for the scrollable list of tabs on the left side
    left_frame = ttk.Frame(main_frame, width=100)
    left_frame.pack(side=tk.LEFT, fill=tk.Y)

    # Scrollable list of folder names
    tab_list_canvas = tk.Canvas(left_frame)
    tab_list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=tab_list_canvas.yview)
    scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    tab_list_canvas.configure(yscrollcommand=scrollbar.set)
    tab_list_canvas.bind('<Configure>', lambda e: tab_list_canvas.configure(scrollregion=tab_list_canvas.bbox('all')))
    tab_list_canvas.bind_all('<MouseWheel>', lambda event: tab_list_canvas.yview_scroll(-int(event.delta / 60), "units"))
    tab_list_frame = ttk.Frame(tab_list_canvas)
    tab_list_canvas.create_window((0, 0), window=tab_list_frame, anchor='nw')

    # Create the right frame for displaying the content
    content_frame = ttk.Frame(main_frame)
    content_frame.pack(side=tk.RIGHT, expand=True, fill='both')

    # Create individual frames for each tab content
    for index, folder in enumerate(folder_list):
        tab_frame = ttk.Frame(content_frame)
        notebook_tabs.append(tab_frame)
        create_image_gallery(tab_frame, folder)
        press = ttk.Button(tab_list_frame, text=folder, command=lambda i=index: select_tab(i))
        press.pack(fill=tk.X, pady=2)

    first_tab = notebook_tabs[0]
    first_tab.pack(expand=True, fill='both')

    root.mainloop()
main()