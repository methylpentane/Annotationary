

import os
import sys
# import glob
import re
import tkinter
from tkinter import filedialog, messagebox, ttk
from colorsys import hsv_to_rgb
from PIL import Image, ImageTk
import numpy as np

APP = None
# global instance of APPlication
UTAGOE_VERSION = 'LabelingYOLO 1.0'

LABELS_PRESET = ('car', 'track', 'bus', 'traffic light')


            #################################################################
#########################################################################################
######################################   Rectangle   ####################################
#########################################################################################
            #################################################################

class Rectangle:

	# 0-----3
	# |  |  |
	# |--+--|
	# |  |  |
	# 1-----2

	# 4 point
	# 1 rect , 2 centerline, 4 judgeline

	# APP = None
	NUM_OF_POINTS = 4
	NUM_OF_TEMP = 4
	TEMP = []
	TEMP_ID = []

	def __init__(self,coord=None):
		self.points = None
		self.label  = None
		self.ID = []
		if coord:
			self.set_points_by_coord(coord)


	def set_points_by_coord(self, coord):
		# canvasの四角形の座標形式から頂点をセット
		# set vertice by format of tkinter#canvas
		x1, y1, x2, y2 = coord
		if x1 < x2:
			if y1 < y2:
				self.points = np.array([[x1,y1],[x1,y2],[x2,y2],[x2,y1]])
			else:
				self.points = np.array([[x1,y2],[x1,y1],[x2,y1],[x2,y2]])
		else:
			if y1 < y2:
				self.points = np.array([[x2,y1],[x2,y2],[x1,y2],[x1,y1]])
			else:
				self.points = np.array([[x2,y2],[x2,y1],[x1,y1],[x1,y2]])


	def draw(self):
		# 現在の頂点リストをもとにcanvasに描画し、self.IDを設定
		# self.IDがある場合(すでに描画済み)、図形の位置を更新
		# draw on canvas by current vertice list, save IDs
		# just change coords if it have already IDs (already drawn)
		c = (self.points[0]+self.points[2]) / 2 * APP.imgcanvas.ratio
		p = self.points * APP.imgcanvas.ratio

		if self.ID:
			APP.imgcanvas.coords(self.ID[0], p[0][0], p[0][1])
			APP.imgcanvas.coords(self.ID[1], p[0][0], c[1],    p[2][0], c[1])
			APP.imgcanvas.coords(self.ID[2], c[0],    p[0][1], c[0],    p[2][1])
			APP.imgcanvas.coords(self.ID[3], p[0][0], p[0][1], p[1][0], p[1][1])
			APP.imgcanvas.coords(self.ID[4], p[1][0], p[1][1], p[2][0], p[2][1])
			APP.imgcanvas.coords(self.ID[5], p[2][0], p[2][1], p[3][0], p[3][1])
			APP.imgcanvas.coords(self.ID[6], p[3][0], p[3][1], p[0][0], p[0][1])
			APP.imgcanvas.coords(self.ID[7], p[0][0], p[0][1], p[2][0], p[2][1])
		else:
			self.ID.append(APP.imgcanvas.create_text(p[0][0],p[0][1], text=self.label, fill=APP.colors[self.label], font=('',20), justify='left', anchor='nw', tag='label'))
			self.ID.append(APP.imgcanvas.create_line(p[0][0], c[1],    p[2][0], c[1], fill=APP.colors[self.label],width='1',tag='centerline'))
			self.ID.append(APP.imgcanvas.create_line(c[0],    p[0][1], c[0],    p[2][1], fill=APP.colors[self.label],width='1',tag='centerline'))
			self.ID.append(APP.imgcanvas.create_line(p[0][0], p[0][1], p[1][0], p[1][1], stipple='@src/empty.xbm',width='11',tag='rect'))
			self.ID.append(APP.imgcanvas.create_line(p[1][0], p[1][1], p[2][0], p[2][1], stipple='@src/empty.xbm',width='11',tag='rect'))
			self.ID.append(APP.imgcanvas.create_line(p[2][0], p[2][1], p[3][0], p[3][1], stipple='@src/empty.xbm',width='11',tag='rect'))
			self.ID.append(APP.imgcanvas.create_line(p[3][0], p[3][1], p[0][0], p[0][1], stipple='@src/empty.xbm',width='11',tag='rect'))
			self.ID.append(APP.imgcanvas.create_rectangle(p[0][0], p[0][1], p[2][0], p[2][1], outline=APP.colors[self.label],fill='white',stipple='@src/empty.xbm',width='1',tag='rect'))


	def label_redraw(self):
		# ラベルだけ書き直す
		# change label showing
		APP.imgcanvas.itemconfig(self.ID[0], text=self.label, fill=APP.colors[self.label])
		APP.imgcanvas.itemconfig(self.ID[1], fill=APP.colors[self.label])
		APP.imgcanvas.itemconfig(self.ID[2], fill=APP.colors[self.label])
		APP.imgcanvas.itemconfig(self.ID[7], outline=APP.colors[self.label])


	@classmethod
	def show_temp(cls,x,y):
		if cls.TEMP_ID:
			t = [temp * APP.imgcanvas.ratio for temp in cls.TEMP]
			APP.imgcanvas.coords(cls.TEMP_ID[0], t[0], t[1], x, y)
			centerx = (t[0] + x)/2
			centery = (t[1] + y)/2
			APP.imgcanvas.coords(cls.TEMP_ID[1], centerx, t[1], centerx, y)
			APP.imgcanvas.coords(cls.TEMP_ID[2], t[0], centery, x, centery)
		else:
			cls.TEMP_ID.append(APP.imgcanvas.create_rectangle(x,y,x,y, outline='blue', width='1', tag='temp_rect'))
			cls.TEMP_ID.append(APP.imgcanvas.create_line(x,y,x,y, fill='blue', width='1', tag='temp_rect'))
			cls.TEMP_ID.append(APP.imgcanvas.create_line(x,y,x,y, fill='blue', width='1',tag='temp_rect'))


	def modify(self,n,x,y):
		# modifying rectangle
		# 四角形の変形
		global APP

		# n = n
		o = (n+1)%4
		p = (n+2)%4
		q = (n+3)%4

		# 座標を変更
		if n%2:
			self.points[n][0] = x
			self.points[n][1] = y
			self.points[o][1] = y
			self.points[q][0] = x
		else:
			self.points[n][0] = x
			self.points[n][1] = y
			self.points[o][0] = x
			self.points[q][1] = y

		# 移動後座標(_dash)に応じて頂点リストの順番を変更
		# fix the order of list
		n_dash = np.array([x,y], np.int)
		vec_pn_dash = n_dash - self.points[p]
		x_dash = vec_pn_dash[0]
		y_dash = vec_pn_dash[1]
		change_x = False
		change_y = False

		if x_dash < 0:
			if n==2 or n==3:
				change_x = True
		elif x_dash > 0:
			if n==0 or n==1:
				change_x = True

		if y_dash < 0:
			if n==1 or n==2:
				change_y = True
		elif y_dash > 0:
			if n==0 or n==3:
				change_y = True

		if change_x:
			if change_y:
				self.points = self.points[[2,3,0,1], :]
				APP.imgcanvas.knobs = APP.imgcanvas.knobs[[2,3,0,1]]
			else:
				self.points = self.points[[3,2,1,0], :]
				APP.imgcanvas.knobs = APP.imgcanvas.knobs[[3,2,1,0]]
		else:
			if change_y:
				self.points = self.points[[1,0,3,2], :]
				APP.imgcanvas.knobs = APP.imgcanvas.knobs[[1,0,3,2]]

		self.draw()


	def move(self,dxi,dyi):
		px = self.points[:,0]+dxi
		py = self.points[:,1]+dyi
		if px[0] < 1:
			px = px - (px[0]-1)
		if px[2] > APP.img_width:
			px = px - (px[2]-APP.img_width)
		if py[0] < 1:
			py = py - (py[0]-1)
		if py[2] > APP.img_height:
			py = py - (py[2]-APP.img_height)
		self.points = np.vstack((px,py)).transpose()
		self.draw()


	def erase(self):
		for ID in self.ID:
			APP.imgcanvas.delete(ID)
		self.ID.clear()



            #################################################################
