from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# Knowledge Base
KB = {
    "dos": [
        "Aim for 7–9 hours of sleep.",
        "Drink water regularly; start your day with a glass.",
        "Include vegetables/fruit with each meal.",
        "Move your body: target 7–10k steps if appropriate for you."
    ],
    "donts": [
        "Avoid skipping meals frequently.",
        "Limit sugary drinks and ultra-processed snacks.",
        "Don't rely on supplements without professional advice.",
        "Avoid excessive screen time before bed."
    ],
    "diet_tips": [
        "Build a balanced plate: 1/2 veggies, 1/4 protein, 1/4 whole grains.",
        "Prioritize lean proteins (fish, beans, tofu, chicken).",
        "Choose high-fiber carbs (oats, brown rice, quinoa).",
        "Healthy fats in moderation (nuts, olive oil, avocado)."
    ],
    "plans": {
        "weight loss": {
            "breakfast": "Greek yogurt + berries + oats",
            "lunch": "Grilled chicken salad, olive oil & lemon",
            "snack": "Apple + peanut butter",
            "dinner": "Baked salmon, quinoa, steamed broccoli"
        },
        "maintenance": {
            "breakfast": "Oatmeal + banana + chia",
            "lunch": "Turkey sandwich on whole grain + side salad",
            "snack": "Carrots + hummus",
            "dinner": "Stir-fried tofu, mixed veggies, brown rice"
        },
        "muscle gain": {
            "breakfast": "Eggs + whole-grain toast + fruit",
            "lunch": "Chicken, sweet potato, greens",
            "snack": "Cottage cheese + pineapple",
            "dinner": "Beef/tempeh, quinoa, roasted veggies"
        }
    },
    "fallback": "I can help with diet plans and daily do's & don'ts. Try: 'show muscle gain plan' or 'daily health do's'."
}

# Safety keywords for medical redirect
MEDICAL_KEYWORDS = [
    'pain', 'chest pain', 'symptom', 'diagnosis', 'medication', 'emergency',
    'sick', 'fever', 'infection', 'disease', 'doctor', 'prescription',
    'treatment', 'injury', 'blood', 'surgery'
]

# Conversation history (in-memory for demo)
chat_history = []


def check_safety(message):
    """Check if message contains medical keywords requiring redirect"""
    msg_lower = message.lower()
    for keyword in MEDICAL_KEYWORDS:
        if keyword in msg_lower:
            return True
    return False


def get_bot_response(user_message):
    """Generate bot response based on user message"""
    msg_lower = user_message.lower()
    
    # Safety check first
    if check_safety(user_message):
        return "⚠️ I can't help with medical issues, symptoms, or diagnoses. Please consult a healthcare professional or emergency services if needed."
    
    # Check for do's
    if any(word in msg_lower for word in ['do', 'dos', "do's", 'practices', 'daily health']):
        return "**Daily Health Do's:**\n" + "\n".join(f"• {item}" for item in KB['dos'])
    
    # Check for don'ts
    if any(word in msg_lower for word in ['dont', "don't", 'donts', "don'ts", 'avoid']):
        return "**Daily Health Don'ts:**\n" + "\n".join(f"• {item}" for item in KB['donts'])
    
    # Check for diet tips
    if any(word in msg_lower for word in ['diet tip', 'nutrition', 'eating', 'balanced']):
        return "**Diet Tips:**\n" + "\n".join(f"• {item}" for item in KB['diet_tips'])
    
    # Check for meal plans
    for plan_name, plan_details in KB['plans'].items():
        if plan_name in msg_lower or plan_name.replace(' ', '') in msg_lower:
            response = f"**{plan_name.title()} Plan (Sample Day):**\n"
            response += f"🌅 Breakfast: {plan_details['breakfast']}\n"
            response += f"🌞 Lunch: {plan_details['lunch']}\n"
            response += f"🍎 Snack: {plan_details['snack']}\n"
            response += f"🌙 Dinner: {plan_details['dinner']}"
            return response
    
    # Check for hydration
    if 'water' in msg_lower or 'hydrat' in msg_lower:
        return "Stay hydrated! Drink water regularly throughout the day. Start your morning with a glass of water to kickstart your hydration."
    
    # Check for sleep
    if 'sleep' in msg_lower:
        return "Aim for 7–9 hours of quality sleep each night. Avoid screens before bed and maintain a consistent sleep schedule."
    
    # Check for exercise/steps
    if any(word in msg_lower for word in ['exercise', 'steps', 'walk', 'activity', 'move']):
        return "Try to move your body daily! Target 7–10k steps if appropriate for you. Regular physical activity supports overall wellness."
    
    # Fallback
    return KB['fallback']


@app.route('/')
def index():
    """Render the chat page"""
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Get bot response
    bot_response = get_bot_response(user_message)
    
    # Store in history (keep last 10)
    chat_history.append({'user': user_message, 'bot': bot_response})
    if len(chat_history) > 10:
        chat_history.pop(0)
    
    return jsonify({
        'user_message': user_message,
        'bot_response': bot_response
    })


@app.route('/history')
def history():
    """Get chat history"""
    return jsonify({'history': chat_history[-5:]})  # Last 5 messages


if __name__ == '__main__':
    app.run(debug=True)