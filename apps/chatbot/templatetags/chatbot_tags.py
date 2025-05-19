from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def chatbot_widget():
    return mark_safe('''
        <div id="chatbot-widget" class="chatbot-widget">
            <div class="chatbot-header">
                <h3>PrimeCare Dental Assistant</h3>
                <button class="minimize-btn">_</button>
            </div>
            <div class="chatbot-messages"></div>
            <div class="chatbot-input">
                <input type="text" placeholder="Type your message...">
                <button class="send-btn">Send</button>
            </div>
        </div>
    ''') 