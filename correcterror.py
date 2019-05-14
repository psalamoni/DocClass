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
		for i,pdfx in enumerate(pdfs):
			pdf = pdfx[1]
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
			cropimage(folder,jpg,0,0,100,100,'croped_val1_')
			cropimage(folder,jpg,50,240,790,330,'croped_txt2_')
			cropimage(folder,jpg,100,70,700,160,'croped_txt3_')
			print('.')

def GenerateReport(id_source,spath,pages,id_gen,destination,types,docid,outcome,CF,new):
	from os import system
	if new:
		import csv
		system ('mkdir -p docclass_output')
		with open('docclass_output/report.csv', 'w') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			filewriter.writerow([id_source,spath,pages,id_gen,destination,types,docid,outcome,CF])
	else:
		import csv
		with open('docclass_output/report.csv', 'a') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			filewriter.writerow([id_source,spath,pages,id_gen,destination,types,docid,outcome,CF])

def GenerateDoc(id_gen,source_pdfs,abrev,folder,jpg,x1,y1,x2,y2,img_num,doc_num):
	from PyPDF2 import PdfFileWriter, PdfFileReader
	from os import system
	import re
	import pyocr
	import pyocr.builders
	from PIL import Image
	import csv

	# Get input file path
	startnum = jpg.rfind('/')
	endnum = jpg.find('_',startnum)
	id_file = int(jpg[startnum+1:endnum])
	inputfilelist = source_pdfs[id_file]
	inputfile = inputfilelist[1]
	id_file = int(inputfilelist[0])
	inputpdf = PdfFileReader(open(inputfile, "rb"))

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

	# Open list of source pdfs
	with open('pdf_list.csv', 'r') as f:
		reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
		spdfid = list(reader)

	# Change inputfile by the original source
	inputfile = spdfid[id_file]
	inputfile = inputfile[1]

	GenerateReport(str(id_file),inputfile,pages,id_gen,output_folder + abrev + ' ' + str(id_gen) + '.pdf',abrev,doc_num,outcome,'', False)

	# Update tuple id
	id_gen += 1
	return id_gen

