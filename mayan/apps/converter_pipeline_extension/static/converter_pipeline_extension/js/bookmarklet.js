/**
 * Mayan EDMS Converter Bookmarklet
 * Добавляет кнопку "Сконвертировать" в меню файлов документов
 *
 * Использование: Создайте bookmarklet в браузере с этим кодом:
 * javascript:(function(){var s=document.createElement('script');s.src='http://localhost/static/converter_pipeline_extension/js/vue_integration.js';document.head.appendChild(s);})();
 */

(function() {
    'use strict';

    console.log('🔧 Mayan EDMS Converter Bookmarklet loaded');

    // Загружаем основной интеграционный скрипт
    var script = document.createElement('script');
    script.src = '/static/converter_pipeline_extension/js/vue_integration.js';
    document.head.appendChild(script);

})();
