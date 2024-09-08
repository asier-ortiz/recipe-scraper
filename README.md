
# Recipe Scraper

This project is a **web scraper** developed for one of my **side projects**. It extracts recipe data from a website and saves it as JSON. The scraped data will be used in a larger personal project I'm working on. Follow the steps below to set up the scraper on your local machine.
## Prerequisites

Make sure you have **Python 3.7+** installed. You can check your version with:

```bash
python --version
```

If you don’t have Python installed, you can download it from the official Python website: [https://www.python.org/](https://www.python.org/)

## Setup

1. **Clone the repository** (or download the project files):
    ```bash
    git clone https://github.com/yourusername/recipe-scraper.git
    cd recipe-scraper
    ```

2. **Create a virtual environment**:
    You need to create a virtual environment to manage the project dependencies.

    - On macOS/Linux:
        ```bash
        python3 -m venv venv
        ```
    - On Windows:
        ```bash
        python -m venv venv
        ```

3. **Activate the virtual environment**:

    - On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    - On Windows:
        ```bash
        venv\Scripts\activate
        ```

4. **Install the project dependencies**:
    Once the virtual environment is activated, install the dependencies from the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

5. **Run the script**:
    You can now run the scraping script:

    ```bash
    python main.py
    ```

6. **Deactivate the virtual environment** (when done):
    To exit the virtual environment, use the following command:

    ```bash
    deactivate
    ```

## Files

- `main.py`: The main Python script to scrape recipe data.
- `requirements.txt`: Contains the list of project dependencies.

## License

This project is licensed under the MIT License.
