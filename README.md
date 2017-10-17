# proyectoBritcore

based on this assignment: https://github.com/IntuitiveWebSolutions/DataTeamProject

this api has two endpoints:

  1) Filter Facts:
  Allows to filter the table facts by 'agency_id', 'product_id', 'date_id' and 'risk_id',
  this are foreign keys referencing to their respective dimension. In the facts schema,
  this four columns have a unique constraint.

  This endpoint returns a facts sub table, that is returned as JSON

  2) Reports:
  Creates reports taking three arguments:
    1) pandas 'groupby', this argument can be repeated.
    2) to produce a data frame we need the second argument: calulate, which allows to apply:
       sum, mean, size and describe to the groupby object.
    3) explore_dim allows to pair the resulting DataFrame with a dimension, thus making
       possible to explore the impact of variables in the dimension table with the
       aggregated data in the DataFrame.


for ease of use route /file_upload/ allows the uploading a file .csv to the DB,
the route /save_file_to_db/<filename>/<dim>/ gives a preview of the file uploaded [GET]
and if confirmed saves the file to the DB. The dim variable allows to select which dimension
ore table to save to the DB.

It is important to note that a DB schema is not being created, but populated by
the upload process.
