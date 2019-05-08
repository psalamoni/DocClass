import csv

def pathmapping(folder,parameter,recursive,lastint):
	def intsort(elem):
		startnum = elem.rfind('_')+1
		endnum = elem.rfind('.')
		elem = int(elem[startnum:endnum])
		return elem
	import glob
	files = glob.glob(folder + parameter, recursive=recursive)
	if lastint:
		files = sorted(files, key=intsort)
	else:
		files.sort()
	return enumerate(files)

def pdftojpg(pdfs):
	import csv
	from os import system
	from pdf2image import convert_from_path

	with open('pdf2jpg_done.csv', 'a') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',quotechar='"')
		for i, pdf in pdfs:
			print('Converting ', pdf)
			dotposition = pdf.rfind('.')
			folder = 'docclass/' + pdf[0:dotposition]
			folder = folder.replace(' ','1+')
			folder = folder.replace('(','2+')
			folder = folder.replace(')','3+')
			folder = folder.replace('\'','4+')
			folder = folder.replace('&','5+')
			system ('mkdir -p ' + folder)
			print('.')

			pages = convert_from_path(pdf, 100)
			for n, page in enumerate(pages):
				saveimgpath = folder + '/' + str(i) + '_' + str(n) + '.jpg'
				page.save(saveimgpath, 'JPEG')
			filewriter.writerow([i,pdf])
			print('done')

def cropimage(folder,img,x1,y1,x2,y2,save_pattern):
	from PIL import Image
	from os import system
	slashposition = img.rfind('/')
	jpg_name = img[slashposition+1:]
	save_jpg = folder + 'croped/' + save_pattern + jpg_name
	system ('mkdir -p ' + folder + 'croped')
	img = Image.open(img)
	crop_img = img.crop((x1, y1, x2, y2))
	crop_img.save(save_jpg)

def makevals():
	from os import system

	rmfolders = pathmapping('docclass/','**/croped/',True,False)
	for i,rmfolder in rmfolders:
		system('rm -r ' + rmfolder)

	folders = pathmapping('docclass/','**/',True,False)

	for i,folder in folders:
		jpgs = pathmapping(folder,'*.jpg',False,True)
		for i,jpg in jpgs:
			print(jpg)
			cropimage(folder,jpg,100,190,730,310,'croped_txt1_')
			print('.')

def GenerateReport(id_source,spath,pages,id_gen,destination,types,docid,outcome,new):
	from os import system
	if new:
		import csv
		system ('mkdir -p docclass_output')
		with open('docclass_output/report.csv', 'w') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			filewriter.writerow([id_source,spath,pages,id_gen,destination,types,docid,outcome])
	else:
		import csv
		with open('docclass_output/report.csv', 'a') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			filewriter.writerow([id_source,spath,pages,id_gen,destination,types,docid,outcome])

def GenerateDoc(id_gen,source_pdfs,abrev,folder,jpg,x1,y1,x2,y2,img_num,doc_num):
	from PyPDF2 import PdfFileWriter, PdfFileReader
	from os import system
	import re
	import pyocr
	import pyocr.builders
	from PIL import Image

	# Get input file path
	startnum = jpg.rfind('/')
	endnum = jpg.find('_',startnum)
	id_file = int(jpg[startnum+1:endnum])
	inputfile = source_pdfs[id_file]
	inputfile = inputfile[1]
	inputpdf = PdfFileReader(open(inputfile, "rb"), strict=False)

	if doc_num is None:
		cropimage(folder, jpg, x1, y1, x2, y2,'croped_id_')

		jpg_name = jpg[startnum+1:]
		jpg_num = folder + 'croped/croped_id_' + jpg_name

		# Convert image into text mode
		tools = pyocr.get_available_tools()[0]
		text_num = tools.image_to_string(Image.open(jpg_num), builder=pyocr.builders.DigitBuilder())

		# Generate Doc Number
		doc_num = re.findall(r'\d+/\d+', text_num)

		if len(doc_num) == 0:
			doc_num = str(id_gen)
		else:
			doc_num = ''.join(doc_num[0])
			doc_num = doc_num.replace('/','.')

	output_folder = 'docclass_output/' + abrev + '/'

	# Preparing folder to recieve pdfs
	system ('mkdir -p ' + output_folder )

	# Creating pdf file
	output = PdfFileWriter()
	for pagenw in reversed(img_num):
		output.addPage(inputpdf.getPage(pagenw))

	# Check Classification
	if (abrev == 'ERROR'):
		outcome = "Error Doc Type"
	elif (doc_num == str(id_gen)):
		outcome = "Error Doc Num"
	else:
		outcome = "Successful"

	# Saving pdf and creating report
	with open(output_folder + abrev + ' ' + str(id_gen) + '.pdf', "wb") as outputStream:
	        output.write(outputStream)
	pages = str(img_num.pop()+1)
	if len(img_num) >0:
		img_num.reverse()
		pages = pages + '-' + str(img_num.pop()+1)
	img_num.clear()
	GenerateReport(id_file,inputfile,pages,id_gen,output_folder + abrev + ' ' + str(id_gen) + '.pdf',abrev,doc_num,outcome, False)

	# Update tuple id
	id_gen += 1
	return id_gen

