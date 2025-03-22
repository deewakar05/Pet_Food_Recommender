from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def convert_markdown_to_html(text):
    # First, handle the section headers (e.g., "1. Recommended Food Types")
    text = re.sub(r'^\d+\.\s+(.*?)\*\*', r'**\1**', text, flags=re.MULTILINE)
    
    # Convert **text** to <strong>text</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Convert *text* to <strong>text</strong>
    text = re.sub(r'\*(.*?)\*', r'<strong>\1</strong>', text)
    
    # Remove any remaining numbers at the start of lines
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Convert bullet points
    text = re.sub(r'^\s*\*\s+', '• ', text, flags=re.MULTILINE)
    
    # Convert numbered lists (only where actually needed)
    text = re.sub(r'(?m)^(\d+)\.\s+(.+)$', r'<li>\2</li>', text)
    text = re.sub(r'(?s)(<li>.*?</li>)+', r'<ol>\g<0></ol>', text)
    
    # Convert line breaks to <br> tags
    text = text.replace('\n', '<br>')
    
    # Add some spacing between sections
    text = text.replace('<br><br>', '</p><p>')
    
    # Wrap the entire content in paragraphs
    text = f'<p>{text}</p>'
    
    # Clean up any remaining formatting issues
    text = text.replace('<p><br>', '<p>')
    text = text.replace('<br></p>', '</p>')
    text = text.replace('<p><ol>', '<ol>')
    text = text.replace('</ol></p>', '</ol>')
    
    return text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend_food():
    data = request.json
    pet_type = data.get('pet_type')
    age = data.get('age')
    weight = data.get('weight')
    activity_level = data.get('activity_level')
    dietary_restrictions = data.get('dietary_restrictions', '')

    prompt = f"""
    Please provide a well-structured recommendation for pet food with the following details:

    Pet Information:
    - Type: {pet_type}
    - Age: {age} years
    - Weight: {weight} kg
    - Activity Level: {activity_level}
    - Dietary Restrictions: {dietary_restrictions}

    Please format your response in the following sections:

    1. **Recommended Food Types**
    - List the best food options
    - Include both wet and dry food recommendations
    - Mention any specific formulas or varieties

    2. **Daily Portion Sizes**
    - Specify exact amounts in grams/cups
    - Include frequency of meals
    - Adjust based on activity level

    3. **Feeding Schedule**
    - Provide a detailed daily schedule
    - Include timing for each meal
    - Mention any special considerations

    4. **Nutritional Considerations**
    - List important nutrients
    - Explain their benefits
    - Mention any supplements if needed

    5. **Brand Recommendations**
    - Suggest specific brands
    - Include price ranges
    - Mention any special features

    Please use **bold** for important information and maintain clear section breaks.
    """

    try:
        response = model.generate_content(prompt)
        # Convert markdown to HTML
        html_response = convert_markdown_to_html(response.text)
        return jsonify({
            'success': True,
            'recommendations': html_response
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 