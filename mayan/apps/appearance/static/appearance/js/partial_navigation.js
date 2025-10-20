'use strict';

$.fn.hasAnyClass = function() {
    /*
     *  Return true is an element has any of the passed classes
     *  The classes are bassed as an array
     */
    const length = arguments[0].length;
    for (let i = 0; i < length; i++) {
        if (this.hasClass(arguments[0][i])) {
            return true;
        }
    }
    return false;
}

class PartialNavigation {
    constructor (parameters) {
        parameters = parameters || {};

        // lastLocation - used as the AJAX referer
        this.lastLocation = null;

        // initialURL - the URL to send users when trying to access the / URL
        this.initialURL = parameters.initialURL || null;

        // disabledAnchorClasses - Anchors with any of these classes will not be
        // processes as AJAX anchors and their events nulled
        this.disabledAnchorClasses = parameters.disabledAnchorClasses || [];

        // excludeAnchorClasses - Anchors with any of these classes will not be
        // processes as AJAX anchors
        this.excludeAnchorClasses = parameters.excludeAnchorClasses || [];

        // formBeforeSerializeCallbacks - Callbacks to execute before submitting an ajaxForm
        this.formBeforeSerializeCallbacks = parameters.formBeforeSerializeCallbacks || [];

        this.redirectionCode = parameters.redirectionCode;

        if (!this.redirectionCode) {
            alert('Need to setup redirectionCode');
        }

        if (!this.initialURL) {
            alert('Need to setup initialURL');
        }

        // AJAX request throttling and pending request cancellation.
        // Default is 10 requests in 5 seconds of less.
        this.maximumAjaxRequests = parameters.maximumAjaxRequests || 10;
        this.ajaxRequestTimeout = parameters.ajaxRequestTimeout || 5000;

        this.currentAjaxRequest = null;
        this.AjaxRequestTimeOutList = [];
    }

    initialize () {
        this.setupAjaxAnchors();
        this.setupAjaxNavigation();
        this.setupAjaxForm();
    }

    filterLocation (newLocation) {
        /*
         * Method to validate new locations
         */
        let uri = new URI(newLocation);
        const currentLocation = new URI(location);

        if (uri.path() === '') {
            // href with no path remain in the same location
            // We strip the same location query and use the new href's one
            uri.path(
                new URI(currentLocation.fragment()).path()
            )
            return uri.toString();
        }

        if (uri.path() === '/') {
            // Root URL is not allowed
            return this.initialURL;
        }

        return newLocation;
    }

    loadAjaxContent (url) {
        /*
         *  Method to load and display partial backend views to the main
         *  view port.
         */
        const app = this;

        url = this.filterLocation(url);

        this.AjaxRequestTimeOutList.push(
            setTimeout(function() {
                app.AjaxRequestTimeOutList.shift();
            }, 5000)
        );

        // Request exceeded maximum, ignoring.
        if (this.AjaxRequestTimeOutList.length >= 10) {
            return;
        }

        // Another Ajax request is being processed. Cancel them previous
        // one.
        if (this.currentAjaxRequest) {
            this.currentAjaxRequest.abort();
            // Clear the content area to avoid an '0' status server error
            // message.
            $('#ajax-content').empty('');
        }

        this.currentAjaxRequest = $.ajax({
            async: true,
            // Need to set mimeType only when run from local file.
            mimeType: 'text/html; charset=utf-8',
            url: url,
            type: 'GET',
            success: function (data, textStatus, response){
                if (response.status == app.redirectionCode) {
                    // Handle redirects.
                    const newLocation = response.getResponseHeader('Location');

                    app.setLocation(newLocation);
                    app.lastLocation = newLocation;
                } else {
                    app.lastLocation = url;
                    if (response.getResponseHeader('Content-Disposition')) {
                        window.location = this.url;
                    } else {
                        $('#ajax-content').html(data).change();
                    }
                }

                // Enable requests again.
                app.currentAjaxRequest = null;

                // Reset throttling.
                for (let item of app.AjaxRequestTimeOutList) {
                    clearTimeout(item);
                }
                app.AjaxRequestTimeOutList = [];
            },
            error: function (jqXHR, textStatus, errorThrown) {
                app.processAjaxRequestError(jqXHR);
            },
            dataType: 'html',
        });
    }

    onAnchorClick ($this, event) {
        /*
         * Anchor click event manager. We intercept all click events and
         * route them to load the content via AJAX instead.
         */
        let url;

        if ($this.hasAnyClass(this.excludeAnchorClasses)) {
            return true;
        }

        if ($this.hasAnyClass(this.disabledAnchorClasses)) {
            event.preventDefault();
            return;
        }

        if ($this.parents().hasAnyClass(this.disabledAnchorClasses)) {
            return false;
        }

        url = $this.attr('href');
        if (url === undefined) {
            return true;
        }

        if (url.indexOf('javascript:;') > -1) {
            // Ignore/exclude links meant to execute javascript on click.
            return true;
        }

        if (url === '#') {
            // Ignore/exclude links with only a hash .
            return true;
        }

        event.preventDefault();

        if (event.ctrlKey) {
            window.open(url);
            return false;
        }

        if (!($this.hasClass('disabled') || $this.parent().hasClass('disabled'))) {
            this.setLocation(url);
        }
    }

