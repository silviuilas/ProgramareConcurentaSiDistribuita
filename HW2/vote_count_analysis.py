import subprocess

# Install the google-cloud-storage package using pip
subprocess.call(['pip', 'install', 'google-cloud-storage'])

from pyspark.sql import SparkSession
import datetime
from google.cloud import storage
import argparse
import json

# Parse the latest_file argument
parser = argparse.ArgumentParser()
parser.add_argument("--latest_file", help="The path to the latest file in the Cloud Storage bucket")
args = parser.parse_args()
latest_file = args.latest_file
print(latest_file)

bucket_name = 'voting-app-381012-bucket'
blob_name = '2023-03-19T15:03:59_72116/voting-app-381012.json'
destination_file_name = 'voting-app-381012.json'

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(blob_name)
blob.download_to_filename(destination_file_name)

# Create a SparkSession
spark = SparkSession.builder.appName("VoteCountAnalysis").getOrCreate()


def fillInDataMap(param, data_test, data):
    for key, vals in data_test[param].items():
        percentages = {}
        for option, votes in vals['options'].items():
            percentages[option] = votes / vals['votes']
        data[key] = {
            "votes": vals['votes'],
            "percentages": percentages
        }

# Read the input file from GCS
df = spark.read.format("csv").option("header", "true").load(latest_file)
if df.count() == 0:
    print("No rows in input file")
else:
    rows = df.collect()

    # Initialize an empty dictionary to store the counts
    data_test = {}
    countryVotes = {}
    cityVotes = {}
    # Loop through the rows and populate the dictionary
    for row in rows:
        vote_name = row[0]
        country = row[2]
        city = row[3]

        data_test['totalVotes'] = data_test.get('totalVotes', 0) + 1

        specificCountry = countryVotes.get(country, {"votes": 0, "options": {}})
        specificCountry["votes"] += 1
        specificCity = cityVotes.get(city, {"votes": 0, "options": {}})
        specificCity["votes"] += 1

        specificCountry["options"][vote_name] = specificCountry["options"].get(vote_name, 0) + 1
        specificCity["options"][vote_name] = specificCity["options"].get(vote_name, 0) + 1
        data_test["options"][vote_name] = data_test["options"].get(vote_name, 0) + 1

        countryVotes[country] = specificCountry
        cityVotes[city] = specificCity

    data_test['countryVotes'] = countryVotes
    data_test['cityVotes'] = cityVotes

    data = {}
    data['timestamp'] = datetime.datetime.now().isoformat()
    data['totalVotes'] = data_test['totalVotes']
    data['percentages'] = {}

    for option, votes in data_test['options'].items():
        data['percentages'][option] = votes / data_test['totalVotes']

    fillInDataMap('cityVotes', data_test, data)

    fillInDataMap('countryVotes', data_test, data)

    # Save the results to the analysis file in GCS
    blob = bucket.blob("analysis/" + str(datetime.datetime.now()) + ".json")

    # Convert data to JSON and upload to GCS
    blob.upload_from_string(json.dumps(data), content_type='application/json')

# Stop the SparkSession
spark.stop()
