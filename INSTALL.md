# Local Installation Guide

This guide provides detailed instructions for setting up and running the Gemini Streaming Chatbot on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python**: Version `3.13` is required. You can use a version manager like `pyenv` to install and manage Python versions.
- **uv**: A fast Python package installer and resolver. If you don't have it, you can install it with:
  ```bash
  pip install uv
  ```

## Installation Steps

1.  **Clone the Repository**:
    If you haven't already, clone the project repository to your local machine.

2.  **Navigate to the Project Directory**:
    Open your terminal and change to the project's root directory:
    ```bash
    cd path/to/backend
    ```

3.  **Set Up Python Environment**:
    It's recommended to use a virtual environment to manage dependencies. `uv` handles this automatically.

4.  **Install Dependencies**:
    Use `uv` to install the required Python packages from `pyproject.toml`. This command also creates a virtual environment if one doesn't exist.
    ```bash
    uv sync
    ```

5.  **Activate the Virtual Environment**:
    To use the installed packages, you need to activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```
    Your terminal prompt should now indicate that you are in the virtual environment.

6.  **Set Up Environment Variables**:
    The application requires a Gemini API key to function.
    - Create a file named `.env` in the root of the project directory.
    - Add your API key to the `.env` file as follows:
      ```
      GEMINI_API_KEY='your_gemini_api_key_here'
      ```
    **Note**: Never commit the `.env` file to version control. It should be listed in your `.gitignore` file.

## Running the Application

Once you have completed the installation steps, you can start the web server.

1.  **Start the Development Server**:
    The project is configured with a convenient script to run the development server with hot reloading.
    ```bash
    uv run dev
    ```
    Alternatively, you can run `uvicorn` directly:
    ```bash
    uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
    ```

2.  **Access the Application**:
    The application will be running at `http://localhost:8000`.

3.  **View API Documentation**:
    For interactive API documentation, navigate to `http://localhost:8000/docs` in your web browser. This will open the Swagger UI, where you can view and test all available endpoints.

## Verifying the Installation

To ensure everything is set up correctly, you can perform the following checks:

- **Health Check**: Open your browser or use a tool like `curl` to access the health check endpoint:
  ```bash
  curl http://localhost:8000/api/v1/chat/health
  ```
  You should receive a response indicating the service is healthy.

- **Chat Endpoint**: Use the interactive docs or `curl` to send a test message to the chat endpoint.

## Troubleshooting

- **Command `uv` not found**: Make sure you have installed `uv` and that its installation directory is in your system's `PATH`.
- **ModuleNotFoundError**: Ensure you have activated the virtual environment (`source .venv/bin/activate`) before running the application.
- **Authentication Errors**: Double-check that your `GEMINI_API_KEY` is correctly set in the `.env` file and that the API key is valid.
