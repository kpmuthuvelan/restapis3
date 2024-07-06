
* Architecture Diagram

  [Client] ----> [RestAPI Server] ----> [AWS S3]
  
  Can can be anything from curl, postman, python (requests), powershell (Invoke-WebRequest), etc
  
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
- Use the Dockerfile, docker-compose.yml and requirements.txt
- Push to dockerhub using following instructions
	- docker build -t dockerhub_username/movies-api .
	- docker push dockerhub_username/movies-api

Kubernetes
- Check kubernetes folder for kubernetes yaml to deploy to a kubernetes cluster
