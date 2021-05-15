import numpy as np
import h5py 
import matplotlib.pyplot as plt
import scipy.optimize as opt
import math


class functions(): 

    def __init__(self,step,fname):
        self.fname = fname
        self.data = h5py.File(fname, 'r')
        self.counts = np.array(self.data['measurement/APD_MCL_2DSlowScan/count_rate_map'][0,:,:].T) # grab first 
        self.data.close()
        # please modify the BG and step in the main text
        self.BG = 0
        self.x0, self.x1, self.x2, self.y0, self.y1, self.y2 = 0, 0, 0, 0, 0, 0
        self.step = step
        print(self.step)
        self.counts_subtractedBG = self.counts - self.BG
        self.length_y =np.shape(self.counts_subtractedBG)[0] * self.step
        self.length_x = np.shape(self.counts_subtractedBG)[1] * self.step
        self.x =np.round(np.arange(0,self.length_x,self.step),6)
        self.y =np.round(np.arange(0,self.length_y,self.step),6) # np.linspace(0,self.length_y - 1,self.length_y)*self.step
        self.x_grid, self.y_grid = np.meshgrid(self.x,self.y)
        self.counts_subtractedBG = np.dstack((self.x_grid, self.y_grid, self.counts_subtractedBG))
    
    def gaussian_2dfitting(self,x0,y0):
        self.x0, self.y0 = x0, y0
        self.x0 = self.x[np.abs(self.x-x0).argmin()]
        self.y0 = self.y[np.abs(self.y-y0).argmin()]
        self.x0_ind = np.where(self.x==self.x0)[0]
        self.y0_ind = np.where(self.y==self.y0)[0]
        
        # horizontal & vertical linecut
        t = self.counts_subtractedBG
        self.data_H = t[self.y0_ind,:,:][0,:,:][:,[0,2]]
        self.linecut_H = t[self.y0_ind,:,:][0,:,:][:,[0,1]]
        self.data_V = t[:,self.x0_ind,:][:,0,:][:,[1,2]]
        self.linecut_V = t[:,self.x0_ind,:][:,0,:][:,[0,1]]
        self.center = t[self.y0_ind,self.x0_ind,:]

        # diagnol linecut
        self.data_D1, self.data_D2 = [], []
        #diagnol 1 
        count = 0
        while self.x0_ind + count < len(self.x) and self.y0_ind + count < len(self.y) :
            new = t[self.y0_ind + count,self.x0_ind + count]
            self.data_D1.append(new[0])
            count = count + 1
        count = 1
        while self.x0_ind - count > 0 and self.y0_ind - count > 0:
            new = t[self.y0_ind - count,self.x0_ind - count]
            self.data_D1.insert(0,new[0])
            count = count + 1
        self.data_D1 = np.array(self.data_D1)
        
        self.linecut_D1 = self.data_D1[:,[0,1]]
        self.data_D1 =  np.vstack((self.data_D1[:,0] * (2**0.5),self.data_D1[:,2])).T
        
        #diagnol2
        count = 0
        while self.x0_ind + count < len(self.x) and self.y0_ind - count > 0:
            new = t[self.y0_ind - count,self.x0_ind + count]
            self.data_D2.append(new[0])
            count = count + 1
        count = 1
        while self.x0_ind - count > 0 and self.y0_ind + count < len(self.y):
            new = t[self.y0_ind + count,self.x0_ind - count]
            self.data_D2.insert(0,new[0])
            count = count + 1
        self.data_D2 = np.array(self.data_D2)
        self.linecut_D2 = self.data_D2[:,[0,1]]
        self.data_D2 =  np.vstack((self.data_D2[:,0] * (2**0.5),self.data_D2[:,2])).T
        
        # fitting
        def gaussian(x, amp, cen, wid,BG):
            return amp * np.exp(-(x-cen)**2 / wid) + BG
        init_vals = [self.center[0,2], self.center[0,0], 0.5, 500] # guess for inital fit
        popt1, _ = opt.curve_fit(gaussian,self.data_H[:,0],self.data_H[:,1], p0=init_vals,maxfev = 2000)
        self.fitting_1 = gaussian(self.data_H[:,0], *popt1)
        init_vals = [self.center[0,2], self.center[0,1], 0.5, 500] # guess for inital fit
        popt2, _ = opt.curve_fit(gaussian,self.data_V[:,0],self.data_V[:,1], p0=init_vals,maxfev = 2000)
        self.fitting_2 = gaussian(self.data_V[:,0], *popt2)
        
        init_vals = [self.center[0,2], np.max(self.data_D1[:,0])/2, 0.6, 500]
        popt3, _ = opt.curve_fit(gaussian,self.data_D1[:,0],self.data_D1[:,1], p0=init_vals,maxfev = 2000)
        self.fitting_3 = gaussian(self.data_D1[:,0], *popt3)
        init_vals = [self.center[0,2], np.max(self.data_D2[:,0])/2, 0.6, 500]
        popt4, _ = opt.curve_fit(gaussian,self.data_D2[:,0],self.data_D2[:,1], p0=init_vals,maxfev = 2000)
        self.fitting_4 = gaussian(self.data_D2[:,0], *popt4)
    
        #calculate FWHM
        mask = self.fitting_1 > self.fitting_1.max() * 0.5
        self.FWHM_H = str(round(len(self.fitting_1[mask]) * self.step, 4))
        mask = self.fitting_2 > self.fitting_2.max() * 0.5
        self.FWHM_V =  str(round(len(self.fitting_2[mask]) * self.step, 4))
        mask = self.fitting_3 > self.fitting_3.max() * 0.5
        self.FWHM_D1 = str(round(len(self.fitting_3[mask]) * self.step * 2 ** 0.5, 4))
        mask = self.fitting_4 > self.fitting_4.max() * 0.5
        self.FWHM_D2 = str(round(len(self.fitting_4[mask]) * self.step * 2 ** 0.5, 4))
    
    def manual_linecut(self,x1,y1,x2,y2):
        self.x1, self.x2, self.y1, self.y2 = x1, x2, y1, y2

        # in order to mainipulate, every coordination is based on index, instead of raw data
        # linecut points
        x1, x2, y1, y2 = x1 / self.step, x2 / self.step, y1 / self.step, y2 / self.step
        # slope & intercept
        k = (y2-y1) / (x2-x1)
        b = y1 - k * x1
        # pick up points cutting the edge of the index squre, x edge 1st then y edge second
        index_step = 1
        if x1 > x2:
            index_step = -1
        linecut_x1 = np.arange(round(x1)+0.5, round(x2)+0.5, index_step)
        linecut_y1 = k * linecut_x1 + b
        linecut_xy1 = np.array([linecut_x1,linecut_y1]).T
        print('linecut_xy1',linecut_xy1)
        index_step = 1
        if y1 > y2:
            index_step = -1        
        linecut_y2 = np.arange(round(y1)+0.5, round(y2)+0.5, index_step)
        linecut_x2 = (linecut_y2 - b) / k
        linecut_xy2 = np.array([linecut_x2,linecut_y2]).T
        print('linecut_xy2',linecut_xy2)
        # combine 2, then sort by value from 1 column and 2 colunm 
        linecut_xy = np.concatenate((linecut_xy1,linecut_xy2))
        linecut_xy =np.array(sorted(linecut_xy, key = lambda x: (x[0],x[1]))) # convert list to array after sorted 
        #prepare ind to pick raw data from map
        linecut_profile_ind =  linecut_xy[:, [1, 0]] 
        # round the index, enable them ready for read data 
        for count1 in range(np.shape(linecut_profile_ind)[0]):
            for count2 in range(np.shape(linecut_profile_ind)[1]):
                if linecut_profile_ind[count1,count2] >= math.floor(linecut_profile_ind[count1,count2])+0.5:
                    linecut_profile_ind[count1,count2] = int(math.floor(linecut_profile_ind[count1,count2]) + 1)
                else:
                    linecut_profile_ind[count1,count2] = int(math.floor(linecut_profile_ind[count1,count2]))
        self.linecut_raw_data = self.counts_subtractedBG[:,:,2][linecut_profile_ind[:,0].astype(np.int),linecut_profile_ind[:,1].astype(np.int)]
        self.linecut_profile = ( (linecut_xy[:,0] - linecut_xy[0,0]) ** 2 + (linecut_xy[:,1] - linecut_xy[0,1])**2 ) ** 0.5 * self.step
