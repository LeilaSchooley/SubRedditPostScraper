import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def truncate_text(text, max_len):
    """
    Truncates a given text to the maximum length specified.
    """
    if len(text) > max_len:
        text = text[:max_len]
    last_word_idx = text.rfind(' ')
    text = text[:last_word_idx] + '...' if last_word_idx != -1 else text
    return text

def clean_text(text):
    """
    Cleans a given text by removing the punctuation and the stopword if it appears at the end.
    """
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)

    # Remove punctuation from the last token
    last_token = tokens[-1]
    last_token_cleaned = ''.join([char for char in last_token if char not in string.punctuation])

    # Check if the last token without punctuation is a stopword
    if last_token_cleaned.lower() in stop_words:
        tokens = tokens[:-1] + [last_token_cleaned]

    return ' '.join(tokens)

def main():
    max_len = 250

    text = "Southern Tree Agama, also called Blue-throated Agama Acanthocercus atricollis) Length - Female 135 mm, Male 167 mm Femalee can lays 5 - 14 oval, soft-shelled eggs in a hole dug in moist soil These hatch after approximately 90 days Diet- Caterpillars, grasshoppers and beetles'"

    # Truncate the text to the max length
    truncated_text = truncate_text(text, max_len)
    print(f"Truncated Text: {truncated_text}")

    # Clean the text by removing punctuation and stopword if it appears at the end
    cleaned_text = clean_text(truncated_text)
    print(f"Cleaned Text: {cleaned_text}")

if __name__ == '__main__':
    main()
