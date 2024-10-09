'''
    Emailkasten - a open-source self-hostable email archiving server
    Copyright (C) 2024  David & Philipp Aderbauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''   
''' 
    The following code is a modified version of code from xme's emlrender project https://github.com/xme/emlrender.
    Original code by Xavier Mertens, licensed under the GNU General Public License version 3 (GPLv3).
    Modifications by David & Philipp Aderbauer, licensed under the GNU Affero General Public License version 3 (AGPLv3).
    This modified code is part of an AGPLv3 project. See the LICENSE file for details.
'''

import email
import email.header
import imgkit
import os
import quopri
import base64
import hashlib
import logging
from PIL import Image
from .fileManagment import getPrerenderImageStoragePath
from .mailParsing import ParsedMailKeys
from .constants import ProcessingConfiguration, ParsingConfiguration


logger = logging.getLogger(__name__)

def _combineImages(imagesList):
    logger.debug("Combining image parts ...")
    backgroundColor=(255,255,255)
    widths, heights = zip(*(i.size for i in imagesList))

    new_width = max(widths)
    new_height = sum(heights)
    new_im = Image.new('RGB', (new_width, new_height), color = backgroundColor)
    offset = 0
    for images in imagesList:
        # x = int((new_width - im.size[0])/2)
        x = 0
        new_im.paste(images, (x, offset))
        offset += images.size[1]
    
    logger.debug("Successfully combined image parts.")
    return new_im
    


def prerender(parsedMail):
    logger.debug("Generating prerender image for mail ...")

    dumpDir = ProcessingConfiguration.DUMP_DIRECTORY
    # Create the dump directory if not existing yet
    if not os.path.isdir(dumpDir):
        os.makedirs(dumpDir)
        logger.debug(f"Created dump directory {dumpDir}")

    message = email.message_from_bytes(parsedMail[ParsedMailKeys.DATA])
        
    dirtyChars = [ '\n', '\\n', '\t', '\\t', '\r', '\\r']
    
    imgkitOptions = { 'load-error-handling': 'skip'}
    # imgkitOptions.update({ 'quiet': None })
    imagesList = []
    attachments = []

    #
    # Main loop - process the MIME parts
    #
    for part in message.walk():
        if part.is_multipart():
            logger.debug('Multipart found, continue')
            continue
        
        if not part.get_content_disposition():
            mimeType = part.get_content_type()
            charset = part.get_content_charset() or ParsingConfiguration.CHARSET_DEFAULT

            logger.debug(f'Found MIME part: {mimeType}')
            if mimeType.startswith('text/'):
                
                try:
                    payload = quopri.decodestring(part.get_payload(decode=True)).decode(charset, errors='replace')
                except:
                    payload = str(quopri.decodestring(part.get_payload(decode=True)))[2:-1]
                
                # Cleanup dirty characters in html
                if mimeType == 'text/html':
                    for char in dirtyChars:
                        payload = payload.replace(char, '')
                
                # Insert other text into html format
                else: 
                    payload = ProcessingConfiguration.HTML_FORMAT % payload
                
                
                # Generate MD5 hash of the payload
                m = hashlib.md5()
                m.update(payload.encode(charset))
                imagePath = m.hexdigest() + '.png'
                try:
                    imgkit.from_string(payload, dumpDir + '/' + imagePath, options = imgkitOptions)
                    logger.debug(f'Decoded {imagePath}')
                    imagesList.append(os.path.join(dumpDir, imagePath))
                except Exception as e:
                    logger.warning(f'Decoding this MIME part of type {mimeType} returned error {e}')
                    
            elif mimeType.startswith('image/'):
                payload = part.get_payload(decode=False)
                imgdata = base64.b64decode(payload)
                # Generate MD5 hash of the payload
                m = hashlib.md5()
                m.update(payload.encode(charset, errors='replace'))
                imagePath = m.hexdigest() + '.' + mimeType.split('/')[1]
                try:
                    with open(dumpDir + '/' + imagePath, 'wb') as f:
                        f.write(imgdata)
                    logger.debug(f'Decoded {imagePath}')
                    imagesList.append(os.path.join(dumpDir, imagePath))
                except Exception as e:
                    logger.warning(f'Decoding this MIME part of type {mimeType} returned error {e}')
                    
            else:
                fileName = part.get_filename() or f"{hash(part)}.attachment"
                attachments.append(f"{fileName} ({mimeType})")
                logger.debug(f'Added attachment {fileName} of MIME type {mimeType}')
        else:
            fileName = part.get_filename() or f"{hash(part)}.attachment"
            attachments.append(f"{fileName} ({mimeType})")
            logger.debug(f'Added attachment {fileName} of MIME type {mimeType}')

    if attachments:
        footer = '<p><hr><p><b>Attached Files:</b><p><ul>'
        for a in attachments:
            footer = footer + '<li>' + a + '</li>'
        m = hashlib.md5()
        m.update(footer.encode('utf-8'))
        imagePath = m.hexdigest() + '.png'
        try:
            imgkit.from_string(footer, dumpDir + '/' + imagePath, options = imgkitOptions)
            logger.debug(f'Created footer {imagePath}')
            imagesList.append(os.path.join(dumpDir, imagePath))
        except Exception as e:
            logger.warning(f'Creation of footer failed with error {e}')
    else:
        logger.debug("No attachments found for rendering.")

    if imagesList:
        renderImageFilePath = getPrerenderImageStoragePath(parsedMail)
        images = list(map(Image.open, imagesList))
        combinedImage = _combineImages(images)
        logger.debug(f"Saving prerender image at {renderImageFilePath} ...")
        combinedImage.save(renderImageFilePath)
        logger.debug(f"Successfully saved prerender image at {renderImageFilePath}.")
        # Clean up temporary images
        for image in imagesList:
            os.remove(image)
    else:
        logger.debug("No images rendered.")