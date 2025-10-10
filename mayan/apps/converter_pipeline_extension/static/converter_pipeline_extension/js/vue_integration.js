/**
 * Mayan EDMS Vue.js Integration for Converter Pipeline Extension
 * Добавляет кнопку конвертации в Vue.js компоненты Mayan EDMS
 */

(function() {
    'use strict';

    console.log('🔧 Mayan EDMS Vue.js Converter Integration loaded');

    let vueApp = null;
    let observer = null;

    // Ждем загрузки Vue.js приложения
    function waitForVue() {
        // Mayan EDMS Vue.js app обычно монтируется на элемент с id="app" или подобным
        const appElement = document.querySelector('#app, .app, [data-app]');

        if (appElement && window.Vue) {
            console.log('🔧 Vue.js app found, initializing converter integration');
            initializeVueIntegration();
        } else {
            // Если Vue.js еще не загрузился, ждем
            setTimeout(waitForVue, 1000);
        }
    }

    function initializeVueIntegration() {
        // Наблюдаем за изменениями в DOM для динамически загружаемых компонентов
        observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    // Проверяем, появились ли новые компоненты документов
                    checkForDocumentComponents();
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // Первоначальная проверка
        setTimeout(checkForDocumentComponents, 2000);

        // Периодическая проверка каждые 3 секунды
        setInterval(checkForDocumentComponents, 3000);
    }

    function checkForDocumentComponents() {
        console.log('🔧 Checking for document components...');

        // Ищем контекстные меню действий файлов (dropdown меню с действиями)
        const actionMenus = document.querySelectorAll([
            '.dropdown-menu', // Bootstrap dropdown
            '.v-menu__content', // Vuetify menu
            '[role="menu"]', // ARIA menu
            '.context-menu' // Общее контекстное меню
        ].join(', '));

        actionMenus.forEach(function(menu) {
            // Проверяем, содержит ли меню пункты действий файла
            const hasFileActions = Array.from(menu.querySelectorAll('a, button, [role="menuitem"]')).some(function(item) {
                const text = item.textContent || '';
                return text.includes('Скачать') || text.includes('Удалить') || text.includes('Редактировать') ||
                       text.includes('Download') || text.includes('Delete') || text.includes('Edit');
            });

            if (hasFileActions) {
                console.log('🔧 Found file actions menu, adding converter button');
                addConverterButtonToFileActionsMenu(menu);
            }
        });

        // Также ищем компоненты с действиями (старый подход как резервный)
        const actionContainers = document.querySelectorAll([
            '.v-card__actions, .card-actions',
            '.actions, .action-buttons',
            '[class*="action"]'
        ].join(', '));

        actionContainers.forEach(function(container) {
            addConverterButtonToActions(container);
        });
    }

    function addConverterButtonToFileActionsMenu(menu) {
        // Проверяем, есть ли уже кнопка конвертации
        if (menu.querySelector('.converter-btn, .convert-btn')) {
            return;
        }

        // Находим ID файла из URL или из контекста
        const fileId = getFileIdFromCurrentPage();

        if (!fileId) {
            console.log('🔧 Could not determine file ID for converter button');
            return;
        }

        // Создаем элемент меню конвертации
        const converterItem = document.createElement('a');
        converterItem.className = 'dropdown-item converter-btn';
        converterItem.href = '/converter-pipeline/media-conversion/' + fileId + '/';
        converterItem.innerHTML = '<i class="fas fa-exchange-alt"></i> Сконвертировать';

        // Добавляем обработчик клика
        converterItem.addEventListener('click', function(e) {
            console.log('🔧 Converter button clicked for file ID:', fileId);
            // Не предотвращаем переход по умолчанию
        });

        // Находим подходящее место для вставки кнопки
        // Ищем пункт "Скачать" или "Download" как ориентир
        const menuItems = Array.from(menu.querySelectorAll('a, button, [role="menuitem"]'));
        let insertAfter = null;

        for (let i = 0; i < menuItems.length; i++) {
            const item = menuItems[i];
            const text = item.textContent || '';

            // Вставляем после "Скачать/Download" или перед "Удалить/Delete"
            if (text.includes('Скачать') || text.includes('Download')) {
                insertAfter = item;
                break;
            }
        }

        if (insertAfter) {
            // Вставляем после найденного элемента
            insertAfter.parentNode.insertBefore(converterItem, insertAfter.nextSibling);
        } else {
            // Если не нашли ориентир, добавляем в конец меню
            menu.appendChild(converterItem);
        }

        console.log('✅ Converter button added to file actions menu');
    }

    function getFileIdFromCurrentPage() {
        // Сначала пробуем получить из URL
        const urlMatch = window.location.pathname.match(/\/documents\/\d+\/files\/(\d+)\//);
        if (urlMatch) {
            return urlMatch[1];
        }

        // Если не нашли в URL, пробуем найти в DOM (data-атрибуты, формы и т.д.)
        const fileElements = document.querySelectorAll('[data-file-id], [data-pk], input[name*="file"], input[name*="pk"]');
        for (let elem of fileElements) {
            const fileId = elem.getAttribute('data-file-id') ||
                          elem.getAttribute('data-pk') ||
                          elem.value;
            if (fileId && !isNaN(fileId)) {
                return fileId;
            }
        }

        // Пробуем найти в JavaScript переменных или JSON данных на странице
        const scripts = document.querySelectorAll('script');
        for (let script of scripts) {
            const content = script.textContent || script.innerText;
            const match = content.match(/"file_id"\s*:\s*(\d+)/) || content.match(/"id"\s*:\s*(\d+)/);
            if (match) {
                return match[1];
            }
        }

        return null;
    }

    function addConverterButtonToComponent(component) {
        // Проверяем, есть ли уже кнопка конвертации
        if (component.querySelector('.converter-btn, .convert-btn')) {
            return;
        }

        // Пытаемся найти ID документа или файла
        const documentId = getDocumentIdFromElement(component);
        const fileId = getFileIdFromElement(component);

        if (!fileId && !documentId) {
            return;
        }

        // Ищем контейнер для действий в этом компоненте
        const actionContainer = component.querySelector([
            '.v-card__actions',
            '.card-actions',
            '.actions',
            '.action-buttons',
            '.dropdown-menu'
        ].join(', '));

        if (actionContainer) {
            addConverterButtonToActions(actionContainer, fileId || documentId);
        } else {
            // Если нет контейнера действий, добавляем кнопку в конец компонента
            const button = createConverterButton(fileId || documentId);
            if (button) {
                component.appendChild(button);
                console.log('✅ Added converter button to component');
            }
        }
    }

    function addConverterButtonToActions(container, targetId) {
        // Проверяем, есть ли уже кнопка конвертации
        if (container.querySelector('.converter-btn, .convert-btn')) {
            return;
        }

        // Если targetId не передан, пытаемся найти его
        if (!targetId) {
            const component = container.closest('[data-document-id], [data-file-id], .document-card, .file-card');
            if (component) {
                targetId = getDocumentIdFromElement(component) || getFileIdFromElement(component);
            }
        }

        if (!targetId) {
            return;
        }

        const button = createConverterButton(targetId);
        if (button) {
            container.appendChild(button);
            console.log('✅ Added converter button to actions container');
        }
    }

    function createConverterButton(targetId) {
        const button = document.createElement('a');

        // Используем стили Vuetify для консистентности
        button.className = 'v-btn v-btn--text theme--light v-size--small converter-btn';
        button.href = '/converter-pipeline/media-conversion/' + targetId + '/';
        button.innerHTML = `
            <span class="v-btn__content">
                <i class="fas fa-exchange-alt v-icon--left"></i>
                Конвертировать
            </span>
        `;

        // Добавляем стили для лучшего отображения
        button.style.marginLeft = '8px';
        button.style.textDecoration = 'none';

        // Добавляем обработчик клика
        button.addEventListener('click', function(e) {
            console.log('🔧 Converter button clicked for ID:', targetId);
        });

        return button;
    }

    function getDocumentIdFromElement(element) {
        // Пытаемся найти ID документа в атрибутах или data
        return element.getAttribute('data-document-id') ||
               element.getAttribute('data-doc-id') ||
               element.dataset.documentId ||
               element.dataset.docId;
    }

    function getFileIdFromElement(element) {
        // Пытаемся найти ID файла в атрибутах или data
        return element.getAttribute('data-file-id') ||
               element.getAttribute('data-fid') ||
               element.dataset.fileId ||
               element.dataset.fid;
    }

    // Начинаем наблюдение за Vue.js
    waitForVue();

})();
