# KuraNet
## Overview
Its an Online Polling System API that allows users to create and participate in polls. The API is built using Django Rest Framework and provides endpoints for user authentication, poll management, voting, and results display.

## Features
- **User Authentication**: Secure login and registration for users.
- **Poll Creation**: Users can create polls with multiple options.
- **Poll Participation**: Users can vote on existing polls.
- **Results Display**: Real-time results of polls are displayed to users.
- **Admin Panel**: Admins can manage users and polls.

## 🚧 Setup Git Hooks (Required)

Run this after cloning:

```bash
./tools/git-hooks/setup-hooks.sh
```

## 🛠️ Development Setup

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
## 🏃 Running the Application

```bash