    processAjaxRequestError (jqXHR) {
        /*
         * Method to process an AJAX request and make it presentable to the
         * user.
         */
        if (djangoDEBUG) {
            let errorMessage = null;

            if (jqXHR.status != 0) {
                errorMessage = jqXHR.responseText || jqXHR.statusText;
            } else {
                errorMessage = 'Server communication error.';
            }

            $('#ajax-content').html(
                ' \
                    <div class="row">\
                        <div class="col-xs-12">\
                            <div id="banner-server-error">\
                                <div class="alert alert-danger" role="alert"><i class="fa fa-exclamation-triangle"></i> Server error, status code: ' + jqXHR.status + '</div> \
                                    <pre id="django-server-error"><code>' +  errorMessage +'</code> \
                                    </pre> \
                                </div>\
                            </div>\
                    </div>\
                '
            );

            // Call Django's debug view initial JavaScript.
            if (jqXHR.status === 500) {
                  hideAll(document.querySelectorAll('table.vars'));
                  hideAll(document.querySelectorAll('ol.pre-context'));
                  hideAll(document.querySelectorAll('ol.post-context'));
                  hideAll(document.querySelectorAll('div.pastebin'));
            }
        } else {
            if (jqXHR.status == 0) {
                $('#modal-server-error .modal-body').html($('#template-error').html());
                $('#modal-server-error').modal('show')
            } else {
                if ([403, 404, 500].indexOf(jqXHR.status !== -1)) {
                    $('#ajax-content').html(jqXHR.responseText);
                } else {
                    $('#ajax-content').html(jqXHR.statusText);
                }
            }
        }
    }

    setLocation (newLocation, pushState) {
        /*
         * Method to update the browsers history and trigger a page update.
         */

        // Validate the new location first.
        newLocation = this.filterLocation(newLocation);

        if (typeof pushState === 'undefined') {
            // Check if we should just load the content or load the content
            // and update the history.
            pushState = true;
        }

        let currentLocation = new URI(location);
        currentLocation.fragment(newLocation);

        if (pushState) {
            history.pushState({}, '', currentLocation);
        }
        this.loadAjaxContent(newLocation);
    }

    setupAjaxAnchors () {
        /*
         * Setup the new click event handler.
         */
        const app = this;
        $('body').on('click', 'a', function (event) {
            app.onAnchorClick($(this), event);
        });
    }

    setupAjaxForm () {
        /*
         * Method to setup the handling of form in an AJAX way.
         */
        const app = this;
        let lastAjaxFormData = {};

        $('form').ajaxForm({
            async: true,
            beforeSerialize: function($form, options) {
                // Manage any callback registered to preprocess the form.
                $.each(app.formBeforeSerializeCallbacks, function (index, value) {
                   value($form, options);
                });
            },
            beforeSubmit: function(arr, $form, options) {
                const uri = new URI(location);
                const uriFragment = uri.fragment();
                const url = $form.attr('action') || uriFragment;
                const formAction = new URI(url);
                let finalUrl = new URI(formAction.path());
                const formQueryString = new URLSearchParams(
                    decodeURIComponent($form.serialize())
                );

                options.url = url;

                // Merge the URL and the form values in a smart way instead
                // of just blindly adding a '?' between them.
                formQueryString.forEach(function(value, key) {
                    finalUrl.addQuery(key, value);
                });

                lastAjaxFormData.url = finalUrl.toString();

                if ($form.attr('target') == '_blank') {
                    // If the form has a target attribute we emulate it by
                    // opening a new window and passing the form serialized
                    // data as the query.
                    const formAction = new URI($form.attr('action'));
                    let finalUrl = new URL(formAction.path());
                    const formQueryString = new URLSearchParams(
                        decodeURIComponent($form.serialize())
                    );

                    // Merge the URL and the form values in a smart way instead
                    // of just blindly adding a '?' between them.
                    formQueryString.forEach(function(value, key) {
                        finalUrl.addQuery(key, value);
                    });
                    window.open(finalUrl.toString());

                    return false;
                }
            },
            dataType: 'html',
            delegation: true,
            error: function(jqXHR, textStatus, errorThrown){
                app.processAjaxRequestError(jqXHR);
            },
            mimeType: 'text/html; charset=utf-8', // ! Need set mimeType only when run from local file
            success: function(data, textStatus, request) {
                if (request.status == app.redirectionCode) {
                    // Handle redirects after submitting the form
                    const newLocation = request.getResponseHeader('Location');

                    app.setLocation(newLocation);
                } else {
                    let currentUri = new URI(window.location.hash);
                    currentUri.fragment(lastAjaxFormData.url);
                    history.pushState({}, '', currentUri);
                    $('#ajax-content').html(data).change();
                }
            }
        });
    }

    setupAjaxNavigation () {
        /*
         * Setup the navigation method using the hash of the location.
         * Also handles the back button event and loads via AJAX any
         * URL in the location when the app first launches. Registers
         * a callback to send an emulated HTTP_REFERER so that the backends
         * code will still work without change.
         */
        const app = this;

        // Load ajax content when the hash changes
        if (window.history && window.history.pushState) {
            $(window).on('popstate', function() {
                const uri = new URI(location);
                const uriFragment = uri.fragment();
                app.setLocation(uriFragment, false);
            });
        }

        // Load any initial address in the URL of the browser
        if (window.location.hash) {
            const uri = new URI(window.location.hash);
            const uriFragment = uri.fragment();
            this.setLocation(uriFragment);
        } else {
            this.setLocation('/');
        }

        $.ajaxSetup({
            beforeSend: function (jqXHR, settings) {
                // Emulate the HTTP_REFERER.
                jqXHR.setRequestHeader('X-Alt-Referer', app.lastLocation);
            },
        });
    }
}
