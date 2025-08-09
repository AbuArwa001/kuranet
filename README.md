# KuraNet

## Overview
KuraNet is a robust online polling system API built with the Django Rest Framework. It serves as the backend for a platform where users can create, manage, and participate in polls. The API provides secure and well-documented endpoints for a wide range of functionalities, from user authentication to real-time results display. This documentation is designed to serve as a comprehensive guide for developers looking to integrate with or contribute to the project. The system is designed to be scalable and uses a token-based authentication system to ensure all interactions are secure. The API's architecture allows for seamless integration with any front-end application, providing a solid foundation for a dynamic and interactive user experience.

## Table of Contents
- [KuraNet](#kuranet)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [API Endpoints](#api-endpoints)
    - [Authentication](#authentication)
    - [Users](#users)
    - [Polls](#polls)
  - [📊 Entity Relationship Diagram (ERD)](#-entity-relationship-diagram-erd)
  - [🚧 Setup Git Hooks (Required)](#-setup-git-hooks-required)
  - [🛠️ Development Setup](#️-development-setup)
    - [Prerequisites](#prerequisites)
    - [Setup GitFlow](#setup-gitflow)
    - [Clone the Repository](#clone-the-repository)
    - [Install Dependencies](#install-dependencies)
  - [⚙️ Project Structure](#️-project-structure)
  - [🏃 Running the Application](#-running-the-application)
  - [🧪 Testing the Application](#-testing-the-application)
  - [Postman Collection](#postman-collection)
  - [License](#license)

## Features
* **User Authentication**: The API provides a secure and stateless authentication mechanism using JSON Web Tokens (JWTs). Users can register, log in to receive an access token, and refresh their access token when it expires. This ensures that sensitive endpoints are protected and that only authenticated users can perform actions like creating polls or voting.
* **Poll Creation**: Authenticated users have the ability to create new polls. A poll is defined by a central question and a set of multiple-choice options. The system allows for flexibility in poll creation, enabling users to craft engaging and relevant polls for the community.
* **Poll Participation**: The core functionality of the platform is voting. Users can cast their vote on any active poll by selecting one of the available options. The system enforces a one-vote-per-user-per-poll rule to maintain the integrity of the results.
* **Results Display**: Vote results are not static. The API provides endpoints that deliver real-time updates on poll outcomes, including total vote counts for each option and their respective percentages. This dynamic feedback loop keeps users engaged and informed.
* **Admin Panel**: KuraNet leverages Django's built-in administrative interface. This panel provides administrators with powerful tools to manage user accounts, oversee all created polls, and handle moderation tasks. It is a vital component for the maintenance and governance of the platform.

## API Endpoints
This section provides a summary of the available API endpoints, grouped by functionality. The API base URL is `https://liwomasjid.co.ke/api/v1`. All authenticated requests must include an `Authorization: Bearer <access_token>` header.

### Authentication
| **Method** | **Endpoint** | **Description** |
|---|---|---|
| `POST` | `/users/auth/register/` | Register a new user account. |
| `POST` | `/users/auth/login/` | Log in with username and password to get `access` and `refresh` tokens. |
| `POST` | `/users/auth/refresh/` | Use the `refresh` token to get a new `access` token. |
| `POST` | `/users/auth/logout/` | Invalidate the current `access` token. |

### Users
| **Method** | **Endpoint** | **Description** |
|---|---|---|
| `GET` | `/users/` | List all users (requires authentication). |
| `GET` | `/users/{id}/` | Get details for a specific user by their ID. |
| `PUT` | `/users/{id}/` | Update user details. The request body should contain the fields to be updated. |
| `POST` | `/users/{id}/deactivate/` | Deactivate a user's account. |

### Polls
| **Method** | **Endpoint** | **Description** |
|---|---|---|
| `POST` | `/polls/` | Create a new poll. Request body requires a `question` and an `is_active` status. |
| `GET` | `/polls/` | List all available polls, including their questions and options. |
| `POST` | `/polls/{id}/options/` | Add a new option to a specific poll. The request body should contain the `option_text`. |
| `PUT` | `/polls/{id}/options/{option_id}/` | Update an option for a specific poll. The request body should contain the new `option_text`. |
| `POST` | `/polls/{id}/votes/` | Cast a vote on a specific poll option. Request body requires `option_id`. |
| `GET` | `/polls/{id}/votes/` | Get the vote results for a specific poll, showing the count for each option. |

## 📊 Entity Relationship Diagram (ERD)

```mermaid
---
config:
  layout: elk
  look: handDrawn
  theme: neo
title: POLL SYSTEM
---
erDiagram
	direction LR
	USERS {
		int userID PK ""  
		string username  ""  
		string email  ""  
		string password_hash  ""  
	}
	ROLES {
		int roleID PK ""  
		int userID FK ""  
		string RoleName  "Admin, Creator, User"  
	}
	POLLS {
		int pollID PK ""  
		int userID FK ""  
		string title  ""  
		string description  ""  
		datetime creationDate  ""  
		datetime closingDate  ""  
		string status  ""  
	}
	POLL_OPTIONS {
		int optionID PK ""  
		string optionText  ""  
	}
	VOTES {
		int voteID PK ""  
		int userID FK ""  
		int pollID FK ""  
		int optionID FK ""  
		datetime timestamp  ""  
	}

	USERS||--o{POLLS:"creates"
	USERS||--||ROLES:"creates"
	POLLS||--o{POLL_OPTIONS:"has"
	POLL_OPTIONS||--o{VOTES:"is_for"
	USERS||--o{VOTES:"casts"

	style VOTES stroke:#000000

	VOTES:::Ash
<<<<<<< HEAD

=======
>>>>>>> release/0.1.93
```
The ERD above visually represents the relationships between the core entities of the KuraNet application. It shows how a `USER` can create `POLL`s and cast `VOTE`s. Each `POLL` has multiple `POLLOPTION`s, and each `VOTE` is linked to a specific option. The `RESULT` entity aggregates the votes for each poll and its options.

## 🚧 Setup Git Hooks (Required)
This project uses Git hooks to automate tasks and enforce code quality standards before commits are made. This helps to prevent common errors, maintain a consistent codebase, and streamline the development workflow. To set up the hooks, run the following command after cloning the repository:

```bash
./tools/git-hooks/setup-hooks.sh
```

## 🛠️ Development Setup

### Prerequisites
To ensure a smooth development experience, it is highly recommended to use GitFlow for managing your branching and commit strategy. This workflow helps to organize the development process by providing a clear structure for features, hotfixes, and releases.

### Setup GitFlow
* Install GitFlow if not already installed.
    1. For macOS users, you can use Homebrew:
    ```bash
    brew install git-flow
    ```
    2. For Ubuntu users, you can use apt:
    ```bash
    sudo apt-get install git-flow
    ```
    3. For Windows users, download the installer from the [GitFlow GitHub repository](https://github.com/nvie/gitflow).
* Initialize GitFlow in your repository:
    ```bash
    git flow init
    ```

### Clone the Repository
git clone [ https://github.com/AbuArwa001/kuranet.git ](https://github.com/AbuArwa001/kuranet.git)
```bash

cd kuranet
```

### Install Dependencies
1. Create a virtual environment to isolate project dependencies:
```bash
python3 -m venv venv
```
2. Activate the virtual environment:
```bash
source .venv/bin/activate
```
3. Install the project's required Python packages from the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

## ⚙️ Project Structure
The project follows a standard Django application structure. Key directories and files include:
* `kuranet/`: The main Django project folder.
* `polls/`: A Django app containing models, views, and serializers related to polls.
* `users/`: A Django app for user authentication and management.
* `tools/`: Contains the Git hooks and other development scripts.
* `requirements.txt`: Lists all project dependencies.

## 🏃 Running the Application
1. After setting up dependencies, apply the database migrations to set up the schema:
```bash
python manage.py migrate
```
2. Start the development server. The API will be accessible at `http://127.0.0.1:8000/`:
```bash
python manage.py runserver
```

## 🧪 Testing the Application
To ensure the stability and correctness of the application, you can run the provided test suite.
```bash
python manage.py test
```
This command will execute all unit and integration tests, providing feedback on the application's functionality.

## Postman Collection
A Postman collection with all the API endpoints is provided in the `Kuranet_API.postman_collection.json` file. You can import this file into your Postman client to get started quickly. The collection is pre-configured with a base URL variable and includes test scripts that automatically capture and set access/refresh tokens after a successful login, streamlining your testing workflow.

## License
This project is licensed under the MIT License.
