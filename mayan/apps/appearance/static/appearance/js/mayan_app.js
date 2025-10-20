'use strict';

class MayanApp {
    constructor (options) {
        this.options = options || {
            ajaxMenusOptions: []
        }

        this.afterBaseLoadCallbacks = [];
        this.ajaxExecuting = false;
        this.ajaxMenusOptions = options.ajaxMenusOptions;
        this.ajaxMenuHashes = {};
        this.ajaxSpinnerSeletor = '#ajax-spinner';
        this.window = $(window);
    }

    // Class methods and variables

    static async countChecked() {
        const checkCount = $('.check-all-slave:checked').length;

        if (checkCount) {
            $('#multi-item-title').hide();
            $('#multi-item-actions').show();
        } else {
            $('#multi-item-title').show();
            $('#multi-item-actions').hide();
        }
    }

    static async setupDropdownDirectionChange () {
        $('body').on('shown.bs.dropdown', '.dropdown', function () {
            const $this = $(this);
            const $elementMenu = $this.children('.dropdown-menu');
            const $elementMenuButton = $this.children('.dropdown-toggle');
            const elemenMenuOffset = $elementMenu.offset();
            const sizeDownwards = elemenMenuOffset.top + $elementMenu.height() + 5;
            const sizeUpwards = elemenMenuOffset.top - $elementMenu.height() - $elementMenuButton.height();

            const spaceDownwards = $(window).scrollTop() + $(window).height() - sizeDownwards;
            const spaceUpwards = sizeUpwards - $(window).scrollTop();

            if ((spaceUpwards >= 0 || spaceUpwards > spaceDownwards) && spaceDownwards < 0) {
              $this.addClass('dropup');
            }
        });

        $('body').on('hidden.bs.dropdown', '.dropdown', function() {
            $(this).removeClass('dropup');
        });
    }

    static async setupMultiItemActions () {
        $('body').on('change', '.check-all-slave', function () {
            MayanApp.countChecked();
        });

        $('body').on('click', '.btn-multi-item-action', function (event) {
            let id_list = [];
            $('.check-all-slave:checked').each(function (index, value) {
                //Split the name (ie:"pk_200") and extract only the ID
                id_list.push(value.name.split('_')[1]);
            });
            event.preventDefault();
            partialNavigation.setLocation(
                $(this).attr('href') + '?id_list=' + id_list.join(',')
            );
        });
    }

    static async setupNavBarState () {
        $('body').on('click', '#accordion-sidebar a', function (event) {
            $('#accordion-sidebar li').removeClass('active');
            $(this).parents('li').addClass('active');
        });
    }

    static async updateNavbarState () {
        const uri = new URI(window.location.hash);
        const uriFragment = uri.fragment();
        $('#accordion-sidebar a').each(function (index, value) {
            if (value.pathname === uriFragment) {
                const $this = $(this);

                $this.closest('.collapse').addClass('in').parent().find('.collapsed').removeClass('collapsed').attr('aria-expanded', 'true');
                $this.parents('li').addClass('active');
            }
        });
    }

    // Instance methods

    async addAfterBaseLoadCallback ({func, self, args=null}) {
        this.afterBaseLoadCallbacks.push({func: func, self: self, args: args});
    }

    async afterBaseLoad (callContext) {
        let context = {
            ...callContext,
            self: this
        };

        const self = this;
        for (const callback of self.afterBaseLoadCallbacks) {
            let callingArguments;

            if (callback.args) {
                callingArguments = callback.args;
            } else {
                callingArguments = context;
            }

            callback.func.bind(callback.self)(callingArguments);
        };
    }

    callbackAJAXSpinnerUpdate () {
        if (this.ajaxExecuting) {
            $(this.ajaxSpinnerSeletor).fadeIn(50);
        }
    }

    async doRefreshAJAXMenu (options) {
        $.ajax({
            complete: function() {
                if (options.interval !== null) {
                    setTimeout(app.doRefreshAJAXMenu, options.interval, options);
                }
            },
            success: function(data) {
                const menuHash = options.app.ajaxMenuHashes[data.name];

                if ((menuHash === undefined) || (menuHash !== data.hex_hash)) {
                    $(options.menuSelector).html(data.html);
                    options.app.ajaxMenuHashes[data.name] = data.hex_hash;
                    if (options.callback !== undefined) {
                        options.callback(options);
                    }
                }
            },
            url: options.url,
        });
    }

