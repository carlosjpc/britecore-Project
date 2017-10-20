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

To have this app running in your computer follow this steps:

1) Clone the repository
  git clone https://github.com/carlosjpc87/proyectoBritcore.git

2) Create a virtual Environment and install requirements.txt
  if your on Linux: $ pip install -r path/requirements.txt

3) Set up your a database:
  if your using Postgres please install psycog2: $ pip install psycopg2

4) Configure DB connection and your .csv folder:
  from the app root directory go to trial_app/insurance_data/settings.config
  Provide a path to your UPLOAD_FOLDER: 'your_path/proyectoBritcore/trial_app/uploads'
  Provide DB connection: 'postgresql://user:password@localhost/db_name'

5) Navigate to /proyectoBritcore type:
  5.1) python run.py db init      (generates a Migrations folder, where Alembic
                                   will create the scripts to update your DB)
  5.1) python run.py db migrate    (generates the script from models.py to
                                    create the tables required for the app to work)
  5.1) python run.py db upgrade    (runs the script, you should see the tables
                                    created in your db)

  ![Alt text](https://user-images.githubusercontent.com/977013/31831687-e80965da-b589-11e7-97a9-6e0fdc179a14.jpg?raw=true "Star Schema")

6) Go to your web browser to 127.0.0.1:5000/file_upload/ and upload finalapi.csv
   which you can download from here: https://www.kaggle.com/moneystore/agencyperformance

7) When uploaded it will take you to a preview, click yes and the app will
   generate the star schema and save it to the DB.

8) the app has to endpoints accesible at:
  8.1) the facts endpoint lets you query the facts table passing any of the
       following parameters: agency_id, date_id, risk_id and/or product_id and
       returns the query as JSON. (http://127.0.0.1:5000/facts/)
  8.2) the report endpoint lets you create csv files where the facts table,
       converted to a pandas dataframe is goruped by one or more of the columns
       mentioned on point 8.1 and apply a pandas aggregation functions like sum()
       the last optional parameter allows the coupling of the resulting data
       frame with a dimension, to analyse the possible effects of changes in that
       dimension with the aggregated data in facts.
