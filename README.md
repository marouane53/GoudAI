# GoudAI

GoudAI is an AI-powered journalist that generates high-quality articles in Moroccan Arabic Darija based on a given topic. It utilizes the Anthropic API for language generation and the SERP API for retrieving relevant search results.

## Installation

1. Clone the repository:
   git clone https://github.com/marouane53/GoudAI.git
2. Install the required dependencies:
   pip install -r requirements.txt
   
4. Replace the `ANTHROPIC_API_KEY` and `SERP_API_KEY` variables in the code with your own API keys.

## Usage

1. Run the script:
python goudai.py

2. Enter a topic to write about when prompted.

3. Choose whether you want an automatic edit after the initial draft by entering 'yes' or 'no'.

4. The script will generate search terms, retrieve relevant URLs, and generate an article based on the collected information.

5. The generated article will be saved as a text file with the formatted title.

6. If you opted for an automatic edit, the edited article will also be saved as a separate text file.

## Acknowledgements

This code is inspired by and heavily modified from a project by [mshumer](https://github.com/mshumer). Errors from the original code have been fixed and additional functionality has been added.

## License

This project is licensed under the [MIT License](LICENSE).


