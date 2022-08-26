# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
HEADINGS = ['Variable', 'Mip Table', 'Expression', 'Comments', 'Dimensions', 'Units', 'Component', 'Status', 'File']
HEADER_ROW_TEMPLATE = '  <thead><tr bgcolor="{}">\n{}  </tr></thead>\n'
ROW_TEMPLATE = '  <tr bgcolor="{}">\n{}  </tr>\n'
CELL_TEMPLATE = '   <{0}>{1}</{0}>\n'
TABLE_TEMPLATE = '<table border=1, id="table_id", class="display">\n{}</table>\n'
CODE_CELL_TEMPLATE = '   <td><pre><code>{}</code></pre></td>\n'
TOOLTIP_TEMPLATE = '<div class="tooltip">{}<span class="tooltiptext">{}</span></div>'
GITURL = 'https://github.com/MetOffice/CDDS/blob/main/mip_convert/mip_convert/process/processors.py#L{}'
GITURL_MAPPING = 'https://github.com/MetOffice/CDDS/blob/main/mip_convert/mip_convert/process/{}#L{}'
HYPERLINK = '<a href="{}">{}</a>'
BGCOLORS = ['#E0EEFF', '#FFFFFF']

HEADER = """
<html>
<head>
<link rel="stylesheet" type="text/css" charset="UTF-8" href="../src/jquery.dataTables-1.11.4.min.css" />
<script type="text/javascript" charset="UTF-8" src="../src/jquery-3.6.0.slim.min.js"></script>
<script type="text/javascript" charset="UTF-8" src="../src/jquery.dataTables-1.11.4.min.js"></script>
<script type="text/javascript">
//<![CDATA[
$(document).ready( function () {
    $('#table_id').DataTable({"pageLength": 100});
    } );
//]]>
</script>
</head>
<style>


   /* Tooltip container */
   .tooltip {
     position: relative;
     display: inline-block;
     border-bottom: 1px dotted black; /* If you want dots under the hoverable text */
   }

   /* Tooltip text */
   .tooltip .tooltiptext {
     visibility: hidden;
     bottom: 100%;
     left: 50%;
     width: 600;
     background-color: #FFFFFF;
     color: black;
     text-align: left;
     padding: 18px 18px 18px 18px;
     border-radius: 4px;
     border: 1px solid #000;

     /* Position the tooltip text - see examples below! */
     position: absolute;
     z-index: 1;
   }

   /* Show the tooltip text when you mouse over the tooltip container */
   .tooltip:hover .tooltiptext {
     visibility: visible;
   }
   </style>
<body>"""

FOOTER = """
</body>
</html>"""
