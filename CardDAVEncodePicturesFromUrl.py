##############################################################################
# usage:
# python CardDAVEncodePicturesFromUrl.py <input-file> <output-file>"
#
# This script reads a VCF-file, pulls the contact image from the URL and
# converts it as a base64 coded string into the output VCF file.
# Google contacts uses URL links in exports.
#
# It also reformats the birthdate from 19640602 to 1964-06-02 because
# iCloud demands this format, other CalDAV servers like Synology are more
# tolerant.
#
#
# input

# PHOTO:https://lh3.googleusercontent.com/contacts/<some_random_id>
#
# output
#
# PHOTO;ENCODING=b;TYPE=jpg:/9j/4AAQSkZJRgABAQAAAQABAAD/4gv4SUNDX1BST0ZJTE
#  UAAQEAAAvoAAAAAAIAAABtbnRyUkdCIFhZWiAH2QADABsAFQAkAB9hY3NwAAAAAAAAAAAAAA
#  AAAAAAAAAAAAEAAAAAAAAAAAAA9tYAAQAAAADTLQAAAAAp+D3er/JVrnhC+uTKgzkNAAAAAA
#  ...
##############################################################################
import sys
import re
import requests
import base64

def format_vcard_base64(b64_string, chunk_size=72):
    """
    slice b64_string into slices of size chunk_size
    :param b64_string:
    :param chunk_size:
    :return: sliced string with newlines
    """
    chunks = [b64_string[i:i+chunk_size] for i in range(0, len(b64_string), chunk_size)]
    return "\n ".join(chunks)

def fetch_and_encode_image(url):
    """
    pulls image designated by url and encodes it in base64 format
    :param url:
    :return: encoded base64 string
    """
    try:
        response = requests.get(url, stream=False)
        
        response.raise_for_status()
        
        encoded_bytes = base64.b64encode(response.content)
        
        encoded_string = encoded_bytes.decode('utf-8')
        
        return encoded_string

    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der URL: {e}")
        return None
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        return None

def copy_file_line_by_line(source_filename, destination_filename):
    """
    copies file lines by line from source_filename to destination_filename,
    searches for PHOTO entries and processes them
    :param source_filename:
    :param destination_filename:
    :return: -
    """
    photo_pattern = re.compile(r"^PHOTO:\s*(.*)\s*")
    photo_pattern2 = re.compile(r"^\s+(.*)\s")
    bday_pattern = re.compile(r"^BDAY:\s*(\d{8})\s*$")
    try:
        with open(source_filename, 'r', encoding='utf-8') as infile:
            with open(destination_filename, 'w', encoding='utf-8') as outfile:
                # flag "PHOTO" line found
                photoFound = False
                url1 = ""
                for line in infile:
                    # check for pattern "BDAY:19640602" and reformat it to "BDAY:1964-06-02"
                    match_bday = bday_pattern.match(line)
                    if match_bday:
                        bday_date = match_bday.group(1)
                        outfile.write(f"BDAY:{bday_date[0:4]}-{bday_date[4:6]}-{bday_date[6:8]}\n")
                        continue
                    # check if line starts with "PHOTO": yes -> set flag
                    # if flag "photoFound" set, check if following lines start with a space
                    # if yes, assemble content to a URL
                    # Else write complete line to output
                    if photoFound:
                        match2 = photo_pattern2.match(line)
                        url2 = ""
                        if match2:
                            url2 = match2.group(1)
                        url = url1 + url2
                        encodedImage = "PHOTO;ENCODING=b;TYPE=jpg:" + fetch_and_encode_image(url) + "\n"
                        encodedString = format_vcard_base64(encodedImage)
                        outfile.write(encodedString)
                        photoFound = False
                    else:
                        match = photo_pattern.match(line)
                        if match:
                            photoFound = True
                            url1 = match.group(1)
                        else:
                            photoFound = False
                            outfile.write(line)

    except FileNotFoundError:
        print(f"Fehler: Die Quelldatei '{source_filename}' wurde nicht gefunden.")
        sys.exit(1)
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        sys.exit(1)


if len(sys.argv) != 3:
    print("Verwendung: python VcfEncodePicturesFromUrl.py <Eingabedatei> <Ausgabedatei>")
    sys.exit(1)

argument1 = sys.argv[1]
argument2 = sys.argv[2]

copy_file_line_by_line(argument1, argument2)