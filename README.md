# Real-Time Chat Application

## Overview
This is a real-time chat application built using Python, Django, and Redis. The application allows users to send and receive messages in real-time via WebSockets. It focuses on functionality over design, ensuring robust and efficient communication.

## Features
- User registration, login, and logout.
- Create chat rooms with users.
- Send and receive real-time messages.
- Error handling and logging (logs are saved in `debug.log`).
- Message throttling (1 message per second).
- Unit and integration tests covering all features.
- GitHub Actions for CI/CD, Docker setup, and testing.
- SILK for monitoring.

## Tech Stack
- **Backend**: Django, Django Channels, Redis, Daphne
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose
- **Testing and Monitoring**: Unit tests, Integration tests, SILK monitoring
- **CI/CD**: GitHub Actions

## Setup Instructions
### Prerequisites
- Docker
- Docker Compose
- Make (optional, but simplifies command execution)

### Steps
1. **Clone the Repository**
   ```sh
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. **Build and Run the Application**

    - Using Make:
   ```sh
   make run
   ```
   - Or using Docker Compose directly:
   ```sh
    docker-compose up --build
   ```
3. You can Create a Superuser
   - Using Make:
      ```sh
         make run
      ```
   - Or using Docker Compose directly:
      ```sh
        docker-compose exec web python manage.py createsuperuser
      ```
4. You can run Tests
    - Using Make:
      ```sh
         make run
      ```
   - Or using Docker Compose directly:
      ```sh
        docker-compose exec web python manage.py test 
       ```

## Usage Instructions
1.  **Register or Login**
   - Open the application in your browser.
   - Register a new user by providing your name, last name, and email and password or login with yoy credentials.

2. **Create Another User**
- To chat, create another user (use an incognito window for convenience).


3. **Start Chatting** 
- Select the user you want to chat with from the list on the index page.
- Enter the chat room and start messaging.
- Refresh the page to see that messages are retained.


## Additional Commands

- You can find additional command in ```Makefile```

## Additional Commands

- Visit ```/silk``` on your local server to access SILK monitoring.

## Logging

All API calls and errors are logged in ```debug.log```

## Deployment

The application is not deployed but is set up to run locally using Docker.

## API Throttling

Throttling is implemented in the chat consumer, limiting users to one message per second.

## Conclusion 

This project demonstrates a robust implementation of a real-time chat application
with efficient message handling, user management, and real-time capabilities using Django, Redis, and Docker. 
Follow the setup instructions to get started and explore the features.