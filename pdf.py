import requests
from pdfminer.high_level import extract_text
from io import BytesIO


def pdf_to_text(url):
    response = requests.get(url)
    pdf_file = BytesIO(response.content)

    text = extract_text(pdf_file)
    return text


def create_chunks(text, chunk_size, overlap):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i+chunk_size]
        chunks.append(' '.join(chunk))
    return chunks


def abs_to_pdf(url):
    return url.replace('abs', 'pdf')

# # Example usage
# url = 'https://arxiv.org/pdf/2304.13343.pdf'
# pdf_text = pdf_to_text(url)
# chunks = create_chunks(pdf_text, 300, 50)
#
# print(len(chunks))

