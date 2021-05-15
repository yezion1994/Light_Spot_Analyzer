from tkinter import filedialog
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import *
from tkinter import ttk
import os
from functions import functions


# WINDOW CREATION
win = tk.Tk()
geo = win.geometry
geo("1500x900")
win['bg'] = 'orange'
win.f1 = tk.Frame()
win.f1.grid(row=0, column=0)
win.f2 = tk.Frame()
win.f2.rowconfigure(0, weight=1)
win.f2.grid(row=1, column=0)
win.f3 = tk.Frame()
win.f3.rowconfigure(0, weight=1)
win.f3.grid(row=0, column=1, rowspan=2)
box = list()
cb = []
folder,fname = [],[]
t = []
    
# draw figure & induce fig toolbar
fig1 = Figure(figsize=(5, 4), dpi=100)
axis1 = fig1.add_subplot(111)
axis11 = fig1.add_subplot(111)
canvas1 = FigureCanvasTkAgg(fig1, master=win.f1)  # A tk.DrawingArea.
canvas1.draw()
canvas1.get_tk_widget().grid(row=0, column=0, pady=0, padx=0, columnspan=2)

frame = tk.Frame(win.f1)
frame.grid(row=1, column=0)
toobar1 = NavigationToolbar2Tk(canvas1, frame)
canvas1.get_tk_widget().grid(row=0, column=0)

fig2 = Figure(figsize=(10, 8), dpi=100)
canvas2 = FigureCanvasTkAgg(fig2, master=win.f3)  # A tk.DrawingArea.
canvas2.draw()
canvas2.get_tk_widget().grid(row=0, column=0, pady=0, padx=0, columnspan=2)

frame = tk.Frame(win.f3)
frame.grid(row=1, column=0)
toobar2 = NavigationToolbar2Tk(canvas2, frame)
canvas2.get_tk_widget().grid(row=0, column=0)

# Combo box
choices = ["gaussian fitting","manual linecut"]
choiceVar = tk.StringVar()
cb = ttk.Combobox(win.f2, textvariable=choiceVar, values=choices, state='readonly', width=13)
cb.current(0)
coordination_input = Entry(win.f2,width=25)
v = StringVar(win.f2, value='0.025')
step_input = Entry(win.f2, textvariable=v, width=10)
path_input = Entry(win.f2,width=60)
lbox = tk.Listbox(win.f2,width=60)

# get the list of files
folder = os.getcwd()
flist = os.listdir()
lbox = tk.Listbox(win.f2,width=60)
# THE ITEMS INSERTED WITH A LOOP
for item in flist:
    lbox.insert(tk.END, item)
path_input.insert(tk.END, folder)

def showcontent(event):
    x = lbox.curselection()[0]
    file = lbox.get(x)
    print(file)
    '''
    with open(file) as file:
        file = file.read()
    #text.delete('1.0', tk.END)
    #text.insert(tk.END, file)
    # print(file)
    '''

def _browser():
    global folder
    lbox.delete('0', tk.END)
    folder = filedialog.askdirectory()# show an "Open" dialog box and return folder path 
    os.chdir(folder)
    flist = os.listdir(folder) # show all files path in the folder
    print(folder)
    print(flist)
    # THE ITEMS INSERTED WITH A LOOP
    path_input.delete('0', tk.END)
    path_input.insert(-1,folder)
    for item in flist:
        lbox.insert(tk.END, item)

def _load():
    global sample
    global cb
    global fname
    # choose file
    x = lbox.curselection()[0]
    fname = lbox.get(x)
    print(fname)
    step = float(step_input.get())
    sample = functions(step,fname)
    x = sample.counts_subtractedBG[:,:,0]
    y = sample.counts_subtractedBG[:,:,1]
    z = sample.counts_subtractedBG[:,:,2]
    try:
        cb.remove()
    except:
        pass
    im = axis1.imshow(z,cmap=plt.cm.jet,extent=[x.min(),x.max(),y.min(),y.max()],origin='lower')
    cb = fig1.colorbar(im, ax=axis1)
    axis1.set_title(fname,fontsize = 8)
    canvas1.draw()

def _clean():
    try:
        axis11.get_legend().remove()
    except:
        pass
    fig2.clf()
    canvas2.draw()

# show coordination
def getClickedCord(event):
    global x0
    global y0
    global box
    x0 = round(event.xdata,4)
    y0 = round(event.ydata,4)
    print('you pressed', x0, y0)
    try:
        axis11.collections[0].remove()
        while axis11.lines != []:
            axis11.lines[0].remove()
    except:
        pass
    axis11.scatter(x0,y0,marker ='x',color='black')
    canvas1.draw()
    if choiceVar.get() == "gaussian fitting":
        coordination_input.delete('0', tk.END)
        coordination_input.insert(-1,(x0, ',', y0))
        print(coordination_input.get())
    if choiceVar.get() == "manual linecut":
        box.append((x0,y0))
        if len(box) > 2:
            box.pop(0)
        if len(box) == 2:
            try:
                axis11.lines.remove()
                while axis11.lines != []:
                    axis11.lines[0].remove()
            except:
                pass
            axis11.plot([box[0][0],box[1][0]],[box[0][1],box[1][1]],marker ='x',color='black')
            canvas1.draw()
        coordination_input.delete('0', tk.END)
        coordination_input.insert(-1,box)

