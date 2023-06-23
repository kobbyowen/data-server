# DataServer Package

The DataServer package allows you to quickly spin up a full fake REST API without writing any code. It takes JSON or CSV files as a data source and generates the API endpoints based on the data provided.

# Installation

To use the FakeAPI package, you need to set up a virtual environment using venv and install the required dependencies.

1. Open a terminal and navigate to the project directory.

2. Create a virtual environment by running the following command:
   `python -m venv venv`

3. Activate the virtual environment:
   On Windows:
   `venv\Scripts\activate.bat`

   On macOS and Linux:
   `source venv/bin/activate`

4. Install the data_server package by running the command:
   `pip install data_server`

# Usage

To run the DataServer package, follow these steps:

1. Prepare your JSON or CSV file as the data source for the API. Make sure the file follows the expected structure.

2. Run the package's command directly from the terminal with the format below:
   data_server file [options]
3. The API will start running, and you will see the following output:
   WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.

   - Running on [http://127.0.0.1:2000](http://127.0.0.1:2000)
     Press ##CTRL+C to quit
   - Restarting with stat

4. You can now access the API endpoints by making HTTP requests to [http://127.0.0.1:2000](http://127.0.0.1:2000)

   GET requests will retrieve data from the API.
   POST requests will add new data to the API.
   PUT requests will update existing data in the API.
   DELETE requests will remove data from the API.
   The specific endpoints and available operations will be automatically generated based on the structure of your JSON or CSV file.

5. To stop the API, press ##CTRL+C in the terminal.

# Command-Line Arguments

The DataServer package uses the argparse library to parse command-line arguments. Here are the available arguments that you can use:

usage: data_server file [options]

positional arguments:
file The path of a JSON or CSV file to serve

optional arguments:
--host HOST The host the server runs on. Defaults to 127.0.0.1
--port PORT The server port. Defaults to 2000
--static-folder STATIC_FOLDER
A path to a folder to serve static files from
--static-url-prefix STATIC_URL_PREFIX
The URL path prefix used to serve static files
--url-path-prefix URL_PATH_PREFIX
A prefix that should be added to every request URL
--additional-headers ADDITIONAL_HEADERS
Additional headers to add to every response
--sleep-before-request SLEEP_BEFORE_REQUEST
Number of milliseconds to wait before sending a response for a request
--disable-stdin Disable stdin if the server is run in a subprocess

controller arguments:
--page-size PAGE_SIZE
The default page size. Can be changed by using 'size'
--page-param-name PAGE_PARAM_NAME
A URL param name used to control paging. Defaults to 'page'
--sort-param-name SORT_PARAM_NAME
A URL param name used to control sorting. Defaults to 'sort_by'
--order-param-name ORDER_PARAM_NAME
An order param name used to control ordering. Defaults to 'order'
--size-param-name SIZE_PARAM_NAME
A URL param name used to control the size of resources returned per request. Defaults to 'size'
--created-at-key-name CREATED_AT_KEY_NAME
The created at key name. Defaults to 'created_at'
--updated-at-key-name UPDATED_AT_KEY_NAME
The updated at key name. Defaults to 'updated_at'
--id-name ID_NAME The name of the key denoting the ID of a resource. Defaults to 'id'
--auto-generate-ids AUTO_GENERATE_IDS
Determines whether IDs should be auto-generated during a POST request. Defaults to True
--use-timestamps USE_TIMESTAMPS
Determines whether timestamps should be added during a POST request and modified after every change to the resource. Defaults to True

# Example Data Files

The examples directory in the project contains sample JSON and CSV files that you can use to test the DataServer package. Feel free to explore these files to understand the required structure.

# Acknowledgments

This package is built using Python and leverages the Werkzeug library for creating the REST API endpoints.

# License

This project is licensed under the MIT License. See the LICENSE file for details.
