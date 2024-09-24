This project consists of a Flask backend and an Angular frontend for a realtime chat application using socketio. Follow the steps below to set up and run the application.

## Backend

1. **Set up environment**
    ```
        python3 -m venv venv
        venv\Scripts\activate
    ```

2. **Install dependencies**
    ```
        pip install -r requirements.txt
    ```

3. **Update Database URI Inside Config.py**
    ```
        SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/dbname'
    ```

4. **Run Flask App**
    ```
        python app.py
    ```

## Frontend

1. **Navigate to the client/chat-app directory**
    ```
        cd project/client/chat-app
    ```

2. **Install dependencies (node version 16.14.2)**
    ```
        npm install 
    ```

3. **Run Flask App**
    ```
        ng serve or npm start
    ```
