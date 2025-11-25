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