def imageanalise(id_gen,source_pdfs,folders):
	from fuzzywuzzy import fuzz
	from fuzzywuzzy import process
	# import glob
	import pyocr
	import pyocr.builders
	import re
	from PIL import Image
	from os import system

	# Creating a report file id_source,spath,pages,id_gen,destination,types,docid,outcome
	GenerateReport('ID Source','Source Path','Pages','ID Destination','Destination','Type','Doc ID','Outcome','', True)
	id_gen = int(id_gen)

	# Verify subfolder in main folder
	for i,folder in folders:
		vals = pathmapping(folder,'croped/croped_val1_*.jpg',False,True)
		pdf_pages_number = []
		
		# Check for validation images inside folder
		for numpage,val in reversed(list(vals)):
			print(val)
			green_grade = 0
			im = Image.open(val)

			jpg = val.replace('croped/croped_val1_','')

			# Saving PDF pages
			pdf_pages_number.append(numpage)
			
			# Check for green grade in image
			for pixel in im.getdata():
				if (pixel[1]>(pixel[2]+10) and pixel[1]>(pixel[0]+10)):
					green_grade += 1
			
			# Check text inside main area of analises
			if (green_grade >=200):

				# Build txt image in order to be analised
				cropimage(folder,jpg,100,120,700,270,'croped_txt1_')

				jpg_text = val.replace('val1','txt1')

				# Convert image into text mode
				tools = pyocr.get_available_tools()[0]
				text_txt1 = tools.image_to_string(Image.open(jpg_text), builder=pyocr.builders.DigitBuilder())

				if fuzz.partial_ratio('INSTALACAO', text_txt1) > 70:
					id_gen = GenerateDoc(id_gen,source_pdfs,'LI',folder,jpg,280,400,715,475,pdf_pages_number,None)
					print('\n ============ DOCUMENT FOUND (LI) =========== \n')
				elif fuzz.partial_ratio('OPERACAO', text_txt1) > 70:
					id_gen = GenerateDoc(id_gen,source_pdfs,'LO',folder,jpg,280,400,715,475,pdf_pages_number,None)
					print('\n ============ DOCUMENT FOUND (LO) =========== \n')
				elif fuzz.partial_ratio('PREVIA', text_txt1) > 70:
					id_gen = GenerateDoc(id_gen,source_pdfs,'LP',folder,jpg,280,400,715,475,pdf_pages_number,None)
					print('\n ============ DOCUMENT FOUND (LP) =========== \n')
				elif fuzz.partial_ratio('LOCALIZACAO', text_txt1) > 70:
					id_gen = GenerateDoc(id_gen,source_pdfs,'LL',folder,jpg,100,410,715,475,pdf_pages_number,None)
					print('\n ============ DOCUMENT FOUND (LL) =========== \n')
				else:
					id_gen = GenerateDoc(id_gen,source_pdfs,'ERROR',folder,jpg,350,410,715,475,pdf_pages_number,None)
					print('\n ============ DOCUMENT FOUND (NL) =========== \n')
			else:
				jpg_text2 = val.replace('val1','txt2')

				tools = pyocr.get_available_tools()[0]
				text_txt2 = tools.image_to_string(Image.open(jpg_text2), builder=pyocr.builders.DigitBuilder())

				if fuzz.partial_ratio('Sistema de Tratamento de Efluentes', text_txt2) > 70:
					id_gen = GenerateDoc(id_gen,source_pdfs,'STE',folder,jpg,380,60,620,130,pdf_pages_number,None)
					print('\n ============ DOCUMENT FOUND (STE) =========== \n')
				else:
					jpg_text3 = val.replace('val1','txt3')

					tools = pyocr.get_available_tools()[0]
					text_txt3 = tools.image_to_string(Image.open(jpg_text3), builder=pyocr.builders.DigitBuilder())
					startnum = val.rfind('_')
					endnum = val.rfind('.')
					doc_num = re.findall(r'r\d+/\d+|$', text_txt3)
					doc_num = ''.join(doc_num[0])
					doc_num = doc_num.replace('/','.')
					if doc_num == '':
						doc_num = str(id_gen)

					if fuzz.partial_ratio('LICENGA ESPECIAL', text_txt3) > 70:
						id_gen = GenerateDoc(id_gen,source_pdfs,'LE',None,jpg,0,0,0,0,pdf_pages_number,doc_num)
						print('\n ============ DOCUMENT FOUND (LE) =========== \n')
					elif int(val[startnum+1:endnum])==0:
						id_gen = GenerateDoc(id_gen,source_pdfs,'NotRecon',None,jpg,0,0,0,0,pdf_pages_number,doc_num)
						print('\n ============ DOCUMENT NOT FOUND =========== \n')
	system('rm -r docclass/')

