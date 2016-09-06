# myutils.py

import os
import errno
import cv2
from os import listdir, makedirs
from os.path import isfile, join, isdir
import cv2
import numpy as np

# read in colour images, write out black and white images
def colour_to_bw(dirIn, dirOut):
	
	# get all the file names in dirIn
	fnames = [f for f in listdir(dirIn) if isfile(join(dirIn, f))]

	# get the full path for reading image files
	fnamesfull = [join(dirIn, f) for f in fnames]

	# get the full path for writing image files
	outfnamesfull = [join(dirOut, f) for f in fnames]

	# create output directory dirOut if it does not exist
	try:
		makedirs(dirOut)
		print dirOut + " created ..."
	except OSError as exc:
		if exc.errno == errno.EEXIST and os.path.isdir(dirOut):
			pass
		else:
			raise

 	# turn colour images into black and white images
	for i, f in enumerate(fnamesfull):
		img = cv2.imread(f, 0) # read as grayscale
		img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
		cv2.imwrite(outfnamesfull[i], img)		

def invert_bw(dirIn, dirOut):

	# get all the file names in dirIn
	fnames = [f for f in listdir(dirIn) if isfile(join(dirIn, f))]

	# get the full path for reading image files
	fnamesfull = [join(dirIn, f) for f in fnames]

	# get the full path for writing image files
	outfnamesfull = [join(dirOut, f) for f in fnames]

	# create output directory dirOut if it does not exist
	try:
		makedirs(dirOut)
		print dirOut + " created ..."
	except OSError as exc:
		if exc.errno == errno.EEXIST and os.path.isdir(dirOut):
			pass
		else:
			raise

 	# turn colour images into black and white images
	for i, f in enumerate(fnamesfull):
		img = cv2.imread(f, 0) # read as grayscale
		img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV)
		cv2.imwrite(outfnamesfull[i], img)		

def draw_rect_and_save(dirOut, f, ft, method, min_loc, max_loc, s_w, s_h, img, m, s):

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc

    bottom_right = (top_left[0] + int(s_w), top_left[1] + int(s_h)); #print bottom_right

    # turn into colour image
    img_colour = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    cv2.rectangle(img_colour, top_left, bottom_right, (255,0,0), 20)
    
    outPath = dirOut + m[4:len(m)] + '\\' + ft[0:len(ft)-4] + '\\'; #print outPath
    outfname = outPath + f[0:len(f)-4] + '_scale_' + str(s) + '.jpg'; #print outfname	
    
    if(cv2.imwrite(outfname, img_colour) == False):
    	print 'Result not saved : %s ...' % outfname

def draw_rect_and_save_topN(dirOut, f, ft, method, img, m, result_list):

	if len(img.shape) != 3:
		# turn into colour image
		img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

	topN =len(result_list); #print topN

	for n in range(0, topN):
		(max_val, max_loc, min_loc, s, s_w, s_h) = result_list[n]
			
		# If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
		if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
			top_left = min_loc
		else:
			top_left = max_loc

		bottom_right = (top_left[0] + int(s_w), top_left[1] + int(s_h)); #print bottom_right
		
		cv2.rectangle(img, top_left, bottom_right, (0, int(round(255/(n+1))), 0), int(round(10/(n+1))))
		#cv2.imshow('result', img)
		#cv2.waitKey(0)
		#cv2.destroyAllWindows()

	outPath = dirOut + m[4:len(m)] + '\\' + ft[0:len(ft)-4] + '\\'; #print outPath
	outfname = outPath + f[0:len(f)-4] + '_topN.jpg'; #print outfname	
	
	if(cv2.imwrite(outfname, img) == False):
		print 'Result not saved : %s ...' % outfname

def draw_rect_and_save_topN_MultiClass(dirOut, f, ft, method, img, result_list, offset):

	if len(img.shape) != 3:
		# turn into colour image
		img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

	topN =len(result_list); #print topN

	for n in range(0, topN):
		(max_val, min_val, max_loc, min_loc, s_w_template, s_h_template, t_subd, t_f, i_subd, i_f, s) = result_list[n]
			
		# If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
		if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
			top_left = min_loc
		else:
			top_left = max_loc

		d_img, w_img, h_img = img.shape[::-1]
		h_offset = int(round(offset*h_img)); 
		top_left_offset = (top_left[0], top_left[1] + h_offset); print top_left_offset

		#bottom_right = (top_left[0] + int(s_w_template), top_left[1] + int(s_h_template)); #print bottom_right
		bottom_right_offset = (top_left_offset[0] + int(s_w_template), top_left_offset[1] + int(s_h_template)); #print bottom_right
		
		#cv2.rectangle(img, top_left, bottom_right, (0, int(round(255/(n+1))), 0), int(round(topN/(n+1))))
		cv2.rectangle(img, top_left_offset, bottom_right_offset, (0, int(round(255/(n+1))), 0), int(round(topN/(n+1))))
		#cv2.imshow('result', img)
		#cv2.waitKey(0)
		#cv2.destroyAllWindows()

	outPath = os.path.normpath(os.path.join(dirOut, method[4:len(method)], i_subd, f[0:len(f)-4])); #print outPath
	outfname = outPath + '_topN.jpg'; #print outfname	
	
	if(cv2.imwrite(outfname, img) == False):
		print 'Result not saved : %s ...' % outfname

def CannyEdgeDetector(img, sigma):
	### convert to edge
	# first, smooth the image
	img = cv2.GaussianBlur(img, (3,3), 0)
	# secondly, find the median of image
	median_img = np.median(img)
	# thirdly, compute upper and lower limit for Canny Edge Detector
	Canny_lower_img = int(max(0, (1.0 - sigma) * median_img))
	Canny_upper_img = int(max(255, (1.0 - sigma) * median_img))
	# finally, perform edge detection
	edge = cv2.Canny(img, Canny_lower_img, Canny_upper_img)
	return edge
#################################
if __name__ == "__main__":
	print 'This is myutils.py'