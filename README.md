
# CardDAVEncodePicturesFromUrl

This script processes a Google Contacts export so contact images and birthdays are displayed correctly when imported.

- An export from Google Contact is including contact images as an URLs, but this is not understood by common imports.
Imports expect the image to be included as base64 coded into the VCF file.
- Birthdays are not recognized by iCloud. iCloud expects the format 1964-06-02 while some birthdates are in a format
19640602 which is not understood by iCloud.

Running the script on an Contacts export will fix this.

Tested with Synolgy Contacts and iCloud Contacts on Google export.

 Note that iCloud has certain limits on vCard size. Max size per contact is 256 k, contacts with larger images might
 not get imported properly by iCloud Contacts. Avoid contact images over 256 k.

