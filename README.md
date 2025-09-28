This project is based on the FAST API Tutorials

**For Deployment Purpose we need to create a health check route which just return the response of our website which gives the surity that our website is working.**

```py
@app.get('/health')
def health_check():
    return {
        'status':'OK',
        'version': Model_version,
        'model': True/False
    }
```

- In fast api app file only routes should be there.
- So we need to Refactory the code base.
- Seperate Pydantic Model into schema/user_input.py
- Seperate City from Pydantic Model into config/city_tier
- Seperate Prediction code to model/predict.py
- Create a function to convert user input dictionary into data frame and perform prediction.
- Remove the Creation of dataframe from main route logic.
- Call the method from main route
- Add try Except for prediction(or we can use async await there)
- Add additional information such as confidence score etc.

**We can also validate the data which is getting out through the data not only We can check incoming data we can also check output data.**

- Create a prediction_response.py
- Create Pydantic Model in it for Output Response validation.
- Add response model to the endpoint

## **Containarize the Application**

1. Create Dockerfile to Build Image

```dockerfile
# Use Python 3.13 slim as base (matches your pyproject.toml requirement)
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install uv (for dependency management)
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy the rest of the application
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the app with uvicorn (binds to 0.0.0.0 for external access)
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

After creating this file Run the command

```bash
docker build -t anaskhaann/insurance_prediction_model:1.0.0 .
```

- `-t` tag name of the image
- `:` after this specify the version (default is latest)
- `.` stands for build on current directory.

**QUESTION FOR THIS**

#### Why copy only dependecies and install them and after that install the entire application

Docker builds images by executing the instructions in your Dockerfile sequentially. It caches the result of each step. If a step (and its context, i.e., files used in COPY commands) hasn't changed since the last build, Docker reuses the cached layer instead of re-running the instruction.

Here's why the current approach is better:

1. Separate Dependency Installation
   The steps are structured to isolate the dependency installation:

```dockerfile
# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project
```

**The dependency files (pyproject.toml, uv.lock) rarely change once your project is stable.**

If you only change your application code (the main Python files, HTML templates, etc.), the COPY pyproject.toml uv.lock ./ step remains the same.

Because that step and all preceding steps haven't changed, Docker reuses the cached layer for the subsequent RUN uv sync... step. This means dependencies are not reinstalled every time you make a code change, making your local build much faster.

2. Copying the Full Application Later
   The full application is copied afterward:

```dockerfile
# Copy the rest of the application
COPY . .
```

When you make a change to your application code (e.g., in app/main.py), this COPY . . step will break the cache, as the contents being copied have changed.

However, since the dependency installation step (`RUN uv sync`...) came before this line, it's able to hit the cache, saving significant time.

3. Why Not Copy Everything at Once?
   If you were to copy everything at once, like this:

```dockerfile

# This is the less optimal way

COPY . . # <-- Copies ALL files, including pyproject.toml, source code, etc.

RUN uv sync --frozen --no-install-project
```

Any change to any file in your project (even a single line of Python code) will cause the COPY . . layer to be invalidated.

Since the `RUN uv sync`... step follows the invalidated COPY step, it would also be invalidated and would re-run the dependency installation every single time you build the image, even for minor code changes. This would drastically slow down your development cycle and CI/CD pipelines.

In summary, separating the dependency files from the main application files allows the expensive step of installing dependencies to be cached and reused unless the dependencies themselves (i.e., pyproject.toml or uv.lock) change. This is standard practice for optimizing Docker image builds.

## **Run the Container for testing**

Run with custom container name

```bash
docker run --name testing_container -p 8000:8000 -d anaskhaann/insurance_prediction_model:1.0.0
```

```bash
docker run --name your_custom_container_name -p yourmachinePort:PortExposedFromImage -d image_name
```

## **Push The image to HUB**

Simply run the commands in order

```bash

# command one to login
docker login
# Enter your credential

# After that push image to hub
# docker push image_name
docker push anaskhaann/insurance_prediction_model:1.0.0
```

## **Testing**

- Delete image from system
  `docker rmi anaskhaann/insurance_prediction_model:1.0.0`

- Pull image
  `docker pull anaskhaann/insurance_prediction_model:1.0.0`

- Run and Test
  `docker run --name test -p 8000:8000 -d anaskhaann/insurance_prediction_model:1.0.0`

- Go to `localhost:8000` and test the `/predict` route

## **Final Steps for Deployment**

We will use AWS Cloud Service.
Create account on AWS.
Select Services and Choose EC2 Instance.

1. create an EC2 instance:

- Set name (test_app)
- select os(we choose ubuntu)
- select the hardware i.e Instance Type(we choose t2.micro for free usage)
- Create Key-Pair(SSH for Login remotely)
- Select Network settings. Dont change much in this just make sure that allow ssh traffic from anywhere should be checked and set to `0.0.0.0/0`
- Configure Storage
- Click Launch Instance to Create a EC2 Instance

2. Connect to the EC2 instance(test_app)

- This can be done using putty like software by uploading `.pem` file for remote access.
- But we will directly connect from console
- The new terminal window will get Open.

3. Run the following commands:
   a. sudo apt-get update
   b. sudo apt-get install -y docker.io # install docker
   c. sudo systemctl start docker # start docker
   d. sudo systemctl enable docker # enable docker for auto start with ec2 instance
   e. sudo usermod -aG docker $USER # used to grant permission to pull image from external server
   f. exit # to restart the terminal

4. Restart a new connection to EC2 instance
5. Run the following commands
   a. Pull the Image

   ```bash
   docker pull anaskhaann/insurance_prediction_model:1.0.0
   ```

   b. Run the Container

   ```bash
   docker run --name -p 8000:8000 -d anaskhaann/insurance_prediction_model:1.0.0
   ```

   Now we can access

6. Go to Instance Page:

- Copy the Public IPv4 address to check
- The problem is we cannot send `https`, because we have not have ssl certificates
- We Still cannot access So to fix this Change the Security Settings Because no external ip can acces it.

7. Select Instance `->` Go to Security `->` Go to Security Groups:

- Define the Rules that any external source can talk with our port 8000
- Edit Inbound Rule
- Add new rule `Custom TCP` `->` Define Port `8000` `->` Select source to anywhere.

8. Check the API By visiting the Public IPv4 address.
9. Change the frontend code to have the url of the Public IPv4
