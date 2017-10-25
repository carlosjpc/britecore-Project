# proyectoBritcore

based on this assignment: https://github.com/IntuitiveWebSolutions/DataTeamProject

this api has three endpoints: <br />

  1) Facts: '/facts/' <br />
  Allows to filter the table facts by 'agency_id', 'product_id', 'date_id' and 'risk_id',
  this are foreign keys referencing to their respective dimension. In the facts schema,
  this four columns have a unique constraint. <br />

  This endpoint returns a facts sub table, that is returned as JSON <br />


  2) Reports: '/report/' <br />
  Creates reports taking three arguments: <br />
    a) pandas 'groupby', this argument can be repeated. <br />
    b) to produce a data frame we need the second argument: calulate, which allows to apply:
       sum, mean, size and describe to the groupby object. <br />
    c) explore_dim allows to pair the resulting DataFrame with a dimension, thus making
       possible to explore the impact of variables in the dimension table with the
       aggregated data in the DataFrame. <br />


  3) PDF Reports: '/pdf_report/' <br />
  Returns a pdf comparing the industry numbers to those of one agency. <br />
    a) It takes 'agency_id', 'product_id', 'date_id' and 'risk_id' and 'line_type'
    as parameters for comparison. <br />
    b) Agency_id must be provided and is the agency which will be compared to all
    other agencies in the DB. <br />
    c) at least one argument must be left blank, so that the comparison runs along
    that dimension values. <br />

  For the pdf creation to work you must install wkhtmltopdf, which can't be done
  with pip, you must download and install https://wkhtmltopdf.org/downloads.html,
  if your using MacOs that's it, if Windows please adjust line 20 in views.py to
  point to your wkhtmltopdf.exe file. <br />



for ease of use route /file_upload/ allows the uploading a file .csv to the DB,
the route /save_file_to_db/<filename>/<dim>/ gives a preview of the file uploaded [GET]
and if confirmed saves the file to the DB. The dim variable allows to select which dimension
of the table to save to the DB. <br />

It is important to note that a DB schema is not being created, but populated by
the upload process. <br />
