"""
Middleware for Converter Pipeline Extension
"""

import re


class ConverterJavaScriptMiddleware:
    """
    Middleware that injects converter JavaScript into HTML pages
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only inject into HTML responses
        if (hasattr(response, 'get') and
            response.get('Content-Type', '').startswith('text/html')):

            if hasattr(response, 'content'):
                # Inject our JavaScript for Vue.js interface
                javascript_code = '''
<script>
(function() {
    'use strict';

    console.log('🔧 Converter Pipeline Extension: Middleware JavaScript loaded');

    // Function to add converter button to Vue.js interface
    function addConverterButton() {
        console.log('🔍 Looking for Vue.js document file menus...');

        // Wait for Vue.js to load
        setTimeout(function() {
            // Look for file action menus in Vue.js components
            var actionMenus = document.querySelectorAll('[role="menu"], .v-menu__content, .dropdown-menu');
            console.log('📋 Found', actionMenus.length, 'potential menus');

            actionMenus.forEach(function(menu, index) {
                console.log('   Checking menu', index + 1);

                // Check if converter button already exists
                if (menu.querySelector('.converter-btn')) {
                    console.log('   Converter button already exists');
                    return;
                }

                // Look for file actions
                var menuItems = menu.querySelectorAll('[role="menuitem"], a, button, .v-list-item');
                console.log('   Found', menuItems.length, 'menu items');

                var hasFileActions = false;
                for (var i = 0; i < menuItems.length; i++) {
                    var text = menuItems[i].textContent || menuItems[i].innerText || '';
                    console.log('   Menu item', i + 1, 'text:', text);

                    if (text.includes('Download') || text.includes('Delete') ||
                        text.includes('Скачать') || text.includes('Удалить') ||
                        text.includes('Print') || text.includes('Email')) {
                        hasFileActions = true;
                        console.log('   Found file action!');
                        break;
                    }
                }

                if (hasFileActions && !menu.querySelector('.converter-btn')) {
                    console.log('📁 Adding converter button to Vue.js menu');

                    // Create converter button for Vue.js
                    var converterBtn = document.createElement('a');
                    converterBtn.className = 'v-list-item converter-btn';
                    converterBtn.href = '/converter-pipeline/media-conversion/1/';
                    converterBtn.innerHTML = '<i class="fas fa-exchange-alt"></i> Convert';
                    converterBtn.style.color = '#1976d2';
                    converterBtn.style.fontWeight = '500';

                    // Add click handler
                    converterBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        window.open(this.href, '_blank');
                    });

                    // Insert before the last item or append
                    if (menu.lastElementChild) {
                        menu.insertBefore(converterBtn, menu.lastElementChild);
                    } else {
                        menu.appendChild(converterBtn);
                    }

                    console.log('✅ Converter button added to Vue.js interface!');
                }
            });
        }, 2000);
    }

    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addConverterButton);
    } else {
        addConverterButton();
    }

    // Run periodically to handle dynamic content
    setInterval(addConverterButton, 5000);

})();
</script>
                '''

                # Replace closing body tag with JavaScript + closing body tag
                response.content = response.content.replace(
                    b'</body>',
                    javascript_code.encode('utf-8') + b'</body>'
                )

        return response