def imageanalise(id_gen,source_pdfs,folders):
	from fuzzywuzzy import fuzz
	from fuzzywuzzy import process
	import os
	import pyocr
	import pyocr.builders
	import re
	from PIL import Image

	# Creating a report file id_source,spath,pages,id_gen,destination,types,docid,outcome
	GenerateReport('ID Source','Source Path','Pages','ID Destination','Destination','Type','Doc ID','Outcome', True)

	# Verify subfolder in main folder
	for i,folder in folders:
		vals = pathmapping(folder,'croped/croped_txt1_*.jpg',False,True)
		pdf_pages_number = []
		pdf_pages_sv = []
		fdfd = list(vals)
		
		# Check for validation images inside folder
		for numpage,val in reversed(fdfd):
			print(val)
			#green_grade = 0
			im = Image.open(val)

			jpg = val.replace('croped/croped_txt1_','')

			# Saving PDF pages
			pdf_pages_number.append(numpage)
			
			# Check for green grade in image
			# for pixel in im.getdata():
			# 	if (pixel[1]>(pixel[2]+10) and pixel[1]>(pixel[0]+10)):
			# 		green_grade += 1
			
			# Check text inside main area of analises
			# if (green_grade >=200):

			# Build txt image in order to be analised
			cropimage(folder,jpg,100,120,700,270,'croped_txt1_')

			jpg_text = val.replace('val1','txt1')

			# Convert image into text mode
			tools = pyocr.get_available_tools()[0]
			text_txt1 = tools.image_to_string(Image.open(jpg_text), builder=pyocr.builders.DigitBuilder())
			print(fuzz.token_set_ratio('ALVARA', text_txt1))
			print(fuzz.token_set_ratio('HABITESSE', text_txt1))
			startnum = val.rfind('_')
			endnum = val.rfind('.')

			if fuzz.token_set_ratio('ALVARA', text_txt1) > 70 and fuzz.token_set_ratio('CUMPRIMENTO', text_txt1) < 30:

				if len(pdf_pages_number)>1:
					pdf_pages_sv.append(pdf_pages_number.pop())
					pdf_pages_sv.append(pdf_pages_number.pop())
					pdf_pages_sv.reverse()
					id_gen = GenerateDoc(id_gen,source_pdfs,'ALVARA',folder,jpg,550,180,770,330,pdf_pages_sv,None)
					print('\n ============ DOCUMENT FOUND (ALVARA) =========== \n')
					if len(pdf_pages_number)>0:
						id_gen = GenerateDoc(id_gen,source_pdfs,'NotRecon',folder,jpg,0,0,1,1,pdf_pages_number,None)
						print('\n ============ DOCUMENT NOT FOUND =========== \n')
				
				else:
					id_gen = GenerateDoc(id_gen,source_pdfs,'ALVARA',folder,jpg,550,180,770,330,pdf_pages_number,None)
					print('\n ============ DOCUMENT FOUND (ALVARA) =========== \n')

			elif fuzz.token_set_ratio('HABITESSE', text_txt1) > 70 and fuzz.token_set_ratio('VALIDAMOS', text_txt1) < 30 :
				# Saving PDF pages
				if len(pdf_pages_number)>1:
					pdf_pages_sv.append(pdf_pages_number.pop())
					pdf_pages_sv.append(pdf_pages_number.pop())
					pdf_pages_sv.reverse()
					id_gen = GenerateDoc(id_gen,source_pdfs,'HABITESSE',folder,jpg,250,260,420,300,pdf_pages_sv,None)
					print('\n ============ DOCUMENT FOUND (HABITESSE) =========== \n')
					if len(pdf_pages_number)>0:
						id_gen = GenerateDoc(id_gen,source_pdfs,'NotRecon',folder,jpg,0,0,1,1,pdf_pages_number,None)
						print('\n ============ DOCUMENT NOT FOUND =========== \n')
				else:
					id_gen = GenerateDoc(id_gen,source_pdfs,'HABITESSE',folder,jpg,250,260,420,300,pdf_pages_number,None)
					print('\n ============ DOCUMENT FOUND (HABITESSE) =========== \n')
			elif int(val[startnum+1:endnum])==0:
				id_gen = GenerateDoc(id_gen,source_pdfs,'NotRecon',folder,jpg,0,0,1,1,pdf_pages_number,None)
				print('\n ============ DOCUMENT NOT FOUND =========== \n')
			# else:
			# 	jpg_text2 = val.replace('val1','txt2')

			# 	tools = pyocr.get_available_tools()[0]
			# 	text_txt2 = tools.image_to_string(Image.open(jpg_text2), builder=pyocr.builders.DigitBuilder())

			# 	if fuzz.partial_ratio('Sistema de Tratamento de Efluentes', text_txt2) > 70:
			# 		id_gen = GenerateDoc(id_gen,source_pdfs,'STE',folder,jpg,380,60,620,130,pdf_pages_number,None)
			# 		print('\n ============ DOCUMENT FOUND (STE) =========== \n')
			# 	else:
			# 		jpg_text3 = val.replace('val1','txt3')

			# 		tools = pyocr.get_available_tools()[0]
			# 		text_txt3 = tools.image_to_string(Image.open(jpg_text3), builder=pyocr.builders.DigitBuilder())
			# 		startnum = val.rfind('_')
			# 		endnum = val.rfind('.')
			# 		doc_num = re.findall(r'r\d+/\d+|$', text_txt3)
			# 		doc_num = ''.join(doc_num[0])
			# 		doc_num = doc_num.replace('/','.')
			# 		if doc_num == '':
			# 			doc_num = str(id_gen)

			# 		if fuzz.partial_ratio('LICENGA ESPECIAL', text_txt3) > 70:
			# 			id_gen = GenerateDoc(id_gen,source_pdfs,'LE',None,jpg,0,0,0,0,pdf_pages_number,doc_num)
			# 			print('\n ============ DOCUMENT FOUND (LE) =========== \n')
			# 		elif int(val[startnum+1:endnum])==0:
			# 			id_gen = GenerateDoc(id_gen,source_pdfs,'NotRecon',None,jpg,0,0,0,0,pdf_pages_number,doc_num)
			# 			print('\n ============ DOCUMENT NOT FOUND =========== \n')
	
	os.system('rm -r -f docclass/')


