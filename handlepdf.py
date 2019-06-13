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
		if serrors[i][2] != '' and i!=0:
			path_source = serrors[i][1]
			print(path_source + '\n\n')
			path_source = path_source.replace(' ', '\ ')
			qpages = int(serrors[i][2])
			serrors[i][2] = ''
			with open(serrors[i][1], "rb") as pdf1_in:
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

def GenerateReport(id_source,spath,cf,new):
	from os import system
	if new:
		import csv
		system ('mkdir -p docclass_output')
		with open('docclass_output/report.csv', 'w') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			filewriter.writerow([id_source,spath,cf])
	else:
		import csv
		with open('docclass_output/report.csv', 'a') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			filewriter.writerow([id_source,spath,cf])

"""def GenerateDoc(id_gen,source_pdfs,abrev,folder,jpg,x1,y1,x2,y2,img_num,doc_num):
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
	
	os.system('rm -r -f docclass/')"""


while True: 
	print('Press P to create a pdf list | H to handle pdf actions of report.csv')
	V = input()
	if (V=='P' or V=='p' or V=='H' or V=='h'):
		break

if (V=='P' or V=='p'):
    source_pdfs = pathmapping('','**/*.pdf',True,False)
    GenerateReport('ID Source','Source Path','CF',True)
    for npdf, path in source_pdfs:
        GenerateReport(npdf,path,'',True)

else:
	# Make validation images for docs identifying
	makevals()
