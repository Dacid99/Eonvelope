# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# The following code is a modified version of code from xme's emlrender project https://github.com/xme/emlrender.
# Original code by Xavier Mertens, licensed under the GNU General Public License version 3 (GPLv3).
# Modifications by David & Philipp Aderbauer, licensed under the GNU Affero General Public License version 3 (AGPLv3).
# This modified code is part of an AGPLv3 project. See the LICENSE file for details.

from __future__ import annotations

import base64
import email
import email.header
import hashlib
import logging
import os
import quopri
from typing import TYPE_CHECKING

import imgkit
from PIL import Image

from .constants import ParsingConfiguration, ProcessingConfiguration
from .fileManagment import getPrerenderImageStoragePath
from .mailParsing import ParsedMailKeys

if TYPE_CHECKING:
    from PIL import ImageFile


logger = logging.getLogger(__name__)

def _combineImages(imagesFileList: list[ImageFile.ImageFile]) -> Image.Image:
    """Combining multiple images into one with attention to their sizes.

    Args:
        imagesFileList: The list of images to combine.

    Returns:
        The combined image.
    """
    logger.debug("Combining image parts ...")
    backgroundColor=(255,255,255)
    widths, heights = zip(*(imageFile.size for imageFile in imagesFileList))

    newWidth = max(widths)
    newHeight = sum(heights)
    newImage = Image.new("RGB", (newWidth, newHeight), color = backgroundColor)
    offset = 0
    for images in imagesFileList:
        # xCoordinate = int((new_width - im.size[0])/2)
        xCoordinate = 0
        newImage.paste(images, (xCoordinate, offset))
        offset += images.size[1]

    logger.debug("Successfully combined image parts.")
    return newImage



def prerender(parsedMail: dict) -> None:
    """Creates a prerender image of an email.

    Args:
        parsedMail: The data of the mail to be prerendered.
    """
    logger.debug("Generating prerender image for mail ...")

    dumpDir = ProcessingConfiguration.DUMP_DIRECTORY
    # Create the dump directory if not existing yet
    if not os.path.isdir(dumpDir):
        os.makedirs(dumpDir)
        logger.debug("Created dump directory %s", dumpDir)

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

            logger.debug("Found MIME part: %s", mimeType)
            if mimeType.startswith('text/'):

                try:
                    payload = quopri.decodestring(part.get_payload(decode=True)).decode(charset, errors='replace')
                except Exception:
                    payload = str(quopri.decodestring(part.get_payload(decode=True)))[2:-1]

                # Cleanup dirty characters in html
                if mimeType == 'text/html':
                    for char in dirtyChars:
                        payload = payload.replace(char, '')

                # Insert other text into html format
                else:
                    payload = ProcessingConfiguration.HTML_FORMAT % payload


                # Generate MD5 hash of the payload
                md5 = hashlib.md5()
                md5.update(payload.encode(charset))
                imagePath = md5.hexdigest() + '.png'
                try:
                    imgkit.from_string(payload, dumpDir + '/' + imagePath, options = imgkitOptions)
                    logger.debug("Decoded %s", imagePath)
                    imagesList.append(os.path.join(dumpDir, imagePath))
                except Exception:
                    logger.warning("Decoding this MIME part of type %s returned error!", mimeType, exc_info=True)

            elif mimeType.startswith('image/'):
                payload = part.get_payload(decode=False)
                imgdata = base64.b64decode(payload)
                # Generate MD5 hash of the payload
                md5 = hashlib.md5()
                md5.update(payload.encode(charset, errors='replace'))
                imagePath = md5.hexdigest() + '.' + mimeType.split('/')[1]
                try:
                    with open(dumpDir + '/' + imagePath, 'wb') as dumpImageFile:
                        dumpImageFile.write(imgdata)
                    logger.debug("Decoded %s", imagePath)
                    imagesList.append(os.path.join(dumpDir, imagePath))
                except Exception:
                    logger.warning("Decoding this MIME part of type %s returned error!", mimeType, exc_info=True)

            else:
                fileName = part.get_filename() or f"{hash(part)}.attachment"
                attachments.append(f"{fileName} ({mimeType})")
                logger.debug("Added attachment %s of MIME type %s", fileName, mimeType)
        else:
            fileName = part.get_filename() or f"{hash(part)}.attachment"
            attachments.append(f"{fileName} ({mimeType})")
            logger.debug("Added attachment %s of MIME type %s", fileName, mimeType)

    if attachments:
        footer = '<p><hr><p><b>Attached Files:</b><p><ul>'
        for attachment in attachments:
            footer = footer + '<li>' + attachment + '</li>'
        md5 = hashlib.md5()
        md5.update(footer.encode('utf-8'))
        imagePath = md5.hexdigest() + '.png'
        try:
            imgkit.from_string(footer, dumpDir + '/' + imagePath, options = imgkitOptions)
            logger.debug("Created footer %s", imagePath)
            imagesList.append(os.path.join(dumpDir, imagePath))
        except Exception:
            logger.warning("Creation of footer failed with error!", exc_info=True)
    else:
        logger.debug("No attachments found for rendering.")

    if imagesList:
        renderImageFilePath = getPrerenderImageStoragePath(parsedMail)
        images = list(map(Image.open, imagesList))
        combinedImage = _combineImages(images)
        logger.debug("Saving prerender image at %s ...", renderImageFilePath)
        combinedImage.save(renderImageFilePath)
        logger.debug("Successfully saved prerender image at %s.", renderImageFilePath)
        # Clean up temporary images
        for image in imagesList:
            os.remove(image)
    else:
        logger.debug("No images rendered.")
