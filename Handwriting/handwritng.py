import io
import os

# Imports the Google Cloud client library
# from google.cloud import vision
# from google.cloud.vision import types

# # Instantiates a client
# client = vision.ImageAnnotatorClient()

# # The name of the image file to annotate
# file_name = os.path.join(
#     os.path.dirname(__file__),
#     'IMG_20190601_185159.jpg')

# # Loads the image into memory
# with io.open(file_name, 'rb') as image_file:
#     content = image_file.read()

# image = types.Image(content=content)

# # Performs label detection on the image file
# response = client.label_detection(image=image)
# labels = response.label_annotations

# print('Labels:')
# for label in labels:
#     print(label.description)

def detect_document(path):
    """Detects document features in an image."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.document_text_detection(image=image)
    s=''

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
           # print('\nBlock confidence: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
                #print('Paragraph confidence: {}'.format(
                   # paragraph.text))

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    #print('Word text: {} (confidence: {})'.format(
                       # word_text, word.confidence))

                    for symbol in word.symbols:
                        #print('\tSymbol: {} (confidence: {})'.format(
                         #   symbol.text, symbol.confidence))
                        s += symbol.text
                    s+= ' '
        print('{}'.format(s))

detect_document('IMG_20190601_195041.JPG')