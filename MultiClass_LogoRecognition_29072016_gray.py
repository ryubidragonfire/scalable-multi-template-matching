# MultiClass_Logo_Recognition_29072016.py

import cv2
import myutils as mu
import csv
import errno
import sys
from matplotlib import pyplot as plt
import numpy as np
import os
import argparse

def main():

### User input

	argparser = argparse.ArgumentParser(description='This script will take a list of images and a list of template to perform template matching.')
	argparser.add_argument('-i', '--dirIn', help='Input directory', required=True)
	argparser.add_argument('-o', '--dirOut', help='Output directory', required=True)
	argparser.add_argument('-t', '--dirTemplate', help='Template directory', required=True)
	argparser.add_argument('-r', '--resultFile', help='Result filename', required=True)
	argparser.add_argument('-m', '--method', help='Template matching methods, e.g. cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF_NORMED', required=True)
	argparser.add_argument('-sn', '--saveTopN', help='Save top N number of matches detected in a single image, e.g. True, False', required=True)
	argparser.add_argument('-mt', '--max_val_threshold', help='Threshold for max_val, which is the result of template matching, e.g. 0.70', required=True)
	args = argparser.parse_args()

	dirIn = args.dirIn
	dirOut = args.dirOut
	dirTemplate = args.dirTemplate
	fnameResult = args.resultFile
	method = args.method
	max_val_threshold = args.max_val_threshold

### Configuration
	saveAllResultImages = False
	saveTopNResultImages = args.saveTopN
	#saveTopNResultImages = False

	#scaling = np.linspace(0.1, 1, 1) # just do one for testing
	scaling = np.linspace(0.03, 0.3, 28) # see "about_2016_07_25.txt"

	topN = 5

### create output directory dirOut if it does not exist
	image_subdir = os.listdir(dirIn)

	for i_subdir in image_subdir:
		subdirNew = os.path.normpath(os.path.join(dirOut, method[4:], i_subdir))

		try:
			os.makedirs(subdirNew)
			print subdirNew	+ " created ..."
		except OSError as exc:
			if exc.errno == errno.EEXIST and os.path.isdir(subdirNew):
				pass
			else:
				raise
	
### open a file to write results to
	fnameResult_path = os.path.normpath(os.path.join(dirOut, method[4:len(method)], fnameResult))
	if not os.path.exists(fnameResult_path):
		f_row = open(fnameResult_path, 'w')
		writer_row = csv.writer(f_row, delimiter='\t')
	else:
		print('Result file already os.path.exists!')
		sys.exit()

### open a file to write topN results to
	fname_topNResult_path = os.path.join(dirOut, method[4:len(method)], fnameResult[0:len(fnameResult)-4])
	fname_topNResult_path = fname_topNResult_path + '_topN.tsv'
	if not os.path.exists(fname_topNResult_path):
		f_topN_row = open(fname_topNResult_path, 'w')
		writer_topN_row = csv.writer(f_topN_row, delimiter='\t')
	else:
		print('Result file already os.path.exists!')
		sys.exit()

