# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
HEADINGS = ['Variable', 'Mip Table', 'Expression', 'Comments', 'Dimensions', 'Units', 'Component', 'Status', 'File']
HEADER_ROW_TEMPLATE = ('  <thead>\n   <tr bgcolor="{0}">\n{1}   </tr>\n   \
                       <tr class="filters">\n{2}   </tr>\n   </thead>\n')
ROW_TEMPLATE = '  <tr bgcolor="{}">\n{}  </tr>\n'
CELL_TEMPLATE = '     <{0}>{1}</{0}>\n'
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
<link rel="stylesheet" type="text/css" charset="UTF-8"
href="https://cdn.datatables.net/2.3.2/css/dataTables.dataTables.min.css"/>
<script type="text/javascript" charset="UTF-8" src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script type="text/javascript" charset="UTF-8" src="https://cdn.datatables.net/2.3.2/js/dataTables.min.js"></script>
<script type="text/javascript">
$(document).ready(function () {
  var table = $('#table_id').DataTable({
    orderCellsTop: true,
    fixedHeader: true,
    pageLength: 100,
    initComplete: function () {
      var api = this.api();

      // Show the tables once DataTables has initialized
      $('#table_id').css('visibility', 'visible');

      // For each column, add a select filter to the second row
      api.columns().eq(0).each(function (colIdx) {
        var cell = $('.filters th').eq(colIdx);
        if (cell.length) {
          var select = $('<select><option value="">All</option></select>')
            .appendTo(cell.empty())
            .on('change', function () {
              api.column(colIdx)
                .search(this.value ? '^' + this.value + '$' : '', true, false)
                .draw();
            });

          api.column(colIdx).data().unique().sort().each(function (d) {
            if (d) select.append('<option value="' + d + '">' + d + '</option>');
          });
        }
      });
    }
  });
});
</script>
</head>
<style>

  /* Hide table until DataTables has fully initialized */
    #table_id {
    visibility: hidden;
   }

  /* Format the datatables */
  table.dataTable {
    table-layout: fixed;
    width: 100%;
  }

  table.dataTable td {
    max-width: 300px;
    white-space: normal;
    word-wrap: break-word;
  }

  pre, code {
    white-space: pre-wrap;
    word-break: break-word;
  }

  table.dataTable thead select {
    width: 100%;
    box-sizing: border-box;
    padding: 4px;
    font-size: 0.9em;
  }

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
     width: 600px;
     background-color: #FFFFFF;
     color: black;
     text-align: left;
     padding: 18px;
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
