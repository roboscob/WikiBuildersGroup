from xhtml2pdf import pisa
from bs4 import BeautifulSoup

def generatePDF(pdf_file_path, html):
    # open output file for writing (truncated binary)
    result_file = open(pdf_file_path, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        html,  # the HTML to convert
        dest=result_file)  # file handle to receive result

    # close output file
    result_file.close()


def generateTXT(txt_file_path, html):
    # open output file for writing
    result_file = open(txt_file_path, "w")

    # convert HTML to TXT
    soup = BeautifulSoup(html)
    # write the txt to output file
    result_file.write(soup.get_text('\n'))

    # close output file
    result_file.close()