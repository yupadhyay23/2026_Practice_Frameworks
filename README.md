# 2026_Practice_Frameworks Setup Instructions

1. Clone the repository:
git clone https://github.com/yupadhyay23/2026_Practice_Frameworks.git
cd 2026_Practice_Frameworks

2. Create a Python virtual environment:
python -m venv .venv

3. Activate the virtual environment:
- On Windows (PowerShell):
  .venv\Scripts\activate
- On macOS / Linux:
  source .venv/bin/activate

4. Install project dependencies:
pip install -r requirements.txt

5. Set up environment variables:
- Copy the example file:
  cp .env.example .env
  (On Windows, manually duplicate the file instead)
- Open the newly created .env file and add your API keys or any required environment variables.
⚠️ Do not commit your .env file to GitHub.

6. Run the project:
python main.py
(Replace main.py with your project’s entry file if different)

7. When finished, you can deactivate the virtual environment:
deactivate
