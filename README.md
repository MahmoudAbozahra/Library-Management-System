📚 Library Management System

A Django-based web application to manage a library. It supports user registration, authentication, book management (add, edit, delete), category management, search functionality, and role-based authorization (admin, workers, and customers).

🚀 Features:

User Authentication:

User Registration

User Login & Logout

Password Validation

Authorization (Roles & Permissions):

Admin:

Full control: Add, edit, delete books & categories.

Workers:

Can edit book details.

Cannot add or delete books.

Customers:

Can view books only.

Book Management:

Add new books (admin only)

Edit existing books (admin & workers)

Delete books (admin only)

Categorize books

Search Functionality:

Search books by title.

🛠️ Technology Stack:

Backend: Django 5.x

Frontend: Bootstrap 4, HTML5, CSS3

Database: MySQL 

Authentication & Authorization: Django built-in auth system, Groups & Permissions