def processerror():
	import os
	import csv
	from PyPDF2 import PdfFileWriter, PdfFileReader
	from PIL import Image
	import numpy

	def sortDocId(Doc):
		id = int(Doc[0])
		return id
	def pageDesc(Doc):
		if not Doc[2].isdigit():
			posend = Doc[2].rfind('-')
			page = Doc[2][:posend]
		else:
			page = Doc[2]
		page = int(page)
		return page
	def onepage(var):
		if (var.find('-')!=-1):
			return var.find('-')
		else:
			pass


	with open('docclass_output/report.csv', 'r') as f:
		reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
		serrors = list(reader)
		header = serrors[0]
		serrors = serrors[1:]
		serrors = sorted(serrors, key=pageDesc, reverse=True)
		serrors = sorted(serrors, key=sortDocId)
		header = [header]
		for serror in serrors:
			header.append(serror)
		serrors = header
	
	id_gen = len(serrors)
	regendoc = []
	i=0
	while (i<len(serrors)):
		if (serrors[i][8] != '' and i!=0):
			print(serrors[i][8])
			path_source = serrors[i][4]
			stype = serrors[i][5]
			print(path_source + '\n\n\n')
			path_source = path_source.replace(' ', '\ ')

			if (serrors[i][8] == '1'):
				dest = path_source.replace(stype,'LL')
				os.system('mv -f ' + path_source + ' ' + dest)
				serrors[i][4] = dest
				serrors[i][5] = 'LL'
				serrors[i][8] = ''
				if serrors[i][3]==serrors[i][6]:
					serrors[i][7] = 'Error Doc Num'
				else:
					serrors[i][7] = 'Successful'
			elif (serrors[i][8] == '2'):
				dest = path_source.replace(stype,'LP')
				os.system('mv -f ' + path_source + ' ' + dest)
				serrors[i][4] = dest
				serrors[i][5] = 'LP'
				serrors[i][8] = ''
				if serrors[i][3]==serrors[i][6]:
					serrors[i][7] = 'Error Doc Num'
				else:
					serrors[i][7] = 'Successful'
			elif (serrors[i][8] == '3'):
				dest = path_source.replace(stype,'LI')
				os.system('mv -f ' + path_source + ' ' + dest)
				serrors[i][4] = serrors[i][4].replace(stype,'LI')
				serrors[i][5] = 'LI'
				serrors[i][8] = ''
				if serrors[i][3]==serrors[i][6]:
					serrors[i][7] = 'Error Doc Num'
				else:
					serrors[i][7] = 'Successful'
			elif (serrors[i][8] == '4'):
				dest = path_source.replace(stype,'LO')
				os.system('mv -f ' + path_source + ' ' + dest)
				serrors[i][4] = serrors[i][4].replace(stype,'LO')
				serrors[i][5] = 'LO'
				serrors[i][8] = ''
				if serrors[i][3]==serrors[i][6]:
					serrors[i][7] = 'Error Doc Num'
				else:
					serrors[i][7] = 'Successful'
			elif (serrors[i][8] == '5'):
				dest = path_source.replace(stype,'LE')
				os.system('mv -f ' + path_source + ' ' + dest)
				serrors[i][4] = serrors[i][4].replace(stype,'LE')
				serrors[i][5] = 'LE'
				serrors[i][8] = ''
				if serrors[i][3]==serrors[i][6]:
					serrors[i][7] = 'Error Doc Num'
				else:
					serrors[i][7] = 'Successful'
			elif (serrors[i][8] == '6'):
				dest = path_source.replace(stype,'STE')
				os.system('mv -f ' + path_source + ' ' + dest)
				serrors[i][4] = serrors[i][4].replace(stype,'STE')
				serrors[i][5] = 'STE'
				serrors[i][8] = ''
				if serrors[i][3]==serrors[i][6]:
					serrors[i][7] = 'Error Doc Num'
				else:
					serrors[i][7] = 'Successful'
			elif (serrors[i][8] == '7'):
				dest = path_source.replace(stype,'NotRecon')
				os.system('mv -f ' + path_source + ' ' + dest)
				serrors[i][4] = serrors[i][4].replace(stype,'NotRecon')
				serrors[i][5] = 'NotRecon'
				serrors[i][8] = ''
				serrors[i][7] = 'Error Doc Num'
			elif (serrors[i][8] == '8'):
				with open(serrors[i][4], "rb") as pdf_in:
					inputpdf = PdfFileReader(pdf_in)
					outputpdf = PdfFileWriter()
					for pagenum in range(inputpdf.numPages):
						page = inputpdf.getPage(pagenum)
						page.rotateClockwise(180)
						outputpdf.addPage(page)
					with open('docclass_output/' + stype + '/temp.pdf', "wb") as pdf_out:
						outputpdf.write(pdf_out)
				os.system('mv -f docclass_output/' + stype + '/temp.pdf ' + path_source)
				regendoc.append([serrors[i][0],serrors[i][4]])
				serrors[i][7] = 'Deleted'
				serrors[i][8] = ''
				continue
			elif (serrors[i][8] == '9'):
				if i<len(serrors)-1:
					if serrors[i][0]==serrors[i+1][0]:
						with open(serrors[i+1][4], "rb") as pdf1_in:
							inputpdf1 = PdfFileReader(pdf1_in)
							with open(serrors[i][4], "rb") as pdf2_in:
								inputpdf2 = PdfFileReader(pdf2_in)
								outputpdf = PdfFileWriter()
								for pagenum in range(inputpdf1.numPages):
									page = inputpdf1.getPage(pagenum)
									outputpdf.addPage(page)
								for pagenum in range(inputpdf2.numPages):
									page = inputpdf2.getPage(pagenum)
									outputpdf.addPage(page)
								with open('docclass_output/' + stype + '/temp.pdf', "wb") as pdf_out:
									outputpdf.write(pdf_out)
						path_dest = serrors[i+1][4]
						path_dest = path_dest.replace(' ','\ ')
						os.system('mv -f docclass_output/' + stype + '/temp.pdf ' + path_dest)
						os.system('rm ' + path_source)
						serrors[i+1][2] = serrors[i+1][2][:onepage(serrors[i+1][2])] + '-' + serrors[i][2][onepage(serrors[i][2]):]
						serrors[i][7] = 'Deleted'
						serrors[i][8] = ''
						continue
			elif (serrors[i][8] == '10'):
				serrors[i][8] = ''
				with open(serrors[i][4], "rb") as pdf1_in:
					inputpdf1 = PdfFileReader(pdf1_in)
					outputpdf1 = PdfFileWriter()
					outputpdf2 = PdfFileWriter()

					page = inputpdf1.getPage(0)
					outputpdf1.addPage(page)

					with open('docclass_output/' + stype + '/temp.pdf', "wb") as pdf_out:
						outputpdf1.write(pdf_out)

					if (inputpdf1.numPages>1):
						for pagenum in range(inputpdf1.numPages-1):
							page = inputpdf1.getPage(pagenum)
							outputpdf2.addPage(page)
						with open('docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf', "wb") as pdf_out:
							outputpdf2.write(pdf_out)
						serror = []
						serror = serrors[i].copy()
						serror[3] = id_gen
						serror[4] = 'docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf'
						serror[5] = 'NotRecon'
						serror[6] = id_gen
						serror[7] = 'Error Doc Num'
						id_gen += 1
						serrors[i][2] = str(serrors[i][2][:serrors[i][2].find('-')])
						if str(int(serror[2][:serror[2].find('-')])+1)==serror[2][int(serror[2].find('-')+1):]:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+1)
						else:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+1) + serror[2][serror[2].find('-'):]
						serrors.append(serror)
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('mv -f docclass_output/' + stype + '/temp.pdf ' + path_dest)
			elif (serrors[i][8] == '11'):
				doctype = 'HABITESSE'
				qpages = 1
				serrors[i][8] = ''
				with open(serrors[i][4], "rb") as pdf1_in:
					inputpdf1 = PdfFileReader(pdf1_in)
					outputpdf1 = PdfFileWriter()
					outputpdf2 = PdfFileWriter()

					page = inputpdf1.getPage(0)
					outputpdf1.addPage(page)

					with open('docclass_output/' + stype + '/temp.pdf', "wb") as pdf_out:
						outputpdf1.write(pdf_out)

					if (inputpdf1.numPages>qpages):
						for pagenum in range(inputpdf1.numPages-qpages):
							page = inputpdf1.getPage(pagenum+qpages)
							outputpdf2.addPage(page)
						with open('docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf', "wb") as pdf_out:
							outputpdf2.write(pdf_out)
						serror = []
						serror = serrors[i].copy()
						serror[3] = id_gen
						serror[4] = 'docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf'
						serror[5] = 'NotRecon'
						serror[6] = id_gen
						serror[7] = 'Error Doc Num'
						id_gen += 1
						if str(int(serror[2][:serror[2].find('-')])+qpages)==serror[2][int(serror[2].find('-')+1):]:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+qpages)
						else:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+qpages) + serror[2][serror[2].find('-'):]
						serrors.append(serror)
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('rm ' + path_source)
				serrors[i][2] = serrors[i][2][:onepage(serrors[i][2])]
				serrors[i][4] = 'docclass_output/' + doctype + '/' + doctype + ' ' + str(serrors[i][3]) + '.pdf'
				serrors[i][5] = doctype
				serrors[i][7] = 'Successful'
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('mv -f docclass_output/' + stype + '/temp.pdf ' + path_dest)
			elif (serrors[i][8] == '12'):
				doctype = 'HABITESSE'
				qpages = 2
				serrors[i][8] = ''
				with open(serrors[i][4], "rb") as pdf1_in:
					inputpdf1 = PdfFileReader(pdf1_in)
					outputpdf1 = PdfFileWriter()
					outputpdf2 = PdfFileWriter()

					for numpage in range(qpages):
						page = inputpdf1.getPage(numpage)
						outputpdf1.addPage(page)

					with open('docclass_output/' + stype + '/temp.pdf', "wb") as pdf_out:
						outputpdf1.write(pdf_out)

					if (inputpdf1.numPages>qpages):
						for pagenum in range(inputpdf1.numPages-qpages):
							page = inputpdf1.getPage(pagenum+qpages)
							outputpdf2.addPage(page)
						with open('docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf', "wb") as pdf_out:
							outputpdf2.write(pdf_out)
						serror = []
						serror = serrors[i].copy()
						serror[3] = id_gen
						serror[4] = 'docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf'
						serror[5] = 'NotRecon'
						serror[6] = id_gen
						serror[7] = 'Error Doc Num'
						id_gen += 1
						if str(int(serror[2][:serror[2].find('-')])+qpages)==serror[2][int(serror[2].find('-')+1):]:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+qpages)
						else:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+qpages) + serror[2][serror[2].find('-'):]
						serrors.append(serror)
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('rm ' + path_source)
				serrors[i][2] = str(serrors[i][2][:serrors[i][2].find('-')]) + '-' + str(int(serrors[i][2][:serrors[i][2].find('-')])+qpages-1)
				serrors[i][4] = 'docclass_output/' + doctype + '/' + doctype + ' ' + str(serrors[i][3]) + '.pdf'
				serrors[i][5] = doctype
				serrors[i][7] = 'Successful'
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('mv -f docclass_output/' + stype + '/temp.pdf ' + path_dest)
			elif (serrors[i][8] == '13'):
				doctype = 'HABITESSE'
				qpages = 3
				serrors[i][8] = ''
				with open(serrors[i][4], "rb") as pdf1_in:
					inputpdf1 = PdfFileReader(pdf1_in)
					outputpdf1 = PdfFileWriter()
					outputpdf2 = PdfFileWriter()

					for numpage in range(qpages):
						page = inputpdf1.getPage(numpage)
						outputpdf1.addPage(page)

					with open('docclass_output/' + stype + '/temp.pdf', "wb") as pdf_out:
						outputpdf1.write(pdf_out)

					if (inputpdf1.numPages>qpages):
						for pagenum in range(inputpdf1.numPages-qpages):
							page = inputpdf1.getPage(pagenum+qpages)
							outputpdf2.addPage(page)
						with open('docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf', "wb") as pdf_out:
							outputpdf2.write(pdf_out)
						serror = []
						serror = serrors[i].copy()
						serror[3] = id_gen
						serror[4] = 'docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf'
						serror[5] = 'NotRecon'
						serror[6] = id_gen
						serror[7] = 'Error Doc Num'
						id_gen += 1
						if str(int(serror[2][:serror[2].find('-')])+qpages)==serror[2][int(serror[2].find('-')+1):]:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+qpages)
						else:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+qpages) + serror[2][serror[2].find('-'):]
						serrors.append(serror)
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('rm ' + path_source)
				serrors[i][2] = str(serrors[i][2][:serrors[i][2].find('-')]) + '-' + str(int(serrors[i][2][:serrors[i][2].find('-')])+qpages-1)
				serrors[i][4] = 'docclass_output/' + doctype + '/' + doctype + ' ' + str(serrors[i][3]) + '.pdf'
				serrors[i][5] = doctype
				serrors[i][7] = 'Successful'
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('mv -f docclass_output/' + stype + '/temp.pdf ' + path_dest)
			elif (serrors[i][8] == '14'):
				doctype = 'ALVARA'
				qpages = 1
				serrors[i][8] = ''
				with open(serrors[i][4], "rb") as pdf1_in:
					inputpdf1 = PdfFileReader(pdf1_in)
					outputpdf1 = PdfFileWriter()
					outputpdf2 = PdfFileWriter()

					for numpage in range(qpages):
						page = inputpdf1.getPage(numpage)
						outputpdf1.addPage(page)

					with open('docclass_output/' + stype + '/temp.pdf', "wb") as pdf_out:
						outputpdf1.write(pdf_out)

					if (inputpdf1.numPages>qpages):
						for pagenum in range(inputpdf1.numPages-qpages):
							page = inputpdf1.getPage(pagenum+qpages)
							outputpdf2.addPage(page)
						with open('docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf', "wb") as pdf_out:
							outputpdf2.write(pdf_out)
						serror = []
						serror = serrors[i].copy()
						serror[3] = id_gen
						serror[4] = 'docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf'
						serror[5] = 'NotRecon'
						serror[6] = id_gen
						serror[7] = 'Error Doc Num'
						id_gen += 1
						if str(int(serror[2][:serror[2].find('-')])+qpages)==serror[2][int(serror[2].find('-')+1):]:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+qpages)
						else:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+qpages) + serror[2][serror[2].find('-'):]
						serrors.append(serror)
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('rm ' + path_source)
				serrors[i][2] = serrors[i][2][:onepage(serrors[i][2])]
				serrors[i][4] = 'docclass_output/' + doctype + '/' + doctype + ' ' + str(serrors[i][3]) + '.pdf'
				serrors[i][5] = doctype
				serrors[i][7] = 'Successful'
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('mv -f docclass_output/' + stype + '/temp.pdf ' + path_dest)
			elif (serrors[i][8] == '15'):
				doctype = 'ALVARA'
				qpages = 2
				serrors[i][8] = ''
				with open(serrors[i][4], "rb") as pdf1_in:
					inputpdf1 = PdfFileReader(pdf1_in)
					outputpdf1 = PdfFileWriter()
					outputpdf2 = PdfFileWriter()

					for numpage in range(qpages):
						page = inputpdf1.getPage(numpage)
						outputpdf1.addPage(page)

					with open('docclass_output/' + stype + '/temp.pdf', "wb") as pdf_out:
						outputpdf1.write(pdf_out)

					if (inputpdf1.numPages>qpages):
						for pagenum in range(inputpdf1.numPages-qpages):
							page = inputpdf1.getPage(pagenum+qpages)
							outputpdf2.addPage(page)
						with open('docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf', "wb") as pdf_out:
							outputpdf2.write(pdf_out)
						serror = []
						serror = serrors[i].copy()
						serror[3] = id_gen
						serror[4] = 'docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf'
						serror[5] = 'NotRecon'
						serror[6] = id_gen
						serror[7] = 'Error Doc Num'
						id_gen += 1
						if str(int(serror[2][:serror[2].find('-')])+qpages)==serror[2][int(serror[2].find('-')+1):]:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+qpages)
						else:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+qpages) + serror[2][serror[2].find('-'):]
						serrors.append(serror)
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('rm ' + path_source)
				serrors[i][2] = str(serrors[i][2][:serrors[i][2].find('-')]) + '-' + str(int(serrors[i][2][:serrors[i][2].find('-')])+qpages-1)
				serrors[i][4] = 'docclass_output/' + doctype + '/' + doctype + ' ' + str(serrors[i][3]) + '.pdf'
				serrors[i][5] = doctype
				serrors[i][7] = 'Successful'
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('mv -f docclass_output/' + stype + '/temp.pdf ' + path_dest)
			elif (serrors[i][8] == '16'):
				doctype = 'ALVARA'
				qpages = 3
				serrors[i][8] = ''
				with open(serrors[i][4], "rb") as pdf1_in:
					inputpdf1 = PdfFileReader(pdf1_in)
					outputpdf1 = PdfFileWriter()
					outputpdf2 = PdfFileWriter()

					for numpage in range(qpages):
						page = inputpdf1.getPage(numpage)
						outputpdf1.addPage(page)

					with open('docclass_output/' + stype + '/temp.pdf', "wb") as pdf_out:
						outputpdf1.write(pdf_out)

					if (inputpdf1.numPages>qpages):
						for pagenum in range(inputpdf1.numPages-qpages):
							page = inputpdf1.getPage(pagenum+qpages)
							outputpdf2.addPage(page)
						with open('docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf', "wb") as pdf_out:
							outputpdf2.write(pdf_out)
						serror = []
						serror = serrors[i].copy()
						serror[3] = id_gen
						serror[4] = 'docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf'
						serror[5] = 'NotRecon'
						serror[6] = id_gen
						serror[7] = 'Error Doc Num'
						id_gen += 1
						if str(int(serror[2][:serror[2].find('-')])+qpages)==serror[2][int(serror[2].find('-')+1):]:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+qpages)
						else:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+qpages) + serror[2][serror[2].find('-'):]
						serrors.append(serror)
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('rm ' + path_source)
				serrors[i][2] = str(serrors[i][2][:serrors[i][2].find('-')]) + '-' + str(int(serrors[i][2][:serrors[i][2].find('-')])+qpages-1)
				serrors[i][4] = 'docclass_output/' + doctype + '/' + doctype + ' ' + str(serrors[i][3]) + '.pdf'
				serrors[i][5] = doctype
				serrors[i][7] = 'Successful'
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('mv -f docclass_output/' + stype + '/temp.pdf ' + path_dest)
			elif (int(serrors[i][8]) > 100):
				doctype = 'NotRecon'
				qpages = int(serrors[i][8])-100
				serrors[i][8] = ''
				with open(serrors[i][4], "rb") as pdf1_in:
					inputpdf1 = PdfFileReader(pdf1_in)
					outputpdf1 = PdfFileWriter()
					outputpdf2 = PdfFileWriter()

					for numpage in range(qpages):
						page = inputpdf1.getPage(numpage)
						outputpdf1.addPage(page)

					with open('docclass_output/' + stype + '/temp.pdf', "wb") as pdf_out:
						outputpdf1.write(pdf_out)

					if (inputpdf1.numPages>qpages):
						for pagenum in range(inputpdf1.numPages-qpages):
							page = inputpdf1.getPage(pagenum+qpages)
							outputpdf2.addPage(page)
						with open('docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf', "wb") as pdf_out:
							outputpdf2.write(pdf_out)
						serror = []
						serror = serrors[i].copy()
						serror[3] = id_gen
						serror[4] = 'docclass_output/NotRecon/NotRecon ' + str(id_gen) + '.pdf'
						serror[5] = 'NotRecon'
						serror[6] = id_gen
						serror[7] = 'Error Doc Num'
						id_gen += 1
						if str(int(serror[2][:serror[2].find('-')])+qpages)==serror[2][int(serror[2].find('-')+1):]:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+qpages)
						else:
							serror[2] = str(int(serror[2][:serror[2].find('-')])+qpages) + serror[2][serror[2].find('-'):]
						serrors.append(serror)
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('rm ' + path_source)
				serrors[i][2] = str(serrors[i][2][:onepage(serrors[i][2])]) + '-' + str(int(serrors[i][2][:onepage(serrors[i][2])])+qpages-1)
				serrors[i][4] = 'docclass_output/' + doctype + '/' + doctype + ' ' + str(serrors[i][3]) + '.pdf'
				serrors[i][5] = doctype
				serrors[i][7] = 'Successful'
				path_dest = serrors[i][4]
				path_dest = path_dest.replace(' ','\ ')
				os.system('mv -f docclass_output/' + stype + '/temp.pdf ' + path_dest)
			
		i+=1
	if len(regendoc)>0:
		pdftojpg(regendoc)
		makevals()
		folders = pathmapping('docclass/','**/',True,False)
		imageanalise(id_gen,regendoc,folders)
		for i,doc in regendoc:
			doc = doc.replace(' ','\ ')
			os.system('rm ' + doc)

		with open('docclass_output/report.csv', 'r') as f:
			reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			serrorsnew = list(reader)
	
	GenerateReport('ID Source','Source Path','Pages','ID Destination','Destination','Type','Doc ID','Outcome','CF', True)
	with open('docclass_output/report.csv', 'a') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for serror in serrors[1:]:
			filewriter.writerow(serror)
		if len(regendoc)>0:
			for serror in serrorsnew[1:]:
				filewriter.writerow(serror)