### Loop patern: group -> image -> group -> template
	template_subdir = os.listdir(dirTemplate)
	image_subdir = os.listdir(dirIn)

	for i_subd in image_subdir: # directory for test images
		i_subd_path = os.path.join(dirIn, i_subd)

		if os.path.isdir(i_subd_path): # group
			print 'i_subd: %s' %i_subd
			i_fnames = [f for f in os.listdir(i_subd_path) if os.path.isfile(os.path.join(i_subd_path, f))]
		
			for i_f in i_fnames: # images
				print '... f: %s' %i_f
				i_fname_path = os.path.normpath(os.path.join(i_subd_path, i_f))
				img = cv2.imread(i_fname_path, 0) # read as gray
				w_img, h_img = img.shape[::-1]
				s_w_template_lowerlimit = 0.01*w_img #0.03*w_img
				s_w_template_higherlimit = 0.15*w_img #0.10*w_img
				s_h_template_lowerlimit = 0.01*h_img #0.05*h_img
				s_h_template_higherlimit = 0.35*h_img

				# search only lower half of image
				offset = 0.5
				img_searchspace = img[int(round(offset*h_img)):h_img, 0:w_img]
				#cv2.imshow(f, img_searchspace)
				#cv2.waitKey(0)
				#cv2.destroyAllWindows()

				result_list = []

				for t_subd in template_subdir: # directory for templates
					t_subd_path = os.path.join(dirTemplate, t_subd)

					if os.path.isdir(t_subd_path): # group
						print '... ... t_subd: %s' %t_subd
						t_fnames = [f for f in os.listdir(t_subd_path) if os.path.isfile(os.path.join(t_subd_path, f))] 
						
						for t_f in t_fnames: # template
							#print '... ... ... t_f: %s' %t_f
							#print 'ref_group: %s, ref_template: %s, test_image: %s, actual_group: %s, actual_template: %s, estimated_group: %s, estimated_template: %s' %(t_subd, t_f, i_f, i_subd, 'need_label', 'estimated_group', 'estimated_template' )
							t_fname_path = os.path.normpath(os.path.join(t_subd_path, t_f))
							template = cv2.imread(t_fname_path, 0) # read as gray
							w_template, h_template = template.shape[::-1]; #print w_template, h_template
							# cv2.imshow(t_fname_path, template)
							# cv2.waitKey(0)
							# cv2.destroyAllWindows()

							# calculate scale template size
							for s in scaling: # a factor of the image area
								#print '... ... ... s: %f' %s
								s_w_img = s*w_img # this is propotional image width in pixel
								s_w_template = int(s_w_img) # this is the required template width in pixel
								s_h_template = int(float(s_w_img)/float(w_template)*float(h_template)) # this is the required template height in pixel

								# let template of right propotional size relative to test image pass
								if s_w_template >= s_w_template_lowerlimit and s_w_template <= s_w_template_higherlimit:
									if s_h_template >= s_h_template_lowerlimit and s_h_template <= s_h_template_higherlimit:
										# scale template
										template_s = cv2.resize(template, (s_w_template, s_h_template))
										w_template_s, h_template_s = template_s.shape[::-1]; #print w_template_s, h_template_s
										#cv2.imshow(t_fname_path, template_s)
										#cv2.waitKey(0)
										#cv2.destroyAllWindows()

										# template matching
										result = cv2.matchTemplate(img, template_s, eval(method))
										min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
										# write result to file

										# result_vector = [ref_group, ref_template, actual_group, test_image, actual_template (need label), estimated_group (todo), estimated_template (todo)]
										result_vector = [i_subd, i_f, t_subd, t_f, s, min_val, max_val, min_loc, max_loc]
										writer_row.writerow(result_vector)
										result_list.append((max_val, min_val, max_loc, min_loc, s_w_template, s_h_template, t_subd, t_f, i_subd, i_f, s))

									else:
										#print ''' Reference template %s of size %d, %d is out of proportion to test image %s of size %d, %d ''' %(t_f, s_w_template, s_h_template, i_f, w_img, h_img)
										pass

								#print 'where am i: i_subd: %s i_f: %s t_subd: %s t_f: %s scale: %f ' %(i_subd, i_f, t_subd, t_f, s)

				# sort results for all scales, for all templates, for all groups
				#print 'where am i: i_subd: %s i_f: %s t_subd: %s t_f: %s scale: %f ' %(i_subd, i_f, t_subd, t_f, s)
				result_list.sort(key=lambda tup: tup[0], reverse=True)

				topN_within_threshold = 0

				for n in range(0,topN):
					(max_val, min_val, max_loc, min_loc, s_w_template, s_h_template, t_subd, t_f, i_subd, i_f, s) = result_list[n]; #print max_val, max_val_threshold
					if max_val >= float(max_val_threshold):
						topN_result_vector = [i_subd, i_f, t_subd, t_f, s, min_val, max_val, max_loc, min_loc]
						writer_topN_row.writerow(topN_result_vector)
						topN_within_threshold = topN_within_threshold + 1
						print 'result[%d]: estimated group: %s [actual group: %s], estimated template: %s [actual template: need labeling], max_val:%f ' %(n, t_subd, i_subd, t_f, max_val)

				# Draw the top n result onto the test image
				if (saveTopNResultImages):
					if topN_within_threshold > 0:
						mu.draw_rect_and_save_topN_MultiClass(dirOut=dirOut, f=i_f, ft=t_f, method=method, img=img, result_list=result_list[0:topN_within_threshold], offset=offset)
					print 'where am i in saveTopNResultImages: i_subd: %s i_f: %s ' %(i_subd,i_f)

	f_row.close()
	f_topN_row.close()
################################
if __name__ == "__main__":
	main()