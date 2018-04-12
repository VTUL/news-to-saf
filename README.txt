This script processes a zipped folder of Virginia Tech News articles sent by Univeristy Relations.
We parse them into individual HTML files with accompanying images, then batch import them into the VT New collection in VTechWorks, https://vtechworks.lib.vt.edu/handle/10919/19073. 

University Relations has asked for a 5-year lag before harvest. This collection contains items from 2003-2010. Items were last loaded ~2015-10-29. Since University Relations now uses a different content management system for VT news, it’s unlikely they will ship us news in the same arrangements, so the script cannot be reused. They never authorize us to directly harvest VT News. To update this collection we may have to be in contact with University Relations again to see if they are willing to send us a new batch and allow us to archive their more recent items.

Each item in the VT News collection, https://vtechworks.lib.vt.edu/handle/10919/19073, 
contain an html file and associated image files. 
For instance,  “Science magazine features sustainability in the Caribbean,” 
https://vtechworks.lib.vt.edu/handle/10919/63880, contains bitstreams,

122010-science-fallmag.html, 
https://vtechworks.lib.vt.edu/bitstream/handle/10919/63880/122010-science-fallmag.html?sequence=1&isAllowed=y, 

and 

M_122010-science-fallmag.jpg, 
https://vtechworks.lib.vt.edu/bitstream/handle/10919/63880/M_122010-science-fallmag.jpg?sequence=2&isAllowed=y.

For example, 122010-science-fallmag.html contains 

    <p><img src="images/M_122010-science-fallmag.jpg" alt="Fall 2010 College of Science Magazine" /></p>

which loads M_122010-science-fallmag.jpg when the URL for 122010-science-fallmag.html is selected.


The link to images/M_122010-science-fallmag.jpg actually goes to M_122010-science-fallmag.jpg
as a feature of DSpace. When an HTML file is in an item as a primary content file, 
relative links in the HTML document are resolved by the 
DSpace webapp to the base filename (no path) within that item.

I think there should either be a DSpace documentation about the subject,
or else notes in the old script where he tweaked html and/or moved associated resources.

Notes:

https://wiki.duraspace.org/plugins/servlet/mobile?contentId=68064792#content/view/68064792

and, in the “HTML content in items” section:

https://wiki.duraspace.org/plugins/servlet/mobile?contentId=68064847#ApplicationLayer-HTMLContentinItems