while True: 
	print('Press P to convert jpg2pdf | C to crop sizeble images | A to analize images')
	V = input()
	if (V=='P' or V=='p' or V=='C' or V=='c' or V=='A' or V=='a'):
		break

if (V=='P' or V=='p'):
	while True: 
		print('Do you want to create a pdf list pdf_list.csv (Y/N)')
		S = input()
		if (S=='Y' or S=='y' or S=='N' or S=='n'):
			break
	
	while True: 
		print('Press K to keep using pdf_list.csv or C to use pdf_listt.csv')
		T = input()
		if (T=='K' or T=='k' or T=='C' or T=='c'):
			break

	if (S=='Y' or S=='y'):
		source_pdfs = pathmapping('','**/*.pdf',True,False)
		with open('pdf_list.csv', 'w') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for npdf, path in source_pdfs:
				filewriter.writerow([npdf,path])
		with open('pdf2jpg_done.csv', 'w') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',quotechar='"')
			filewriter.writerow(['ID File','File Path'])

	if (T=='C' or T=='c'):
		with open('pdf_listt.csv', 'r') as f:
			reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			source_pdfs = list(reader)
	else:
		with open('pdf_list.csv', 'r') as f:
			reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			source_pdfs = list(reader)

	# Convert PDF to JPG
	pdftojpg(source_pdfs)


elif (V=='C' or V=='c'):
	# Make validation images for docs identifying
	makevals()


else:
	while True: 
		print('Press K to keep using pdf_list.csv or C to use pdf_listt.csv')
		T = input()
		if (T=='K' or T=='k' or T=='C' or T=='c'):
			break

	if (T=='C' or T=='c'):
		with open('pdf_listt.csv', 'r') as f:
			reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			source_pdfs = list(reader)
	else:
		with open('pdf_list.csv', 'r') as f:
			reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			source_pdfs = list(reader)
	
	while True: 
		print('Do you want to create a validation list folder_list.csv (Y/N)')
		S = input()
		if (S=='Y' or S=='y' or S=='N' or S=='n'):
			break
	
	while True: 
		print('Press K to keep using folder_list.csv or C to use folder_listt.csv')
		T = input()
		if (T=='K' or T=='k' or T=='C' or T=='c'):
			break

	id_gen = 1

	if (S=='Y' or S=='y'):
		folders = pathmapping('docclass/','**/',True,False)
		with open('folder_list.csv', 'w') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for nfolder, folder in folders:
				filewriter.writerow([nfolder,folder])

	if (T=='C' or T=='c'):
		while True:
			import re
			print('Type id_gen start number')
			id_gen = input()
			id_gen = id_gen
			id_val = re.findall(r'\d+|$',id_gen)
			id_val = ''.join(id_val)
			if (id_gen==id_val):
				id_gen = int(id_gen)
				break

		with open('folder_listt.csv', 'r') as f:
			reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			folders = list(reader)
	else:
		with open('folder_list.csv', 'r') as f:
			reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			folders = list(reader)
	
	# Analise images looking for documents
	imageanalise(id_gen, source_pdfs,folders)
