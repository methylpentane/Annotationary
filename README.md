# utagoekaki
YOLO format labeling tool.  'oekaki' = drawing (japanese)

This is originally for our project of ml-based tracking.

You can draw and make YOLO label(annotation) files from your jpg image sequence.

![screenshot](https://github.com/utagoeinc/utagoekaki/blob/images/src/screenshot.PNG)

## Getting Started
___
#### 1. Prepare environment  
At first, this code safely run at Windows.  
Although this is python code, we not recommend Linux and mac because they don't run this code properly.

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
	
and save as "classes.txt" __in directory of image sequence.__

## Operation
___
#### 1. add label  
Click at start point, and one more click at end point to draw label. then choose class.
Esc key can quit drawing phase.
___
#### 2. move label  
Drag rectangle for move, drag circle on vertice to deform.  
___
#### 3. save label
Press floppy disk button to save labels on current image as text file. The file is in same directory of images.  
___
#### 4. right click menu  
you can delete and change label from right click menu.  
the change will not saved until you press save button again.
___
#### 5. other button on above
magnifier -> zoom function  
triangle -> browse function