    async doToastrMessages (context) {
        toastr.options = {
            'closeButton': true,
            'debug': false,
            'newestOnTop': true,
            'positionClass': 'toast-' + this.options.messagePosition,
            'preventDuplicates': false,
            'onclick': null,
            'showDuration': '300',
            'hideDuration': '1000',
            'timeOut': '5000',
            'extendedTimeOut': '1000',
            'showEasing': 'swing',
            'hideEasing': 'linear',
            'showMethod': 'fadeIn',
            'hideMethod': 'fadeOut'
        }

        $.each(context.djangoMessages, function (index, value) {
            let options = {};

            if (value.tags === 'error') {
                // Error messages persist
                options['timeOut'] = 0;
            }
            if (value.tags === 'warning') {
                // Error messages persist
                options['timeOut'] = 10000;
            }

            toastr[value.tags](value.message, '', options);
        });
    }

    async initialize () {
        const self = this;

        this.setupAJAXSpinner();
        MayanApp.setupDropdownDirectionChange();
        this.setupFormHotkeys();
        this.setupFullHeightResizing();
        this.setupItemsSelector();
        MayanApp.setupMultiItemActions();
        this.setupNavbarCollapse();
        MayanApp.setupNavBarState();
        this.setupNewWindowAnchor();
        $.each(this.ajaxMenusOptions, function(index, value) {
            value.app = self;
            app.doRefreshAJAXMenu(value);
        });
        this.setupPanelSelection();
        partialNavigation.initialize();
    }

    setupAJAXSpinner () {
        const self = this;

        $(document).ajaxStart(function() {
            self.ajaxExecuting = true;
            setTimeout(
                function () {
                    self.callbackAJAXSpinnerUpdate();
                }, 450
            );
        });

        $(document).ready(function() {
            $(document).ajaxStop(function() {
                $(self.ajaxSpinnerSeletor).fadeOut();
                self.ajaxExecuting = false;
            });
        });
    }

    async setupFormHotkeys () {
        $('body').on('keypress', '.form-hotkey-enter', function (event) {
            if ((event.which && event.which == 13) || (event.keyCode && event.keyCode == 13)) {
                $(this).find('.btn-hotkey-default').click();
                event.preventDefault();
            }
        });
        $('body').on('dblclick', '.input-hotkey-double-click', function (event) {
            $(this).parents('form').find('.btn-hotkey-default').click();
            event.preventDefault();
        });
    }

    async setupFullHeightResizing () {
        const self = this;

        this.resizeFullHeight();

        this.window.resize(function() {
            self.resizeFullHeight();
        });
    }

    async setupItemsSelector () {
        const app = this;
        app.lastChecked = null;

        $('body').on('click', '.check-all', function (event) {
            const $this = $(this);
            let checked = $(event.target).prop('checked');
            const $checkBoxes = $('.check-all-slave');

            if (checked === undefined) {
                checked = $this.data('checked');
                checked = !checked;
                $this.data('checked', checked);

                if (checked) {
                    $this.find('[data-fa-i2svg]').addClass($this.data('icon-checked')).removeClass($this.data('icon-unchecked'));
                } else {
                    $this.find('[data-fa-i2svg]').addClass($this.data('icon-unchecked')).removeClass($this.data('icon-checked'));
                }
            }

            $checkBoxes.prop('checked', checked);
            $checkBoxes.trigger('change');
        });

        $('body').on('click', '.check-all-slave', function(e) {
            if (!app.lastChecked) {
                app.lastChecked = this;
                return;
            }
            if (e.shiftKey) {
                const $checkBoxes = $('.check-all-slave');

                const start = $checkBoxes.index(this);
                const end = $checkBoxes.index(app.lastChecked);

                $checkBoxes.slice(
                    Math.min(start,end), Math.max(start,end) + 1
                ).prop('checked', app.lastChecked.checked).trigger('change');
            }
            app.lastChecked = this;
        })
    }

