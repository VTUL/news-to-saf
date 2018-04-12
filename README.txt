This script processes a zipped folder of Virginia Tech News articles sent by Univeristy Relations.
(Bruce Harper, http://search.vt.edu/search/person.html?person=817435, emailed me the batch in 2010.)

Each item in the VT News collection, https://vtechworks.lib.vt.edu/handle/10919/19073, 
contain an html file and associated image files. 
For instance,  “Science magazine features sustainability in the Caribbean,” 
https://vtechworks.lib.vt.edu/handle/10919/63880, contains bitstreams,


122010-science-fallmag.html, 
https://vtechworks.lib.vt.edu/bitstream/handle/10919/63880/122010-science-fallmag.html?sequence=1&isAllowed=y, 

and 

M_122010-science-fallmag.jpg, 
https://vtechworks.lib.vt.edu/bitstream/handle/10919/63880/M_122010-science-fallmag.jpg?sequence=2&isAllowed=y.

122010-science-fallmag.html contains 

    <p><img src="images/M_122010-science-fallmag.jpg" alt="Fall 2010 College of Science Magazine" /></p>

which loads M_122010-science-fallmag.jpg when the URL for 122010-science-fallmag.html is selected.


How does the link to images/M_122010-science-fallmag.jpg actually goes to M_122010-science-fallmag.jpg?

This is a feature of DSpace. When an html file is in an item as a primary content file, 
relative links in the html document are resolved by the 
DSpace webapp to the base filename (no path) within that item.

I think there should either be a DSpace documentation about the subject,
or else notes in Colin’s old scripts where he tweaked html and/or moved associated resources.

Notes:

https://wiki.duraspace.org/plugins/servlet/mobile?contentId=68064792#content/view/68064792

and, in the “HTML content in items” section:

https://wiki.duraspace.org/plugins/servlet/mobile?contentId=68064847#ApplicationLayer-HTMLContentinItems
