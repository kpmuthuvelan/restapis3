
* Architecture Diagram

  Simple Model
  [Client] ----> [RestAPI Server] ----> [AWS S3]

  High Availability (Needs locking in Resource Access)
	Client ---> CDN (Akamai, Cloudfare, etc)  ---> Origin Server (Rest API) ---> [AWS S3]

			           /-------k8s(service)---> k8s deployment pods ---> [AWS S3]
	Client ---> API Gateway---/
  		    (Kong, etc)	  \--------k8s(service)---> k8s deployment pods ---> [AWS S3]

	
  Client can can be anything from curl, postman, python (requests), powershell (Invoke-WebRequest), etc
  
* Create a movies.json file as [{}] in the s3 bucket

* To run the server locally
	- Set the environment varaibles for the s3 bucket access
	- pip install the packages in requirements.txt
	- python restapis3.py
	
* To interact with the server
    - To get all - curl -X GET http://127.0.0.1:5000/api/movies
    - To create/update -  curl -X PUT http://127.0.0.1:5000/api/movies/Inception2/2010 -H 'Content-Type: application/json' -d '{ "director": "me", "genre": "nothing" }'
    - Tp query based on year - curl -X GET http://127.0.0.1:5000/api/movies/query?year=2010
	- To query based on name - curl -X GET http://127.0.0.1:5000/api/movies/query?name=Inception
	- To query based on both -  curl -X GET 'http://127.0.0.1:5000/api/movies/query?name=Inception&year=2010'
	
	
Dockerize
- Review README in Dockerfiles folder
- Use the Dockerfile, docker-compose.yml and requirements.txt
- Push to dockerhub using following instructions
	- docker build -t dockerhub_username/movies-api .
	- docker push dockerhub_username/movies-api

Kubernetes
- Review README in Kubernetes folder
- Check kubernetes folder for kubernetes yaml to deploy to a kubernetes cluster

Authentication/Authorization
- Any identity provider can used.
- Authorization can performed using OAuth Server and JWT tokens.
- See below the changes to implement in the current codeusing builtin user management. Ideally should use AWS IAM Roles based access.


....
users = {
    "testuser": "testpassword"
}

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    
    if username not in users or users[username] != password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

---
@app.route('/api/movies', methods=['GET'])
@jwt_required()
def get_movies():


High Availability
- Kubernetes deployment with 3 replicas
- In order to support high availability, we need to run the server in parallel.
- In that case we need to have lock managment in place.
- Below code does optimistic locking as it just error if the file have been modified in S3.

@app.route('/api/movies/<name>/<int:year>', methods=['PUT'])

def update_movie(name, year):
    try:
        filename = request.args.get('filename', 'movies.json')
        expected_version = request.headers.get('If-Match')

        # Get the existing JSON object
        file_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=filename)
        file_content = file_obj['Body'].read().decode('utf-8')
        json_content = json.loads(file_content)

        # Get the current version
        current_version = file_obj['ETag']

        # Check for version conflict
        if expected_version and expected_version != current_version:
            return jsonify({"error": "Version conflict"}), 409