    async setupListToolbar () {
        const $listToolbar = $('#list-toolbar');

        if ($listToolbar.length !== 0) {
            const $listToolbarClearfix = $listToolbar.closest('.clearfix');
            const $listToolbarSpacer = $('#list-toolbar-spacer');
            const navBarOuterHeight = $('.navbar-fixed-top').outerHeight();

            $listToolbarSpacer.height($listToolbarClearfix.height()).hide();

            $listToolbar.css(
                {
                    width: $listToolbarClearfix.width(),
                }
            );

            $listToolbar.affix({
                offset: {
                    top: $listToolbar.offset().top - navBarOuterHeight,
                },
            });

            $listToolbar.on('affix.bs.affix', function () {
                $listToolbarSpacer.show();

                $listToolbar.css(
                    {
                        width: $listToolbarClearfix.width(),
                    }
                );
            });


            $listToolbar.on('affix-top.bs.affix', function () {
                $listToolbarSpacer.hide();
            });

            this.window.on('resize', function () {
                $listToolbar.css(
                    {
                        width: $listToolbarClearfix.width(),
                    }
                );
            });
        }
    }

    async setupNavbarCollapse () {
        $(document).keyup(function(e) {
            if (e.keyCode === 27) {
                $('.navbar-collapse').collapse('hide');
            }
        });

        $('body').on('click', 'a', function (event) {
            if (!$(this).hasAnyClass(['dropdown-toggle'])) {
                $('.navbar-collapse').collapse('hide');
            }
        });

        // Small screen main menu toggle to open
        $('body').on('click', '#main-menu-button-open', function (event) {
            $('#menu-main').addClass('menu-main-opened');
            $('#ajax-header').addClass('overlay-gray');
        });

        // Small screen main menu toggle to close
        $('body').on('click', '#menu-main-button-close', function (event) {
            $('#menu-main').removeClass('menu-main-opened');
            $('#ajax-header').removeClass('overlay-gray');
        });
    }

    async setupNewWindowAnchor () {
        $('body').on('click', 'a.new_window', function (event) {
            event.preventDefault();
            const newWindow = window.open($(this).attr('href'), '_blank');
            newWindow.focus();
        });
    }

    async setupPanelSelection () {
        const app = this;

        // Setup panel highlighting on check
        $('body').on('change', '.check-all-slave', function (event) {
            const checked = $(event.target).prop('checked');
            if (checked) {
                $(this).closest('.panel-item').addClass('panel-highlighted');
            } else {
                $(this).closest('.panel-item').removeClass('panel-highlighted');
            }
        });

        $('body').on('click', '.panel-item', function (event) {
            const targetSelection = window.getSelection().toString();
            if (!targetSelection) {
                const $this = $(this);
                const targetSrc = $(event.target).prop('src');
                const targetHref = $(event.target).prop('href');
                const targetIsButton = event.target.tagName === 'BUTTON';
                let lastChecked = null;

                if ((targetSrc === undefined) && (targetHref === undefined) && (targetIsButton === false)) {
                    const $checkbox = $this.find('.check-all-slave');
                    const checked = $checkbox.prop('checked');

                    if (checked) {
                        $checkbox.prop('checked', '');
                        $checkbox.trigger('change');
                    } else {
                        $checkbox.prop('checked', 'checked');
                        $checkbox.trigger('change');
                    }

                    if(!app.lastChecked) {
                        app.lastChecked = $checkbox;
                    }

                    if (event.shiftKey) {
                        const $checkBoxes = $('.check-all-slave');

                        const start = $checkBoxes.index($checkbox);
                        const end = $checkBoxes.index(app.lastChecked);

                        $checkBoxes.slice(
                            Math.min(start, end), Math.max(start, end) + 1
                        ).prop('checked', app.lastChecked.prop('checked')).trigger('change');
                    }
                    app.lastChecked = $checkbox;
                    window.getSelection().removeAllRanges();
                }
            }
        });
    }

    async setupScrollView () {
        $('.scrollable').scrollview();
    }

    async setupSelect2 () {
        $('.select2').select2({
            dropdownAutoWidth: true,
            width: '100%'
        });
    }

    async resizeFullHeight () {
        $('.full-height').height(
            this.window.height() - $('.full-height').data('height-difference')
        );
    }
}
