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


class image_analyzer:
    
    def __init__(self, ):
        self.fname,self.cb, self.sample= [],[],[]
        self.button_4, self.box = [], []
        self.x0, self.y0 = 0,0
        self.win = self.setWin()
        self.setCanvas()
        self.setComboBox()
        self.folder = os.getcwd()
        self.flist = os.listdir()
        v = StringVar(self.win.f2, value='0.025')
        self.step_input = Entry(self.win.f2, textvariable=v, width=10)
        self.path_input = Entry(self.win.f2,width=60)
        self.lbox = tk.Listbox(self.win.f2,width=60)
        # THE ITEMS INSERTED WITH A LOOP
        for item in self.flist:
            self.lbox.insert(tk.END, item)
        self.path_input.insert(tk.END, self.folder)
        
        win = self.win
        text_1 = Label(win.f2, text = "(x,y)")
        text_1.grid(row=0, column=2, pady=5, padx=5,sticky='w')

        self.coordination_input = Entry(win.f2,width=30)
        self.coordination_input.grid(row=0, column=3, pady=20, padx=0,sticky='w')
        
        button_1 = tk.Button(master=win.f2, text="browser", command=self._browser)
        button_1.grid(row=1, column=0, pady=10, padx=3,sticky='w')
        button_2 = tk.Button(master=win.f2, text="load", command=self._load)
        button_2.grid(row=1, column=1, pady=10, padx=3,sticky='w')
        text_2 = Label(win.f2, text = "step size")
        text_2.grid(row=1, column=2, pady=5, padx=0,sticky='w')
        self.step_input.grid(row=1, column=3, pady=10, padx=0,sticky='w')
        button_3 = tk.Button(master=win.f2, text="clean", command=self._clean)
        button_3.grid(row=1, column=4, pady=10, padx=10,sticky='w')
        self.button_4 = tk.Button(master=win.f2, text="fitting", command=self._gaussian_fitting)
        self.button_4.grid(row=0, column=4, pady=10, padx=10,sticky='w')
        self.path_input.grid(row=2, column=0, pady=10, padx=0,sticky='w',columnspan = 5)
        self.lbox.grid(row=3, column=0, pady=0, padx=0,sticky='w',columnspan = 5)
        
        button_5 = tk.Button(master=win.f1, text="output", command=self._output1)
        button_5.grid(row=1, column=1, pady=10, padx=10,sticky='w')
        button_6 = tk.Button(master=win.f3, text="output", command=self._output2)
        button_6.grid(row=1, column=0, pady=10, padx=10,sticky='w')
        
        
        self.canvas1.mpl_connect('button_release_event', self.getClickedCord)
        
        self.lbox.bind("<<ListboxSelect>>", self.showcontent)
        
        
        self.win.mainloop()
    
    def setWin(self):
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
        return win
    
    def setCanvas(self):
        # draw figure & induce fig toolbar
        self.fig1 = Figure(figsize=(5, 4), dpi=100)
        self.axis1 = self.fig1.add_subplot(111)
        self.axis11 = self.fig1.add_subplot(111)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.win.f1)  # A tk.DrawingArea.
        self.canvas1.draw()
        self.canvas1.get_tk_widget().grid(row=0, column=0, pady=0, padx=0, columnspan=2)
        
        frame = tk.Frame(self.win.f1)
        frame.grid(row=1, column=0)
        self.toobar1 = NavigationToolbar2Tk(self.canvas1, frame)
        self.canvas1.get_tk_widget().grid(row=0, column=0)
        
        self.fig2 = Figure(figsize=(10, 8), dpi=100)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.win.f3)  # A tk.DrawingArea.
        self.canvas2.draw()
        self.canvas2.get_tk_widget().grid(row=0, column=0, pady=0, padx=0, columnspan=2)
        
        frame = tk.Frame(self.win.f3)
        frame.grid(row=1, column=0)
        self.toobar2 = NavigationToolbar2Tk(self.canvas2, frame)
        self.canvas2.get_tk_widget().grid(row=0, column=0)
        
    def setComboBox(self):
        # Combo box
        choices = ["gaussian fitting","manual linecut"]
        self.choiceVar = tk.StringVar()
        self.cb = ttk.Combobox(self.win.f2, textvariable=self.choiceVar, values=choices, state='readonly', width=13)
        self.cb.current(0)
        self.cb.grid(row=0, column=0, pady=5, padx=5,sticky='w',columnspan=2)
        self.cb.bind('<<ComboboxSelected>>', self._Try)

    def showcontent(self,event):
        x = self.lbox.curselection()[0]
        file = self.lbox.get(x)
        print(file)
    
    def _browser(self):
        self.lbox.delete('0', tk.END)
        self.folder = filedialog.askdirectory()# show an "Open" dialog box and return folder path 
        os.chdir(self.folder)
        flist = os.listdir(self.folder) # show all files path in the folder
        print(self.folder)
        print(flist)
        # THE ITEMS INSERTED WITH A LOOP
        self.path_input.delete('0', tk.END)
        self.path_input.insert(-1,self.folder)
        for item in flist:
            self.lbox.insert(tk.END, item)
    
    def _load(self):
        # global sample
        # global cb
        # global fname
        # choose file
        x = self.lbox.curselection()[0]
        self.fname = self.lbox.get(x)
        fname = self.fname
        print(fname)
        step = float(self.step_input.get())
        self.sample = functions(step,fname)
        x = self.sample.counts_subtractedBG[:,:,0]
        y = self.sample.counts_subtractedBG[:,:,1]
        z = self.sample.counts_subtractedBG[:,:,2]
        try:
            self.cb.remove()
        except:
            pass
        im = self.axis1.imshow(z,cmap=plt.cm.jet,extent=[x.min(),x.max(),y.min(),y.max()],origin='lower')
        self.cb = self.fig1.colorbar(im, ax=self.axis1)
        self.axis1.set_title(self.fname,fontsize = 8)
        self.canvas1.draw()
    
    def _clean(self,):
        try:
            self.axis11.get_legend().remove()
        except:
            pass
        self.fig2.clf()
        self.canvas2.draw()
    
    # show coordination
    def getClickedCord(self,event):
        # global x0
        # global y0
        # global box
        self.x0 = round(event.xdata,4)
        self.y0 = round(event.ydata,4)
        print('you pressed', self.x0, self.y0)
        try:
            self.axis11.collections[0].remove()
            while self.axis11.lines != []:
                self.axis11.lines[0].remove()
        except:
            pass
        self.axis11.scatter(self.x0,self.y0,marker ='x',color='black')
        self.canvas1.draw()
        if self.choiceVar.get() == "gaussian fitting":
            self.coordination_input.delete('0', tk.END)
            self.coordination_input.insert(-1,(self.x0, ',', self.y0))
            print(self.coordination_input.get())
        if self.choiceVar.get() == "manual linecut":
            self.box.append((self.x0,self.y0))
            if len(self.box) > 2:
                self.box.pop(0)
            if len(self.box) == 2:
                try:
                    self.axis11.lines.remove()
                    while self.axis11.lines != []:
                        self.axis11.lines[0].remove()
                except:
                    pass
                box = self.box
                self.axis11.plot([box[0][0],box[1][0]],[box[0][1],box[1][1]],marker ='x',color='black')
                self.canvas1.draw()
            self.coordination_input.delete('0', tk.END)
            self.coordination_input.insert(-1,self.box)
    
    def _gaussian_fitting(self):
        sample = self.sample
        axis11 = self.axis11
        x0,y0 = self.x0,self.y0
        canvas1,canvas2 = self.canvas1,self.canvas2
        fig2 = self.fig2
        fname = self.fname
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
    
    def _manual_linecut(self):
        box = self.box
        sample = self.sample
        fname = self.fname
        x1,y1,x2,y2 = box[0][0],box[0][1],box[1][0],box[1][1]
        self.sample.manual_linecut(x1,y1,x2,y2)
        # linecut plot
        axis2 = self.fig2.add_subplot(111)
        axis2.plot(sample.linecut_profile,sample.linecut_raw_data,marker ='d', label=fname)
        axis2.legend()
        self.canvas2.draw()
        
    def _Try(self,event):
        choiceVar = self.choiceVar
        print(choiceVar.get())
        if choiceVar.get() == "gaussian fitting":
            self._initiate_gaussianfitting()
            
        if choiceVar.get() == "manual linecut":
            self._initiate_manual_linecutfitting()
                
    def _initiate_gaussianfitting(self):
        # global button_4
        button_4 = self.button_4
        self.canvas1.mpl_connect('button_release_event', self.getClickedCord)
        button_4.grid_forget()
        button_4 = tk.Button(master=self.win.f2, text="fitting", command=self._gaussian_fitting)
        button_4.grid(row=0, column=4, pady=10, padx=10,sticky='w')
        self._clean()
    
    def _initiate_manual_linecutfitting(self):
        # global button_4
        button_4 = self.button_4
        self.canvas1.mpl_connect('button_release_event', self.getClickedCord)
        button_4.grid_forget()
        button_4 = tk.Button(master=self.win.f2, text="linecut", command=self._manual_linecut)
        button_4.grid(row=0, column=4, pady=10, padx=10,sticky='w')
        self._clean()
    
    def _output1(self):
        self.fig1.savefig(self.folder+'/'+self.fname+'_image.jpg')
        print("success")
    
    def _output2(self):
        folder = self.folder
        fname = self.fname
        if self.choiceVar.get() == "manual_linecut":
            self.fig2.savefig(folder+'/'+fname+'_manual_linecut.jpg')
        else:
            self.fig2.savefig(folder+'/'+fname+'_gaussian_fitting.jpg')
        print("success")

temp = image_analyzer()