def _gaussian_fitting():
    sample.gaussian_2dfitting(x0,y0)
    # 2d plot    
    axis11.plot(sample.linecut_H[:,0],sample.linecut_H[:,1],color='black', linestyle='solid',label='Horizontal')
    axis11.plot(sample.linecut_V[:,0],sample.linecut_V[:,1],color='black', linestyle='dotted',label='Vertical')
    axis11.plot(sample.linecut_D1[:,0],sample.linecut_D1[:,1],color='black', linestyle='dashed',label='Diagnol1')
    axis11.plot(sample.linecut_D2[:,0],sample.linecut_D2[:,1],color='black', linestyle='dashdot',label='Diagnol2')
    axis11.legend(fontsize=8,loc=3, bbox_to_anchor=(0,0))
    canvas1.draw()
    # linecut plot
    fig2.clear()
    axis21, axis22, axis23, axis24 = fig2.add_subplot(221), fig2.add_subplot(222), fig2.add_subplot(223), fig2.add_subplot(224)
    axis21.scatter(sample.data_H[:,0],sample.data_H[:,1],marker ='d', color='red', label='data')
    axis21.plot(sample.data_H[:,0],sample.fitting_1,color='green', label='fitting')
    axis21.legend(fontsize=8,loc=2,title='Horizontal,FWHM'+ sample.FWHM_H)
    axis22.scatter(sample.data_V[:,0],sample.data_V[:,1],marker ='d', color='red', label='data')
    axis22.plot(sample.data_V[:,0],sample.fitting_2,color='green', label='fitting')
    axis22.legend(fontsize=8,loc=2,title='Vertical,FWHM'+ sample.FWHM_V)
    axis23.scatter(sample.data_D1[:,0],sample.data_D1[:,1],marker ='d', color='red', label='data')
    axis23.plot(sample.data_D1[:,0],sample.fitting_3,color='green', label='fitting')
    axis23.legend(fontsize=8,loc=2,title='Diagnol1,FWHM'+ sample.FWHM_D1)
    axis24.scatter(sample.data_D2[:,0],sample.data_D2[:,1],marker ='d', color='red', label='data')
    axis24.plot(sample.data_D2[:,0],sample.fitting_4,color='green', label='fitting')
    axis24.legend(fontsize=8,loc=2,title='Diagnol2,FWHM'+ sample.FWHM_D2)
    fig2.suptitle(fname+'gaussian_fitting', fontsize=12)
    canvas2.draw()

def _manual_linecut():
    x1,y1,x2,y2 = box[0][0],box[0][1],box[1][0],box[1][1]
    sample.manual_linecut(x1,y1,x2,y2)
    # linecut plot
    axis2 = fig2.add_subplot(111)
    axis2.plot(sample.linecut_profile,sample.linecut_raw_data,marker ='d', label=fname)
    axis2.legend()
    canvas2.draw()
    
def _Try(event):
    print(choiceVar.get())
    if choiceVar.get() == "gaussian fitting":
        _initiate_gaussianfitting()
        
    if choiceVar.get() == "manual linecut":
        _initiate_manual_linecutfitting()
            
def _initiate_gaussianfitting():
    global button_4
    canvas1.mpl_connect('button_release_event', getClickedCord)
    button_4.grid_forget()
    button_4 = tk.Button(master=win.f2, text="fitting", command=_gaussian_fitting)
    button_4.grid(row=0, column=4, pady=10, padx=10,sticky='w')
    _clean()

def _initiate_manual_linecutfitting():
    global button_4
    canvas1.mpl_connect('button_release_event', getClickedCord)
    button_4.grid_forget()
    button_4 = tk.Button(master=win.f2, text="linecut", command=_manual_linecut)
    button_4.grid(row=0, column=4, pady=10, padx=10,sticky='w')
    _clean()

def _output1():
    fig1.savefig(folder+'/'+fname+'_image.jpg')
    print("success")

def _output2():
    if choiceVar.get() == "manual_linecut":
        fig2.savefig(folder+'/'+fname+'_manual_linecut.jpg')
    else:
        fig2.savefig(folder+'/'+fname+'_gaussian_fitting.jpg')
    print("success")

cb.grid(row=0, column=0, pady=5, padx=5,sticky='w',columnspan=2)
text_1 = Label(win.f2, text = "(x,y)")
text_1.grid(row=0, column=2, pady=5, padx=5,sticky='w')
coordination_input = Entry(win.f2,width=30)
coordination_input.grid(row=0, column=3, pady=20, padx=0,sticky='w')

button_1 = tk.Button(master=win.f2, text="browser", command=_browser)
button_1.grid(row=1, column=0, pady=10, padx=3,sticky='w')
button_2 = tk.Button(master=win.f2, text="load", command=_load)
button_2.grid(row=1, column=1, pady=10, padx=3,sticky='w')
text_2 = Label(win.f2, text = "step size")
text_2.grid(row=1, column=2, pady=5, padx=0,sticky='w')
step_input.grid(row=1, column=3, pady=10, padx=0,sticky='w')
button_3 = tk.Button(master=win.f2, text="clean", command=_clean)
button_3.grid(row=1, column=4, pady=10, padx=10,sticky='w')
button_4 = tk.Button(master=win.f2, text="fitting", command=_gaussian_fitting)
button_4.grid(row=0, column=4, pady=10, padx=10,sticky='w')
path_input.grid(row=2, column=0, pady=10, padx=0,sticky='w',columnspan = 5)
lbox.grid(row=3, column=0, pady=0, padx=0,sticky='w',columnspan = 5)

button_5 = tk.Button(master=win.f1, text="output", command=_output1)
button_5.grid(row=1, column=1, pady=10, padx=10,sticky='w')
button_6 = tk.Button(master=win.f3, text="output", command=_output2)
button_6.grid(row=1, column=0, pady=10, padx=10,sticky='w')


canvas1.mpl_connect('button_release_event', getClickedCord)

lbox.bind("<<ListboxSelect>>", showcontent)

cb.bind('<<ComboboxSelected>>', _Try)

win.mainloop()