processerror()

# with open('', 'w') as csvfile:
# 	filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
# 	for npdf, path in source_pdfs:
# 		filewriter.writerow([npdf,path])


# 	# Convert PDF to JPG
# 	pdftojpg(source_pdfs)


# elif (V=='C' or V=='c'):
# 	# Make validation images for docs identifying
# 	makevals()


# else:
# 	while True: 
# 		print('Press K to keep using pdf_list.csv or C to use pdf_listt.csv')
# 		T = input()
# 		if (T=='K' or T=='k' or T=='C' or T=='c'):
# 			break

# 	if (T=='C' or T=='c'):
# 		with open('pdf_listt.csv', 'r') as f:
# 			reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
# 			source_pdfs = list(reader)
# 	else:
# 		with open('pdf_list.csv', 'r') as f:
# 			reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
# 			source_pdfs = list(reader)
	
# 	while True: 
# 		print('Do you want to create a validation list folder_list.csv (Y/N)')
# 		S = input()
# 		if (S=='Y' or S=='y' or S=='N' or S=='n'):
# 			break
	
# 	while True: 
# 		print('Press K to keep using folder_list.csv or C to use folder_listt.csv')
# 		T = input()
# 		if (T=='K' or T=='k' or T=='C' or T=='c'):
# 			break

# 	id_gen = 1

# 	if (S=='Y' or S=='y'):
# 		folders = pathmapping('docclass/','**/',True,False)
# 		with open('folder_list.csv', 'w') as csvfile:
# 			filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
# 			for nfolder, folder in folders:
# 				filewriter.writerow([nfolder,folder])

# 	if (T=='C' or T=='c'):
# 		while True:
# 			import re
# 			print('Type id_gen start number')
# 			id_gen = input()
# 			id_gen = id_gen
# 			id_val = re.findall(r'\d+|$',id_gen)
# 			id_val = ''.join(id_val)
# 			if (id_gen==id_val):
# 				id_gen = int(id_gen)
# 				break

# 		with open('folder_listt.csv', 'r') as f:
# 			reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
# 			folders = list(reader)
# 	else:
# 		with open('folder_list.csv', 'r') as f:
# 			reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
# 			folders = list(reader)
	
# 	# Analise images looking for documents
# 	imageanalise(id_gen, source_pdfs,folders)