#########################################################################################
######################################  Application  ####################################
#########################################################################################
            #################################################################

class Application(tkinter.Frame):

	COMMON_RATIO = 1.1

	def __init__(self, master=None):
		super().__init__(master)
		self.pack(fill=tkinter.BOTH, expand=1)
		self.create_widgets()
		self.load_yolo()
		self.zoom_reset()



	def create_widgets(self):
		# image read
		# filetyp = [('JPG File Folder','')]
		idir = os.path.abspath(os.path.dirname(__file__))
		tkinter.messagebox.showinfo(UTAGOE_VERSION,'welcome!\nplease choose the directory including image sequence')
		# file = tkinter.filedialog.askopenfilename(filetypes=filetyp, initialdir=idir)
		self.image_dir = tkinter.filedialog.askdirectory(initialdir=idir)
		if self.image_dir ==  '':
			tkinter.messagebox.showinfo(UTAGOE_VERSION,'cancel button is pressed. terminate.')
			sys.exit()

		# self.image_list = glob.glob(os.path.join(self.image_dir,'*.jpg'))
		pattern = '.*\.jpe?g'
		self.image_list = [os.path.join(self.image_dir,f) for f in os.listdir(self.image_dir) if re.search(pattern, f, re.IGNORECASE)]
		self.image_list.sort()
		# print(self.image_list)
		if len(self.image_list) == 0:
			tkinter.messagebox.showinfo(UTAGOE_VERSION,'the directory have no image!\nor your images should be \".jpg\" or \".jpeg\".')
			sys.exit()

		self.cur_index = 0
		self.image_pl = Image.open(self.image_list[self.cur_index])
		self.image_tk = ImageTk.PhotoImage(self.image_pl)

		self.img_width = self.image_pl.width
		self.cur_width = self.img_width
		self.img_height = self.image_pl.height
		self.cur_height = self.img_height

		# label
		classes_path = os.path.join(self.image_dir, 'classes.txt')
		if os.path.exists(classes_path):
			with open(classes_path) as f:
				l = f.read().splitlines()
			self.labels = tuple(l)
		else:
			self.labels = LABELS_PRESET
		self.color_num = len(self.labels)
		self.colors = self.get_colors(self.color_num)

		root.title(self.get_title_string())

		# child frame
		self.button_frame = tkinter.Frame(self)
		self.button_frame.pack(fill='x')
		self.imgcvs_frame = tkinter.Frame(self)
		self.imgcvs_frame.pack(fill='both',expand=1)

		# toolbar
		self.button_frame.zoom_frame = tkinter.Frame(self.button_frame)
		self.button_frame.scrl_frame = tkinter.Frame(self.button_frame)
		self.button_frame.save_frame = tkinter.Frame(self.button_frame)
		self.button_frame.zoom_frame.pack(side='left', padx=(0,10))
		self.button_frame.scrl_frame.pack(side='left', padx=(0,10))
		self.button_frame.save_frame.pack(side='left')

		self.zoom_in_icon = ImageTk.PhotoImage(Image.open('src/zoom_in.png'))
		self.zoom_out_icon = ImageTk.PhotoImage(Image.open('src/zoom_out.png'))
		self.zoom_reset_icon = ImageTk.PhotoImage(Image.open('src/zoom_reset.png'))
		self.prev_img_icon = ImageTk.PhotoImage(Image.open('src/prev_img.png'))
		self.next_img_icon = ImageTk.PhotoImage(Image.open('src/next_img.png'))
		self.save_icon = ImageTk.PhotoImage(Image.open('src/save.png'))

		self.zin_button = tkinter.Button(self.button_frame.zoom_frame, image=self.zoom_in_icon, command=self.zoom_in)
		self.zout_button = tkinter.Button(self.button_frame.zoom_frame, image=self.zoom_out_icon, command=self.zoom_out)
		self.reset_button = tkinter.Button(self.button_frame.zoom_frame, image=self.zoom_reset_icon, command=self.zoom_reset)
		self.prev_button = tkinter.Button(self.button_frame.scrl_frame, image=self.prev_img_icon, command=self.prev)
		self.next_button = tkinter.Button(self.button_frame.scrl_frame, image=self.next_img_icon, command=self.next)
		self.save_button = tkinter.Button(self.button_frame.save_frame, image=self.save_icon, command=self.save_yolo)
		self.zin_button.pack(side='left')
		self.zout_button.pack(side='left')
		self.reset_button.pack(side='left')
		self.prev_button.pack(side='left')
		self.next_button.pack(side='left')
		self.save_button.pack(side='left')

		# canvas
		self.cvs_width = self.img_width
		self.cvs_height = self.img_height
		self.imgcanvas = tkinter.Canvas(self.imgcvs_frame, width=self.cvs_width, height=self.cvs_height)
		self.imgcanvas.grid(row=0, column=0, sticky='NEWS')

		self.xscroll = tkinter.Scrollbar(self.imgcvs_frame, orient='horizontal', command=self.imgcanvas.xview)
		self.xscroll.grid(row=1, column=0, sticky='EW')

		self.yscroll = tkinter.Scrollbar(self.imgcvs_frame, orient='vertical', command=self.imgcanvas.yview)
		self.yscroll.grid(row=0, column=1, sticky='NS')

		self.imgcanvas.config(xscrollcommand=self.xscroll.set, yscrollcommand=self.yscroll.set)
		self.imgcvs_frame.grid_rowconfigure(0, weight=1, minsize=0)
		self.imgcvs_frame.grid_columnconfigure(0, weight=1, minsize=0)

		self.imgcanvas.focus_set()
		self.imgcanvas.config(cursor='crosshair')

		# popup menu
		self.menu = tkinter.Menu(self, tearoff=0)
		self.menu.add_command(label='DELETE focused annotation',command=self.delete)
		self.menu.add_command(label='CHANGE LABEL of focused annotation',command=lambda: self.modify_label(self.menu.event))

		# Rectangle.APP = self
		global APP
		APP = self

		# mouse event
		self.imgcanvas.tag_bind('drawable','<Button-1>',self.do_draw)
		self.imgcanvas.tag_bind('rect','<Button-1>',self.focus_id_search)
		self.imgcanvas.tag_bind('rect','<Button1-Motion>',self.move_rect)
		self.imgcanvas.tag_bind('knob','<Button1-Motion>',self.modify_rect)
		self.imgcanvas.bind('<Escape>',self.end_draw)
		self.imgcanvas.bind('<Button-3>',self.do_popup)
		self.imgcanvas.bind('<Configure>',self.save_geometry)
		self.imgcanvas.bind('<a>',self.test)

		# canvas attribute
		self.imgcanvas.rectangle = []
		self.imgcanvas.focusing = None
		self.imgcanvas.mouse_x = None
		self.imgcanvas.mouse_y = None
		self.imgcanvas.knobs = None
		self.imgcanvas.ratio = 1.0


	def test(self,event):
		for rect in self.imgcanvas.rectangle:
			print(rect.points)


	######################################################################## zoom{
	def save_geometry(self,event):
		# retain current window size
		# print('event:', event.width, event.height)
		self.cvs_width = event.width
		self.cvs_height = event.height

	def zoom_in(self,event=None):
		# print('zoom')
		self.imgcanvas.ratio *= self.COMMON_RATIO
		self.zoom_reload()


	def zoom_out(self,event=None):
		# print('zoom')
		self.imgcanvas.ratio /= self.COMMON_RATIO
		self.zoom_reload()


	def zoom_reload(self):
		self.imgcanvas.delete('img')

		# width, height update
		self.cur_width = round(self.img_width*self.imgcanvas.ratio)
		self.cur_height = round(self.img_height*self.imgcanvas.ratio)

		# new resized image
		self.image_pl_resize = self.image_pl.resize((self.cur_width, self.cur_height), Image.NEAREST)
		# print('resize')
		self.image_tk_resize = ImageTk.PhotoImage(self.image_pl_resize)
		# print('tk convert')
		self.imgcanvas.create_image(0,0,image=self.image_tk_resize, anchor='nw', tags=('img','drawable'))
		# print('canvas created')
		self.imgcanvas.tag_lower('img')

		# new resized annotation object
		for rectangle in self.imgcanvas.rectangle:
			rectangle.draw()

		# scroll update, view offset
		x = self.xscroll.get()
		y = self.yscroll.get()
		self.imgcanvas.config(scrollregion=(0,0,self.cur_width,self.cur_height))
		self.zoom_offset(x,y)

		# knob re_focus
		self.re_focus()


	def zoom_reset(self,event=None):
		# reset to default view
		if self.imgcanvas.ratio != 1.0:
			self.imgcanvas.ratio = 1.0
			self.cur_width = self.img_width
			self.cur_height = self.img_height
			del self.image_pl_resize
			del self.image_tk_resize
			self.imgcanvas.delete('img')

		self.imgcanvas.create_image(0,0,image=self.image_tk, anchor='nw', tags=('img','drawable'))
		self.imgcanvas.tag_lower('img')

		for rectangle in self.imgcanvas.rectangle:
			rectangle.draw()

		self.imgcanvas.config(scrollregion=(0,0,self.img_width,self.img_height))
		self.zoom_offset((0.0,1.0),(0.0,1.0))

		self.re_focus()


	def zoom_offset(self,x,y):
		xcenter = (x[0]+x[1])/2
		ycenter = (y[0]+y[1])/2
		newx = xcenter - self.cvs_width/2/self.cur_width
		newy = ycenter - self.cvs_height/2/self.cur_height
		# print(newx, newy)
		self.imgcanvas.xview_moveto(newx)
		self.imgcanvas.yview_moveto(newy)

	######################################################################## }zoom


	######################################################################## image scroll{
	def prev(self,event=None):
		if self.cur_index == 0:
			return

		self.unfocus()
		for rectangle in self.imgcanvas.rectangle:
			rectangle.erase()

		self.cur_index = self.cur_index-1
		self.image_pl = Image.open(self.image_list[self.cur_index])
		self.image_tk = ImageTk.PhotoImage(self.image_pl)

		self.load_yolo()
		self.zoom_reset()
		root.title(self.get_title_string())


	def next(self,event=None):
		if self.cur_index == len(self.image_list)-1:
			return

		self.unfocus()
		for rectangle in self.imgcanvas.rectangle:
			rectangle.erase()

		self.cur_index = self.cur_index+1
		self.image_pl = Image.open(self.image_list[self.cur_index])
		self.image_tk = ImageTk.PhotoImage(self.image_pl)

		self.load_yolo()
		self.zoom_reset()
		root.title(self.get_title_string())


	######################################################################## }image_scroll


	######################################################################## save,load{
	def load_yolo(self):
		name = '{0:04d}.txt'.format(self.cur_index)
		yolo_path = os.path.join(self.image_dir, name)
		self.imgcanvas.rectangle = []
		if os.path.exists(yolo_path):
			with open(yolo_path, 'r') as file:
				for line in file.readlines():
					l = line.split(' ')
					rect = Rectangle(self.yolo_to_tk(float(l[1]),float(l[2]),float(l[3]),float(l[4])))
					rect.label = self.labels[int(l[0])]
					print(rect.points)
					self.imgcanvas.rectangle.append(rect)


	def save_yolo(self):
		name = '{0:04d}.txt'.format(self.cur_index)
		yolo_path = os.path.join(self.image_dir, name)
		line = []
		with open(yolo_path, 'w') as file:
			for rect in self.imgcanvas.rectangle:
				l = str(self.labels.index(rect.label)) + ' '
				yolo_str = ['{0:.6f}'.format(y) for y in self.tk_to_yolo(rect.points[0][0],rect.points[0][1],rect.points[2][0],rect.points[2][1])]
				l = l + ' '.join(yolo_str)
				line.append(l)
			file.write('\n'.join(line))

	######################################################################## }save,load


	######################################################################## right click menu{
	def do_popup(self,event=None):
		self.imgcanvas.tag_unbind('drawable','<Button-1>')
		self.imgcanvas.tag_unbind('rect','<Button-1>')
		self.imgcanvas.tag_unbind('rect','<Button1-Motion>')
		self.imgcanvas.tag_unbind('knob','<Button1-Motion>')
		self.imgcanvas.unbind('<Escape>')
		self.imgcanvas.bind('<Button-1>',self.end_popup)

		self.menu.post(event.x_root, event.y_root)
		self.menu.event = event
		# storing cursor coord


	def end_popup(self,event=None):
		self.imgcanvas.unbind('<Button-1>')
		self.imgcanvas.tag_bind('drawable','<Button-1>',self.do_draw)
		self.imgcanvas.tag_bind('rect','<Button-1>',self.focus_id_search)
		self.imgcanvas.tag_bind('rect','<Button1-Motion>',self.move_rect)
		self.imgcanvas.tag_bind('knob','<Button1-Motion>',self.modify_rect)
		self.imgcanvas.bind('<Escape>',self.end_draw)

		self.menu.grab_release()
		self.menu.unpost()


	def delete(self):
		self.imgcanvas.focusing.erase()
		self.imgcanvas.rectangle.remove(self.imgcanvas.focusing)
		self.unfocus()
		self.end_popup()


	def modify_label(self,event):
		self.label_process(self.imgcanvas.focusing, event)
		if self.is_apply:
			self.imgcanvas.focusing.label_redraw()
		del self.is_apply
		self.end_popup()

	######################################################################## }right click menu


	######################################################################## draw,label{
	def do_draw(self,event):
		# print('start')
		self.imgcanvas.tag_unbind('drawable','<Button-1>')
		self.imgcanvas.tag_unbind('rect','<Button-1>')
		self.imgcanvas.tag_unbind('rect','<Button1-Motion>')
		self.imgcanvas.tag_unbind('knob','<Button1-Motion>')
		self.imgcanvas.unbind('<Button-3>')
		self.imgcanvas.bind('<Motion>',self.show_temp)
		self.imgcanvas.tag_bind('all','<Button-1>',self.draw_rect)
		self.zin_button.config(state='disable')
		self.zout_button.config(state='disable')
		self.reset_button.config(state='disable')
		self.next_button.config(state='disable')
		self.prev_button.config(state='disable')
		self.save_button.config(state='disable')
		self.draw_rect(event)


	def draw_rect(self,event):
		# print('drawing')
		xi,yi = self.xy_on_image(event.x, event.y)
		xc,yc = self.xy_on_canvas(event.x, event.y)
		Rectangle.TEMP.append(xi)
		Rectangle.TEMP.append(yi)
		if len(Rectangle.TEMP) == Rectangle.NUM_OF_TEMP:
			rect = Rectangle(tuple(Rectangle.TEMP))
			self.label_process(rect,event)
			if self.is_apply:
				rect.draw()
				self.focus(rect)
				self.imgcanvas.rectangle.append(rect)
			del self.is_apply
			self.end_draw()
		else:
			self.imgcanvas.create_oval(xc-7,yc-7,xc+7,yc+7, fill='blue', tag='temp_oval')
			Rectangle.show_temp(xc,yc)


	def label_process(self,rect,event):
		self.l_window = tkinter.Toplevel(self)
		# self.l_window.withdraw()
		self.l_window.resizable(0,0)
		self.l_window.protocol("WM_DELETE_WINDOW", lambda: self.add_label(rect,0))

		self.l_window.l_combo = ttk.Combobox(self.l_window, state='readonly')
		self.l_window.l_combo['values'] = self.labels
		self.l_window.l_combo.current(0)
		self.l_window.l_combo.grid(row=0, column=0, columnspan=2, sticky='NEWS', padx=2, pady=2)

		self.l_window.l_button1 = tkinter.Button(self.l_window, text='決定', width=12, command=lambda: self.add_label(rect,1))
		self.l_window.l_button2 = tkinter.Button(self.l_window, text='キャンセル', width=12, command=lambda: self.add_label(rect,0))
		self.l_window.l_button1.grid(row=1,column=0,padx=2,pady=2)
		self.l_window.l_button2.grid(row=1,column=1,padx=2,pady=2)

		self.l_window.l_combo.focus_set()

		width  = self.winfo_width()
		height  = self.winfo_height()
		l_width  = self.l_window.winfo_reqwidth()
		l_height  = self.l_window.winfo_reqheight()
		event.x_root = event.x_root - (l_width - (width - event.x)) if width - event.x < l_width else event.x_root
		event.y_root = event.y_root - (l_height - (height - event.y)) if height - event.y < l_height else event.y_root
		self.l_window.geometry('+'+str(event.x_root)+'+'+str(event.y_root))
		# self.l_window.deiconify()
		self.l_window.wait_visibility()
		self.l_window.lift()
		self.l_window.grab_set()

		self.wait = tkinter.IntVar()
		self.l_window.wait_variable(self.wait)


	def add_label(self,rect,is_apply):
		self.is_apply = is_apply
		if self.is_apply:
			rect.label = self.l_window.l_combo.get()
		self.l_window.grab_release()
		self.l_window.destroy()
		self.wait.set(1)


	def show_temp(self,event):
		xc,yc = self.xy_on_canvas(event.x, event.y)
		Rectangle.show_temp(xc,yc)


	def end_draw(self,event=None):
		# print('end')
		self.imgcanvas.unbind('<Motion>')
		self.imgcanvas.tag_unbind('all','<Button-1>')
		self.imgcanvas.tag_bind('drawable','<Button-1>',self.do_draw)
		self.imgcanvas.tag_bind('rect','<Button-1>',self.focus_id_search)
		self.imgcanvas.tag_bind('rect','<Button1-Motion>',self.move_rect)
		self.imgcanvas.tag_bind('knob','<Button1-Motion>',self.modify_rect)
		self.imgcanvas.bind('<Button-3>',self.do_popup)
		self.zin_button.config(state='active')
		self.zout_button.config(state='active')
		self.reset_button.config(state='active')
		self.next_button.config(state='active')
		self.prev_button.config(state='active')
		self.save_button.config(state='active')



		if Rectangle.TEMP:
			Rectangle.TEMP.clear()
			Rectangle.TEMP_ID.clear()
			self.imgcanvas.delete('temp_oval')
			self.imgcanvas.delete('temp_rect')



	######################################################################## }draw,labal


	######################################################################## modify{
	def modify_rect(self,event):
		xi,yi = self.xy_on_image(event.x, event.y)
		# print(self.imgcanvas.find_withtag('current'))
		ID = self.imgcanvas.find_withtag('current')[0]
		n = np.where(self.imgcanvas.knobs==ID)[0][0]
		# print('id=',ID,'index=',n)
		self.imgcanvas.focusing.modify(n,xi,yi)
		self.re_focus()
	######################################################################## }modify


	######################################################################## move{
	def move_init(self,event):
		self.imgcanvas.mouse_x, self.imgcanvas.mouse_y = self.xy_on_canvas(event.x,event.y)


	def move_rect(self,event):
		xc,yc = self.xy_on_canvas(event.x, event.y)
		dxi = round(xc-self.imgcanvas.mouse_x)/self.imgcanvas.ratio
		dyi = round(yc-self.imgcanvas.mouse_y)/self.imgcanvas.ratio
		self.imgcanvas.focusing.move(dxi, dyi)
		self.imgcanvas.mouse_x = xc
		self.imgcanvas.mouse_y = yc
		self.re_focus()
	######################################################################## }move


	######################################################################## focus{
	def focus(self,rect):
		# 図形をfocusingに指定し、Knobを描画
		# すでにfocusingに指定されている場合(Knobを描画済み)、Knobの位置を更新->re_focus
		# 図形とノブを一番上に持ってくる
		# focus annotaion, draw 'Knobs'
		# just change coord of 'Knobs' if they're already drawn (already focused) -> re_focus
		# adjust order of canvas object
		if not self.imgcanvas.focusing == rect:
			self.imgcanvas.focusing = rect
			self.imgcanvas.delete('knob')
			self.imgcanvas.knobs = np.zeros(rect.__class__.NUM_OF_POINTS, np.int32)
			for i,p in enumerate(rect.points*self.imgcanvas.ratio):
				ID = self.imgcanvas.create_oval(p[0]-7, p[1]-7, p[0]+7, p[1]+7, fill='white', tag='knob')
				# print(i, p, ID)
				self.imgcanvas.knobs[i] = ID
		else:
			for i,p in enumerate(rect.points*self.imgcanvas.ratio):
				self.imgcanvas.coords(self.imgcanvas.knobs[i], p[0]-7, p[1]-7, p[0]+7, p[1]+7)
				# print(i, p, ID)
		for ID in rect.ID:
			self.imgcanvas.tag_raise(ID)
		self.imgcanvas.tag_raise('knob')


	def re_focus(self):
		if self.imgcanvas.focusing:
			self.focus(self.imgcanvas.focusing)


	def focus_id_search(self,event):
		ID = self.imgcanvas.find_withtag('current')[0]
		for r in self.imgcanvas.rectangle:
			for i in r.ID:
				if i == ID:
					self.focus(r)
					self.move_init(event)
					return


	def unfocus(self):
		self.imgcanvas.focusing = None
		self.imgcanvas.knobs = None
		self.imgcanvas.delete('knob')
	######################################################################## }focus


	######################################################################## utiliity{
	def xy_on_canvas(self,x,y):
		# return coord on canvas (external value)
		x = self.imgcanvas.canvasx(x)
		y = self.imgcanvas.canvasy(y)
		if x > self.cur_width:
			a = self.cur_width
		elif x < 1:
			a = 1
		else:
			a = x

		if y > self.cur_height:
			b = self.cur_height
		elif y < 1:
			b = 1
		else:
			b = y

		return a,b


	def xy_on_image(self,x,y):
		# using ratio, return coord on original image size (internal value)
		x = self.imgcanvas.canvasx(x) / self.imgcanvas.ratio
		y = self.imgcanvas.canvasy(y) / self.imgcanvas.ratio

		if x > self.img_width:
			a = self.img_width
		elif x < 1:
			a = 1
		else:
			a = round(x)

		if y > self.img_height:
			b = self.img_height
		elif y < 1:
			b = 1
		else:
			b = round(y)

		return a,b


	def tk_to_yolo(self,x1,y1,x2,y2):
		x1 = (x1-1) / (self.img_width-1)
		x2 = (x2-1) / (self.img_width-1)
		y1 = (y1-1) / (self.img_height-1)
		y2 = (y2-1) / (self.img_height-1)
		# print(x1,x2,y1,y2)
		x = ((x1+x2)/2)
		y = ((y1+y2)/2)
		w = (x2-x1)
		h = (y2-y1)
		return x,y,w,h

	def yolo_to_tk(self,x,y,w,h):
		x1 = x-w/2
		x2 = x+w/2
		y1 = y-h/2
		y2 = y+h/2
		x1 = round(x1*(self.img_width-1))+1
		x2 = round(x2*(self.img_width-1))+1
		y1 = round(y1*(self.img_height-1))+1
		y2 = round(y2*(self.img_height-1))+1
		return x1,y1,x2,y2

	def get_colors(self, color_num):
		colors = {}
		for i in range(0,color_num):
			r,g,b = hsv_to_rgb((1 / color_num * i),1,1)
			code = '#{:02x}{:02x}{:02x}'.format(round(r*255),round(g*255),round(b*255))
			colors[self.labels[i]] = code
		return colors

	def get_title_string(self):
		return UTAGOE_VERSION + ' @ ' + self.image_dir + ' - ' + str(self.cur_index+1) + '/' + str(len(self.image_list))
	######################################################################## }utility





            #################################################################
#########################################################################################
######################################      main     ####################################
#########################################################################################
            #################################################################

def on_closing(root):
    if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
        root.destroy()

root = tkinter.Tk()
root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
# root frame
root.withdraw()
app = Application(master=root)
root.deiconify()
app.mainloop()
