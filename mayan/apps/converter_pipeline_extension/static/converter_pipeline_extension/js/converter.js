/**
 * Converter Pipeline Extension JavaScript
 * Adds converter buttons to Mayan EDMS interface
 */

(function() {
    'use strict';

    console.log('🔧 Converter Pipeline Extension JavaScript loaded');

    // Wait for page to load and Vue.js to initialize
    window.addEventListener('load', function() {
        console.log('🔧 Page loaded, initializing converter buttons');

        // Use MutationObserver to watch for DOM changes
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    setTimeout(addConverterButtons, 1000);
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // Initial attempt to add buttons
        setTimeout(addConverterButtons, 2000);
    });

    function addConverterButtons() {
        console.log('🔧 Looking for places to add converter buttons');

        // Try to find Vue.js components or specific containers
        var containers = document.querySelectorAll('.v-card__actions, .v-toolbar, .action-buttons, [class*="action"], [class*="Action"]');

        containers.forEach(function(container) {
            var documentFileId = getDocumentFileIdFromUrl();

            if (documentFileId && !container.querySelector('.converter-button')) {
                var button = document.createElement('a');
                button.className = 'v-btn v-btn--outlined theme--light v-size--default converter-button';
                button.href = '/converter-pipeline/media-conversion/' + documentFileId + '/';
                button.innerHTML = '<i class="fas fa-exchange-alt"></i> Сконвертировать';
                button.style.marginLeft = '8px';

                // Add click handler
                button.addEventListener('click', function(e) {
                    console.log('🔧 Converter button clicked for file ID:', documentFileId);
                });

                container.appendChild(button);
                console.log('✅ Converter button added for file ID:', documentFileId);
            }
        });

        // Also try jQuery approach as fallback
        if (typeof $ !== 'undefined') {
            $('.document-file-actions, .object-actions, .card-actions').each(function() {
                var $container = $(this);
                var documentFileId = getDocumentFileIdFromUrl();

                if (documentFileId && !$container.find('.converter-button').length) {
                    var $button = $('<a>')
                        .addClass('btn btn-outline-secondary btn-sm converter-button ml-1')
                        .attr('href', '/converter-pipeline/media-conversion/' + documentFileId + '/')
                        .html('<i class="fas fa-exchange-alt"></i> Конвертировать');

                    $container.append($button);
                    console.log('✅ jQuery: Converter button added for file ID:', documentFileId);
                }
            });
        }
    }

    function getDocumentFileIdFromUrl() {
        // Try to extract document file ID from URL
        var urlMatch = window.location.pathname.match(/\/documents\/(\d+)\/files\/(\d+)\//);
        if (urlMatch) {
            return urlMatch[2]; // File ID
        }

        // Try alternative patterns
        urlMatch = window.location.pathname.match(/files\/(\d+)\//);
        if (urlMatch) {
            return urlMatch[1];
        }

        // Try to find file ID in page data
        var scripts = document.querySelectorAll('script');
        for (var i = 0; i < scripts.length; i++) {
            var scriptContent = scripts[i].textContent || scripts[i].innerText;
            var fileIdMatch = scriptContent.match(/"file_id"\s*:\s*(\d+)/) || scriptContent.match(/"id"\s*:\s*(\d+)/);
            if (fileIdMatch) {
                return fileIdMatch[1];
            }
        }

        return null;
    }

    // Periodic check for new content
    setInterval(addConverterButtons, 5000);

})();
