# library management system api

a django rest framework project built to revise and strengthen backend
development concepts.

> **note:** this project is currently a work in progress and is being
> developed primarily for learning and revision purposes.

## goals

-   revisit django rest framework fundamentals
-   practice building production-style rest apis
-   improve project structure and code organization
-   implement authentication and permissions
-   work with serializers, viewsets, routers, and generic views
-   reinforce testing and api documentation

## planned features

-   user authentication
-   book management
-   author management
-   category management
-   borrower management
-   loan and return tracking
-   search and filtering
-   pagination
-   role-based permissions
-   api documentation

## tech stack

-   python
-   django
-   django rest framework
-   sqlite (for development)

## getting started

``` bash
git clone https://github.com/nksarps/pages
cd pages

python -m venv .venv

# windows
.venv\scripts\activate

# macos/linux
source .venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
```

## project status

🚧 under development

this project will continue to evolve as more django rest framework
concepts are implemented and explored.

## license

this project is intended for educational purposes.
