"""
Context processors for Converter Pipeline Extension
"""

def converter_javascript(request):
    """
    Context processor that adds converter JavaScript to all templates
    """
    return {
        'converter_javascript': '''
<script>
(function() {
    'use strict';

    console.log('🔧 Converter Pipeline Extension: Context processor JavaScript loaded');
    alert('JavaScript загружен через context processor!');

    // Функция для добавления кнопки конвертации
    function addConverterButton() {
        console.log('🔍 Looking for menus to add converter button...');

        // Ищем dropdown меню
        var menus = document.querySelectorAll('.dropdown-menu');
        console.log('📋 Found', menus.length, 'dropdown menus');

        menus.forEach(function(menu, index) {
            console.log('   Processing menu', index + 1);

            // Проверяем, есть ли уже кнопка конвертации
            if (menu.querySelector('.converter-btn')) {
                console.log('   Converter button already exists');
                return;
            }

            // Ищем ссылки в меню
            var links = menu.querySelectorAll('a');
            console.log('   Found', links.length, 'links in menu');

            var hasFileActions = false;
            for (var i = 0; i < links.length; i++) {
                var text = links[i].textContent || '';
                console.log('   Link', i + 1, 'text:', text);

                if (text.includes('Скачать') || text.includes('Удалить') ||
                    text.includes('Download') || text.includes('Delete')) {
                    hasFileActions = true;
                    console.log('   Found file action link!');
                    break;
                }
            }

            if (hasFileActions) {
                console.log('📁 Adding converter button to menu');

                // Создаем кнопку конвертации
                var converterBtn = document.createElement('a');
                converterBtn.className = 'dropdown-item converter-btn';
                converterBtn.href = '/converter-pipeline/media-conversion/1/';
                converterBtn.innerHTML = '<i class="fas fa-exchange-alt"></i> Сконвертировать';
                converterBtn.style.color = '#007bff';
                converterBtn.style.fontWeight = 'bold';

                // Добавляем кнопку в меню
                menu.appendChild(converterBtn);
                console.log('✅ Converter button added!');
            }
        });
    }

    // Запускаем через некоторое время
    setTimeout(function() {
        console.log('🚀 Running addConverterButton...');
        addConverterButton();
    }, 1000);

    // Повторяем каждые 3 секунды
    setInterval(addConverterButton, 3000);

})();
</script>
        '''
    }