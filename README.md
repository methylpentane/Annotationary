# Annotationary
tool for making YOLO annotation file  

This is originally for our project of ml-based tracking.

You can draw and make YOLO annotation(label) files from your jpg image sequence.

![screenshot](https://github.com/utagoeinc/Annotationary/blob/images/src/screenshot.PNG)

## Getting Started
___
#### 1. Prepare environment  
At first, this code safely run at Windows.  
Although this is python code, we do not recommend Linux and mac because they don't run this code properly.

And you need:  
- python3
- tkinter
- pillow
- numpy

___
#### 2. Prepare image sequence  
image sequence must be jpg(jpeg) format.  
And give each image numbered file name.  
	
__example a:__ image0000.jpg, image0001.jpg, image0002.jpg, image0003.jpg ...  
__example b:__ picture-3246.JPG, picture-3247.JPG, picture-3248.JPG, picture-3249.JPG ...  

Any file name is ok if python's sort can resolve.

___
#### 3. Prepare class list  
Make __'classes.txt'__ for setup YOLO class you want to input.  
Format is simple. if you set the class "car" and "track" and "people",

	car
	track
	people
	
and save as "classes.txt" __in "data" directory of this repositry.__  

## Operation
___
#### 0. select directory
You will be asked for image directory path, and annotation directory path to save (it can load, too!).  
No JPG images in image directory, cause error.  
You can run with directory "sample" and "labels" if you want see demo.
___
#### 1. add annotation  
Click at start point, and one more click at end point to draw annotation. then choose class.
Esc key can quit drawing phase.  
___
#### 2. move annotation  
Drag rectangle for move, drag circle on vertice to deform.  
___
#### 3. save annotation
Press floppy disk button to save annotations on current image as txt file.  
___
#### 4. right click menu  
you can delete and change annotations from right click menu.  
the change will not saved until you press save button again.  
___
#### 5. other button on above
magnifier -> zoom function  
triangle -> browse function  


## Optional
___
#### point style annotation
presssing p key, Annotationary will change the mode to point mode.  
In this mode, annotation style is point and saved txt file is like (label, x_coord, y_coord).  
this function is for our experimental use, of course not for proper YOLO model.  
pressing r key, you can resume to regular rectangle mode.  