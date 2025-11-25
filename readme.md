This is 

A backend service for a Reciepe-sharing platform supporting two user types:

Customer – can view & rate Reciepes

Seller – can upload Reciepes

Swagger documentation is included for easy testing.

For running the project

If you have docker

Run 
docker-compose up --build

OR 

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

You have to register as seller or customer

Use login api to login after login the api uses JWT for authentication. After logging in, tokens are automatically stored in HTTP-only cookies.

On successful login, you'll receive JWT tokens in HTTP-only cookies. These will be automatically sent with subsequent requests after that The authentication cookies will be sent automatically by the browser.

To ensure fair usage, the API implements rate limiting:

1: 100 requests per day per user
2: Additional throttling on sensitive endpoints like login and registration

There is another app named reciepe_management

Swagger is there 

We have permissions classes for IsCustomer And IsSeller

Like Reciepee Add, Update and Delete are for IsSeller
Rating related thing is for IsCustomer

Model is for Reciepee and RecipeeImage

For a particular reciepee there can be multiple images and ratings

Rating can be from 1 to 5


Have created a asynchronus task with help of celery whenever someone upload a picture 
In delay of it will compress the picture

The compress_recipe_image task is automatically compress the images uploaded by sellers in the background. When a new recipe image is uploaded, this task runs separately using Celery so that the main API does not slow down. The task starts by fetching the image from the database using the given image ID. It then opens the image with the Pillow library. If the uploaded image has transparency, like a PNG with RGBA mode, it is first converted into a normal RGB image so that it can be saved as a JPEG. After that, the image is resized to a maximum of 1024x1024 pixels while keeping the correct aspect ratio. This resizing helps reduce the file size without making the image look stretched or distorted. Once the image is resized, it is saved into memory using JPEG format with a quality of 70, which provides a good balance between clarity and file size. The optimized image is then written back to the model using a new filename that includes "_compressed"

Have created another asyncronus task which send mails to all sellers at 6 a.m. morning except sat and sun for adding a dish

Have handled the logic of 6 a.m. and mon-fri in periodic task not through logic