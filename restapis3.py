from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import json
import os

app = Flask(__name__)

# Configure your AWS credentials and S3 bucket name

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY') 
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY') 
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')


# Initialize the S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

@app.route('/api/movies', methods=['GET'])
def get_movies():
    try:
        filename = request.args.get('filename', 'movies.json')
        file_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=filename)
        file_content = file_obj['Body'].read().decode('utf-8')
        json_content = json.loads(file_content)
        return jsonify(json_content), 200
    except s3_client.exceptions.NoSuchKey:
        return jsonify({"error": "File not found"}), 404
    except (NoCredentialsError, PartialCredentialsError) as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/movies/<name>/<int:year>', methods=['PUT'])
def update_movie(name, year):
    try:
        filename = request.args.get('filename', 'movies.json')
        # Get the existing JSON object
        file_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=filename)
        file_content = file_obj['Body'].read().decode('utf-8')
        json_content = json.loads(file_content)

        # Update the JSON object
        movie_exists = False
        for movie in json_content:
            if movie['name'].lower() == name.lower() and movie['year'] == year:
                movie.update(request.get_json())
                movie_exists = True
                break
        
        if not movie_exists:
            json_content.append({"name": name, "year": year, **request.get_json()})

        # Save the updated JSON object back to S3
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=filename, Body=json.dumps(json_content))

        return jsonify({"message": "Movie updated successfully"}), 200
    except s3_client.exceptions.NoSuchKey:
        return jsonify({"error": "File not found"}), 404
    except (NoCredentialsError, PartialCredentialsError) as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/movies/query', methods=['GET'])
def query_movies():
    try:
        filename = request.args.get('filename', 'movies.json')
        movie_name = request.args.get('name')
        movie_year = request.args.get('year')

        # Get the existing JSON object
        file_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=filename)
        file_content = file_obj['Body'].read().decode('utf-8')
        json_content = json.loads(file_content)

        # Filter movies based on name and/or year
        filtered_movies = [
            movie for movie in json_content
            if (movie_name is None or movie['name'].lower() == movie_name.lower()) and
               (movie_year is None or str(movie['year']) == movie_year)
        ]

        if not filtered_movies:
            return jsonify({"error": "No movies found matching the query"}), 404

        return jsonify(filtered_movies), 200
    except s3_client.exceptions.NoSuchKey:
        return jsonify({"error": "File not found"}), 404
    except (NoCredentialsError, PartialCredentialsError) as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
