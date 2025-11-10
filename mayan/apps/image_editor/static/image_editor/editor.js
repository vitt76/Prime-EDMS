'use strict';

(function() {
    const canvas = document.getElementById('image-editor-canvas');
    const context = canvas.getContext('2d');
    const sourceImage = document.getElementById('image-editor-source');
    const saveButton = document.getElementById('image-editor-save');
    const commentField = document.getElementById('image-editor-comment');
    const brightnessControl = document.getElementById('image-editor-brightness');
    const contrastControl = document.getElementById('image-editor-contrast');

    let currentTool = null;

    function initializeCanvas() {
        if (!sourceImage.src) {
            return;
        }

        sourceImage.onload = function() {
            canvas.width = sourceImage.naturalWidth;
            canvas.height = sourceImage.naturalHeight;
            context.drawImage(sourceImage, 0, 0);
        };

        if (sourceImage.complete) {
            sourceImage.onload();
        }
    }

    function handleToolClick(event) {
        const button = event.currentTarget;
        currentTool = button.getAttribute('data-tool');

        switch (currentTool) {
            case 'rotate-left':
                console.debug('Rotate left');
                break;
            case 'rotate-right':
                console.debug('Rotate right');
                break;
            case 'flip-horizontal':
                console.debug('Flip horizontal');
                break;
            case 'flip-vertical':
                console.debug('Flip vertical');
                break;
            case 'crop':
                console.debug('Crop tool selected');
                break;
        }
    }

    function applyAdjustments() {
        console.debug('Adjustments - brightness:', brightnessControl.value, 'contrast:', contrastControl.value);
    }

    function getCSRFToken() {
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfToken) {
            return csrfToken.value;
        }
        return window.imageEditorConfig && window.imageEditorConfig.csrfToken;
    }

    function handleSave() {
        canvas.toBlob(function(blob) {
            if (!blob) {
                alert('Не удалось получить данные изображения');
                return;
            }

            const formData = new FormData();
            formData.append('image_content', blob, 'edited-image.png');
            formData.append('comment', commentField.value);

            fetch(saveButton.dataset.saveUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                },
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Новая версия успешно сохранена.');
                        window.location.href = `/documents/documents/files/${data.document_file_id}/preview/`;
                    } else {
                        alert('Ошибка при сохранении: ' + JSON.stringify(data.errors));
                    }
                })
                .catch(error => {
                    console.error('Save error:', error);
                    alert('Ошибка при сохранении файла.');
                });
        }, 'image/png');
    }

    function bindEvents() {
        document.querySelectorAll('[data-tool]').forEach(function(button) {
            button.addEventListener('click', handleToolClick);
        });

        brightnessControl.addEventListener('input', applyAdjustments);
        contrastControl.addEventListener('input', applyAdjustments);
        saveButton.addEventListener('click', handleSave);
    }

    initializeCanvas();
    bindEvents();
})();
