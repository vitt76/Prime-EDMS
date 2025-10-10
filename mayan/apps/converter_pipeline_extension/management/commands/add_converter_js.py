from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = 'Add converter JavaScript to Mayan EDMS static files'

    def handle(self, *args, **options):
        # Path to Mayan EDMS static files
        mayan_static_path = '/opt/mayan-edms/lib/python3.9/site-packages/mayan'

        # Find appearance app static directory
        appearance_static = None
        for root, dirs, files in os.walk(mayan_static_path):
            if 'appearance' in root and 'js' in dirs:
                appearance_static = os.path.join(root, 'js')
                break

        if not appearance_static:
            self.stdout.write(self.style.ERROR('Could not find Mayan EDMS appearance static directory'))
            return

        # Create converter JavaScript file
        js_content = '''
(function() {
    'use strict';

    console.log('🔧 Converter Pipeline Extension JavaScript loaded');

    // Ждем 1-2 секунды после загрузки страницы, как было в рабочем решении
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
            addConverterMenu();
        }, 1500);
    });

    function addConverterMenu() {
        console.log('🔧 Looking for menu containers to add converter button...');

        // Ищем контейнеры меню в Mayan EDMS
        var menuContainers = document.querySelectorAll('.dropdown-menu, .menu, [class*="menu"], [class*="action"]');

        menuContainers.forEach(function(container) {
            // Ищем элементы меню для файлов документов
            var menuItems = container.querySelectorAll('a, button, [role="menuitem"]');

            menuItems.forEach(function(item) {
                // Проверяем, есть ли уже кнопка конвертации
                if (item.textContent && item.textContent.includes('Конвертировать')) {
                    return; // Уже есть
                }

                // Ищем элементы, связанные с файлами документов
                if (item.href && item.href.includes('/documents/') && item.href.includes('/files/')) {
                    // Нашли элемент меню для файла документа
                    var converterLink = document.createElement('a');
                    converterLink.href = item.href.replace(/\/documents\/(\\d+)\/files\/(\\d+)\//, '/converter-pipeline/media-conversion/$2/');
                    converterLink.className = 'dropdown-item';
                    converterLink.innerHTML = '<i class="fas fa-exchange-alt"></i> Сконвертировать';

                    // Вставляем после текущего элемента
                    item.parentNode.insertBefore(converterLink, item.nextSibling);
                    console.log('✅ Converter menu item added');
                    return;
                }
            });
        });

        // Альтернативный подход - ищем по URL паттернам для текущей страницы
        setTimeout(function() {
            var currentUrl = window.location.pathname;
            var fileMatch = currentUrl.match(/\/documents\/\\d+\/files\/(\\d+)\//);

            if (fileMatch) {
                var fileId = fileMatch[1];

                // Ищем все выпадающие меню на странице
                var dropdowns = document.querySelectorAll('.dropdown-menu');

                dropdowns.forEach(function(dropdown) {
                    if (!dropdown.querySelector('.converter-menu-item')) {
                        var converterItem = document.createElement('a');
                        converterItem.className = 'dropdown-item converter-menu-item';
                        converterItem.href = '/converter-pipeline/media-conversion/' + fileId + '/';
                        converterItem.innerHTML = '<i class="fas fa-exchange-alt"></i> Сконвертировать';

                        dropdown.appendChild(converterItem);
                        console.log('✅ Converter button added to dropdown menu');
                    }
                });
            }
        }, 500);
    }
})();
        '''

        js_file_path = os.path.join(appearance_static, 'converter_extension.js')

        try:
            with open(js_file_path, 'w') as f:
                f.write(js_content)
            self.stdout.write(self.style.SUCCESS(f'Successfully created JavaScript file: {js_file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to create JavaScript file: {e}'))
            return

        # Now add the script tag to the base template
        base_template_path = '/opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/appearance/templates/appearance/base.html'

        try:
            with open(base_template_path, 'r') as f:
                content = f.read()

            # Add script tag before closing body
            script_tag = '<script src="{% static "appearance/js/converter_extension.js" %}"></script>'
            if script_tag not in content:
                content = content.replace('</body>', f'{script_tag}\n</body>')

                with open(base_template_path, 'w') as f:
                    f.write(content)

                self.stdout.write(self.style.SUCCESS('Successfully added converter JavaScript to base template'))
            else:
                self.stdout.write(self.style.WARNING('Converter JavaScript already in base template'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to modify base template: {e}'))

