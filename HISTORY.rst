4.3.1 (2022-08-21)
==================
- Fixes and improvements merged from version 4.2.9 and 4.2.10.

4.3 (2022-07-27)
================
- Partials navigation updates:

  - Streamline JavaScript partials navigation code.
  - Make the AJAX response redirect code configurable. New setting
    ``APPEARANCE_AJAX_REDIRECTION_CODE`` added.
  - Remove repeated AJAX redirection middleware.

- Add white outline to favicon.
- Add support for optional ``get_mayan_object_permissions`` and
  ``get_mayan_view_permissions`` methods to allow API views to customize
  how required permissions are calculated.
- Added support for form fieldsets.
- Added fieldsets to the following forms:

    - document file properties
    - document type deletion policies
    - metadata type
    - user

- Remove usage of flat ``values_list`` queryset in metadata managers module.
- Prefix all test objects with an underscore to avoid clashes with test
  methods.
- ``PartialNavigation.js`` improvements.

  - Clean URL query on form submit and use form data as the URL query.
  - Remove dead code.
  - Use constants where appropriate.

- Search updates:

  - Add filtering support to list views. All list view that show instances of
    models with a corresponding defined search model, will show a text box
    for filtering the list. The syntax is the same as the standard simple
    search.
  - Empty list views now show the toolbar for cases where the list is empty
    due to a filtering term.
  - Define the ``q`` URL query key as an internal literal named
    ``QUERY_PARAMETER_ANY_FIELD``.

- Support AJAX request cancellation. This avoid the user interface from
  appearing to unresponsive when the backend is overloaded.
- Support AJAX request throttling. Prevents users from requesting too many
  consecutive page loads. Defaults to a maximum of 10 requests in 5 seconds
  of less. This applies only to the user interface. The AJAX throttling
  resets the moment the last pending AJAX request is completed.
- ``BaseBackend`` class improvements.

  - Selectable identifier via the ``_backend_identifier`` property. Defaults
    to ``backend_class_path`` for compatibility.
  - Update ``.get_all`` to return a list and not a dictionary.
  - Add property ``backend_id`` that returns the value of the class
    ``_backend_identifier`` property.

- Convert document file actions from hardcoded logic to an extensible class
  using the ``BaseBackend`` class. Available classes will be loaded from the
  ``document_file_actions`` module. The id of the class defaults to the
  existing literal values for compatibility.
- Add API endpoint called ``document_file_actions`` to list the available
  actions and their properties. API endpoint URL: /api/v4/document_file_actions/
- Add document version modification backend. Convert the document version
  page reset and append functions into document version modication backends.
  Update document version views and API endpoints to use document version
  modification backends.
  Adds new API endpoints:

    - /api/v4/documents/{ ID }/versions/{ ID }/modify/
    - /api/v4/document_version_modification_backends/

- Add workflow action to send user messages.
- Update ``WorkflowAction`` to use ``common.classes.BaseBackend``.
- Pagination refactor:

  - Remove ``django-pure-pagination`` package.
  - Use Django's 3.2 new ``get_proper_elided_page_range`` for paging.
  - Remove duplicate URL query string manipulation.
  - Remove duplicated pagination template.
  - Make pagination argument configurable. Added the setting
    ``VIEWS_PAGING_ARGUMENT``. Defaults to ``page`` for compatibility.

- Update the default pagination size from 40 items to 30.
- Support hyphenated text when using the ElasticSearch backend.
- Add support for supplying files to source backend via the API. Add the
  ``accept_files`` property to ``SourceBackendAction`` which dynamically add
  a ``file`` serializer field for the corresponding action.
- Add an ``upload`` action to the web form source. This allows using web form
  sources to upload documents from the API.
- Support REST API list filtering. Filtering is done using similar logic
  to that of the user interface list filtering. However, the API list
  filtering also support filtering by any field and not just using the
  special "any field" ``q`` query key.
- Merge fixes from version 4.2.2.
- Move the ``purgeperiodictasks`` command from the common app to the
  task_manager app.
- Drop support for Python 3.6.
- Dependencies update:

  - ElasticSearch from 7.16.0 to 7.17.0.
  - Debian from 11.2-slim to 11.3-slim.
  - PostgreSQL from 12.9-alpine to 12.10-alpine.
  - RabbitMQ from 3.9-alpine to 3.10-alpine.
  - amqp from 5.0.9 to 5.1.0.
  - pip from 21.3.1 to 22.2.
  - psycopg2 from 2.9.2 to 2.9.3.
  - redis from 4.0.2 to 4.2.0.
  - FontAwesome from 5.6.3 to 5.15.4.
  - urijs from 1.19.7 to 1.19.10.
  - bleach from 4.0.0 to 4.1.0.
  - django-solo from 1.1.5 to 2.0.0.
  - jstree from 3.3.11 to 3.3.12.
  - PyYAML from 5.4.1 to 6.0.
  - django-model-utils from 4.1.1 to 4.2.0.
  - django-mptt from 0.12.0 to 0.13.4.
  - pycountry from 20.7.3 to 22.3.5.
  - requests from 2.26.0 to 2.27.0.
  - devpi-server from 6.2.0 to 6.5.0.
  - django-debug-toolbar from 3.2.2 to 3.2.4.
  - django-extensions from 3.1.3 to 3.1.5.
  - django-rosetta from 0.9.7 to 0.9.8.
  - django-silk from 4.1.0 to 4.3.0.
  - flake8 from 3.9.2 to 4.0.1.
  - ipython from 7.26.0 to 7.32.0.
  - transifex-client from 0.14.3 to 0.14.4.
  - twine from 3.4.2 to 3.8.0.
  - wheel from 0.37.0 to 0.37.1.
  - Pillow from 8.3.1 to 9.2.0.
  - node-semver from 0.8.0 to 0.8.1.
  - packaging from 21.0 to 21.3.
  - python_gnupg from 0.4.7 to 0.4.8.
  - elasticsearch from 7.16.0 to 7.17.1.
  - django-activity-stream from 0.10.0 to 1.4.0.
  - chart.js from 2.7.3 to 2.8.0.
  - python-magic from 0.4.24 to 0.4.26.
  - gevent from 21.8.0 to 21.12.0.
  - sentry-sdk from 1.4.1 to 1.5.8.
  - whitenoise from 5.3.0 to 6.0.0.
  - cropperjs from 1.5.2 to 1.5.12.
  - django-cors-headers from 3.8.0 to 3.10.0.
  - djangorestframework from 3.12.4 to 3.13.1.
  - jsonschema from 3.2.0 to 4.4.0.
  - swagger-spec-validator from 2.7.3 to 2.7.4.
  - dropzone from 5.9.2 to 5.9.3.
  - pycryptodome from 3.10.1 to 3.10.4.
  - celery from 5.1.2 to 5.2.3.
  - django-formtools from 2.2 to 2.3.
  - django-widget-tweaks from 1.4.9 to 1.4.12.
  - furl from 2.1.2 to 2.1.3.
  - Sphinx from 3.5.4 to 4.5.0.

- Silence warning about unordered object pagination for:

  - Announcements
  - Document index instance nodes
  - Workflow transition triggers
  - File caches
  - Quotas

- Convert API search model names to lowercase to revert backward incompatible
  change in version 4.2. Search model names via the API can now be specified
  in either lowercase (version 4.2) or hybrid case (version <4.2).
- ``mkdtemp`` now accepts a ``dir`` argument like the upstream version.
  However the ``dir`` value is appended to the system wide value of
  ``STORAGE_TEMPORARY_DIRECTORY``.
- Staging folder updates:

  - Support inclusion regular expression.
  - Support exclusion regular expression.
  - Support subfolders.
  - Update scan code to use ``pathlib.Path``.
  - Support pagination.

- Add support for workflow escalation. This feature allows moving a workflow
  forward after the workflow has remained in a certain state after a
  pre-determined amount of time. Multiple escalations are supported for
  each state. Conditions using the templating language are supported.
- Move model based classes to the databases app. Move the classes:

  - ``ModelQueryFields``
  - ``ModelAttribute``
  - ``ModelProperty``
  - ``ModelField``
  - ``ModelFieldRelated``
  - ``ModelReverseField``
  - ``QuerysetParametersSerializer``

- Convert the OCR app to the new error log system. The permission
  "View error log" is now required to view the document version OCR error
  log.
- Convert the document parsing app to the new error log system. The
  permission "View error log" is now required to view the document file
  parsing error log.
- Remove the Python package ``mock``. This package is now available as
  unittest.mock in Python 3.3 onward.
- Unify and remove repeated workflow API views code using parent resolution
  mixins.
- Support adding help text to search model fields. By default the help text
  from the model fields will be used.
- Increase the document type label size from 96 characters to 196.
- Update the document type label field help text.
- Search updates:

  - Rename search model instances from "...search" to "search_model...".
  - Add support for removing search fields from third party apps. The method
    is called ``.remove_search_field(search_field=)`` and requires the
    search field instance obtained from the method ``.get_search_fields()``.
  - Remove the ``search_fields`` list and use the ``search_fields_dict``
    instead for both purposes. The canonical method to obtain the search
    field of a search model is now using the method ``.get_search_fields()``.

- Update the ElasticSearch backend default settings to match those of the
  official Python client.
- Don't introspect document file MIME type at download. Instead pass the
  stored values.
- Support empty ranges for ``parse_range``.
- Add ``group_iterator`` to group iterators in to lists of tuples.
- Refactor bulk object search indexing:

  - Rename ``mayan.apps.dynamic_search.tasks.task_index_search_model`` to
    ``mayan.apps.dynamic_search.tasks.task_index_instances``.
  - Index only objects that exists instead of using blind ranges.
  - Update ``search_index_objects`` management command to trigger multiple
    ``task_index_instances`` tasks instead of just one.

- Add date manipulation template tags. The new tags are ``date_parse`` to
  convert a string into a datetime object and ``timedelta`` to apply time
  transformations to a datetime object.
- Add a ``size`` field to the document file model. Since this value is not
  expected to change, it is now a persistent model field and not calculated
  on demand by querying the storage layer. This change also improves document
  mirroring performance by removing one disk access per document and using
  the database stored size value which is immutable.
- Support searching messages. Make the ``subject``, ``body``, ``date_time``
  fields searchable.
- Error logging updates:

  - Add error log entry delete permission.
  - Add support deleting individual error log entries or the complete error
    log of an object.
  - Add the error log entry delete event.
  - Support subscribing to the error log entry delete event of an object.
  - Add API views. Support added to view the error log of objects.

- Migrations code style cleanup.

  - Rename code migrations functions prefix from ``operation_`` to ``code_``.
  - Add keyword arguments.
  - PEP8 code style cleanups.

- Add support for cabinet mirroring.
- Remove ``django-colorful``. Use HTML5 color field instead.
- Add support to randomize the tag color.
- Document parsing updates. Closes GitLab issue #957. Thanks to
  LeVon Smoker (@lsmoker) for the report and initial suggestions.

  - Pass the original document file to parsers instead of attempting to
    pre-processing the document file to PDF.
  - Add parsing support for office document files and text files.

- Rename test file literals for uniformity.
- Rename management commands to include the app name where they are defined.
  Add a stub command for backwards compatibility.

  - ``checkdependencies`` replaced by ``dependencies_check``.
  - ``checkversion`` replaced by ``dependencies_check_version``.
  - ``createautoadmin`` replaced by ``autoadmin_create``.
  - ``generaterequirements`` replaced by ``dependencies_generate_requirements``.
  - ``initialsetup`` replaced by ``common_initial_setup``.
  - ``installdependencies`` replaced by ``dependencies_install``.
  - ``mountindex`` replaced by ``mirroring_mount_index``.
  - ``performupgrade`` replaced by ``common_perform_upgrade``.
  - ``platformtemplate`` replaced by ``platform_template``.
  - ``preparestatic`` replaced by ``appearance_prepare_static``.
  - ``purgelocks`` replaced by ``lock_manager_purge_locks``.
  - ``purgepermissions`` replaced by ``permissions_purge``.
  - ``purgeperiodictasks`` replaced by ``task_manager_purge_periodic_tasks``.
  - ``purgestatistics`` replaced by ``statistics_purge``.
  - ``revertsettings`` replaced by ``settings_revert``.
  - ``savesettings`` replaced by ``settings_save``.
  - ``showsettings`` replaced by ``settings_show``.
  - ``showversion`` replaced by ``dependencies_show_version``.

- Split the document indexing models module. Module is split into index
  template and instance models.
- Show item count even if the list is empty. This change prevents the list
  toolbar from "jumping" visually when there are no results.
- Simplify how the view title is copied to the window title. Escaping is now
  performed by jQuery.
- Add icons to all views. Every view now has a corresponding icon to be
  displayed with the title.
- Normalize icon, link and view names. Follow the pattern
  object_sub_object_action.
- Add warning message when user attempting to delete their own accounts.
- Add support for Whoosh bulk indexing using the ``BufferedWriter`` class.
  When reindexing the search indexes, for every lock obtained, a group of
  object will be written as a single operation. The number of objects
  written concurrently is controlled by the settings
  ``SEARCH_INDEXING_CHUNK_SIZE``.
- Split converter app views into separate modules.
- Add support for transformation argument forms.
- Improve transformation argument column display.
- Fix argument handling for the transformation
  ``TransformationDrawRectangle``.
- Check and reject negative percent values for the zoom transformation.
- Fix asset transformations hash calculation.
- Use a lower layer that the redaction layer to allow seeing the entire
  document when editing redactions. This is more natural as it gives the
  impression the redaction is actually being edited by being moved instead
  of showing two redactions (old in the image plus the interactive one).
- Add transparency support to the ``TransformationDrawRectanglePercent``
  transformation.
- Unify the ``TransformationDrawRectangle`` and
  ``TransformationDrawRectanglePercent`` transformations.
- Move transformation mixins to their own module.
- Allow classes using ``APIImageViewMixin`` to specify the stream MIME type
  via ``get_stream_mime_type``.
- Fix repeated model manager definition in the ``DocumentFilePage`` model.
- Support easier test document stub creation via the new
  ``auto_create_test_document_stub``. It is mutually exclusive with
  ``auto_create_test_document_stub`` and requires settings
  ``auto_upload_test_document`` to False.
- Add first name and last name fields to the test case user.
- Generalize image transformations into reusable mixins:
  ``ImagePasteCoordinatesAbsoluteTransformationMixin``,
  ``ImagePasteCoordinatesPercentTransformationMixin``,
  ``ImageWatermarkPercentTransformationMixin``.
- Add support for signature capture. The signature capture app allows
  capture of handwritten signatures. The original point data as well as
  an SVG version of the signature is store. The point data represents the
  raw signature primitives that allows reloading them into the signature
  pad library. The SVG version allows for rendering as an image for preview.
  A transformation is added to allow pasting a signature as a page image.
- Remove trailing new lines from the MIME type and encoding returned by the
  ``MIMETypeBackendFileCommand``.
- Make ``MIMETypeBackendFileCommand`` the default MIME backend.
- Fix sorting and grouping of permissions in the workflow action to grant
  or revoke document access.
- Remove ``SearchModel`` unused class method and improve result sorting.
- Navigation updates:

  - Add support for extra HTML attributes.
  - Improve HTML data by allowing the entries to be resolved against the
    context.
  - Support empty URL values. When empty, the link is rendered without a
    href attribute.

- Add link to make staging folder file selection easier. Closes GitLab
  issue #341. Thanks to Leroy Förster (@gersilex) for the report and
  initial idea.
- Modernize Python syntax:

  - Pass generators instead of lists to ``sorted``.
  - Update string formatting to use ``.format``.
  - Remove creating of sets using the set factory and use instead the set
    literal.

- New workflow events: ``workflow instance created`` committed when a new
  workflow is launched for a document and
  ``workflow instance transitioned`` committed when a workflow instance is
  transitioned to a new state, either manually or automatically.
- Track the user when a new workflow instance is created or transitioned.
- Optimize the document indexing by reusing the index instance node if it
  already exists.
- Add support for document index event triggers. Historically document
  indexes used hard coded signals to trigger an index update. The indexing
  app was updated to now use events to trigger these updates. This has the
  additional benefits of allowing runtime configuration of the index event
  triggers, disabling the ones not relevant for an index to improve
  performance. New document indexes default to update on all available
  document events. Existing indexes will me automatically migrated and
  updated to update on all available document events. Index updates now
  support more events like adding or removal from cabinets.
  Closes GitLab issue #631. Thanks to Tobias Huhn (@twhuhn) for the request.
- Convert the staging folder file selection input to a Select2 widget
  supporting text filtering.
- Move the transformations ``TransformationDrawRectangle`` and
  ``TransformationDrawRectanglePercent`` to the decorations layer.
- Add retry backoff maximum delay to the search tasks.
- Add per user object event subscription view.
- Add support for permission filtering to the notification views. This moves
  the access filtering of notification from the class to the view. The
  advantage of this change is that notifications are restricted when the
  access control is modified, even if the notification already exists.
- Normalize how the search "Match all" parameter is evaluated.
- Fix evaluation of "Match all" when using a single level scoped search.
- Discard non supported images contained in MPO images files.
- Use the ElasticSearch count API (https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-count.html)
  to obtain accurate search model status information.
- Delete existing indexes when calling the ElasticSearch backend initialize
  method.
- Wrap search backend errors into a general exception with a short
  explanation.
- Documentation updates:

  - Set the Docker Compose installation method as the main method.
  - Add warning notes for the deprecated installation methods.
  - Expand the requirements section.
  - Move the requirements to their on chapter.
  - Update the features part.

- Add management command ``common_generate_random_secret_key`` to provide
  random values suitable for use as ``SECRET_KEY``.
- Refactor initial setup and upgrade commands:

  - Consolidate management command code.
  - Move command code to a separate class.
  - Convert code to use pathlib.

- Add support for disabling use of the media folder. Add the bootstrap
  setting ``COMMON_DISABLE_LOCAL_STORAGE`` to disable use of the local
  ``media`` folder. When using this setting, all apps must be also configured
  via their respective storage backend settings to use alternate persistence
  methods.
- When serving images using ``APIImageViewMixin``, detect the MIME type of
  the data before sending the stream. This ensures the image will load
  correctly in all browsers that require a MIME type value in the header of
  the stream.
- Change the ``UUID`` field to ElasticSearch field mapping, from ``Keyword``
  to ``Text`` to avoid search indexing error when processing document
  containers with more than 910 documents. ElasticSearch's ``Keyword`` field
  is limited to 32766 bytes and attempting to index a container with more
  than 910 documents would exceed this limit.
- Update the ElasticSearch backend search query configuration to be more
  strict and lower the number of hits matched. Change the ``match`` query to
  ``match_phrase`` and remove the ``fuzzy`` query.
- Ensure document version pages point to an existing content object when
  exporting. Otherwise they are skipped.
- Improve document version export code to skip invalid pages. The page loop
  will skip pages with no content object and regard the first page found
  with a content object as the first exported page.
- Don't assume all storages have a preset mode attribute. Such is the case
  with the ``S3Boto3Storage`` when used for shared uploaded files. Instead
  introspect the mode and fallback to a safe default valur of ``'rb'``.
- Disable the settings edit link when local storage is disabled.
- Display a warning message in the setting edit view when local storage is
  disabled.

4.2.10 (2022-08-20)
===================
- Make file improvements. Don't require a local ``psql`` client to
  launch the PostgreSQL development container. Don't require a local
  Redis client to launch the Redis development container. Fix the
  staging targets.
- Display exception errors to console when Celery fails to initialize.
- Use the ``DownloadFile`` filename attribute if available when performing
  the actual download action. Fall back to the previous logic of the
  string representation of the download file if the filename attribute
  is not set.
- Ensure cabinet document is added using the correct method when using the
  upload wizard. Closes GitLab issue #1118. Thanks to
  haithoum (@haithembenammar) for the report.
- Improve cabinet, metadata, and tag app tests.
- Ensure document tag is attached using the correct method when using the
  upload wizard. Same issue to GitLab issue #1118. Thanks to
  haithoum (@haithembenammar) for the initial report.

4.2.9 (2022-08-04)
==================
- Add permission filtering to the source switch links. The permission
  filtering will be the same as the views: document create permission for the
  source links during document uploads and document file new permissions
  for the source links in the new document file upload view.
- Don't cache the impersonation and the settings app templates. This ensures
  the impersonation banner and settings change banner are triggered
  correctly in all edge cases where multiple frontend processes or load
  balancers are used.
- Add make file development targets ``setup-dev-operating-system-packages``
  and ``setup-dev-python-libraries``.

4.2.8 (2022-07-22)
==================
- Fix the permission requirement of the recently created documents dashboard
  widget. The widget should filter by document view and not document type
  view permission. Thanks to forum user LeVon Smoker (@lsmoker) for
  the report.
- Update Django from version 3.2.13 to 3.2.14.
  https://docs.djangoproject.com/en/4.0/releases/3.2.14/
- Update Pillow from version 8.3.1 to 8.3.2.
- Update cryptodome from version 3.10.1 to 3.10.4.
- Remove the package ``firefox-geckdriver`` from the make file target
  ``setup-dev-environment`` as it is no longer available in recent OS LTS
  releases.
- Update the GitLab CI file to support releasing testing build of the
  Python library and the Docker image separately.
- Update Docker Debian base image from debian:11.3-slim to to
  debian:11.4-slim. https://www.debian.org/News/2022/20220709
- Update PyPDF2 from version 1.26.0 to 1.28.4. Closes GitLab issue #1106.
  Thanks to Stefan Denker (@denkerszaf) for the report and investigation.
- Update Sphinx from version 3.5.4 to 4.5.0 to avoid bug #9038.

4.2.7 (2022-07-01)
==================
- Intercept document file and document version page transformation errors
  and show a corresponding error template. This allows accessing the page
  to fix the transformation error. Closes GitLab issue #1101. Thanks to
  Munzir Taha (@munzirtaha) for the report.
- Backport search fixes from 4.3:

  - Normalize how the search "Match all" parameter is evaluated.
  - Fix evaluation of "Match all" when using a single level scoped search.
  - Improve extraction of URL search query parameters.

4.2.6 (2022-06-25)
==================
- Backport document content parsing template method. This fix
  allows accessing the parsed content of a document directly
  in a template.
- Backport permission form widget choice grouping and sorting improvements.

4.2.5 (2022-05-21)
==================
- Remove unused authentication view.
- Task manager app updates:

  - Add backend Celery queue deduplication to the ``CeleryQueue``.
  - Enable app tests.
  - Add and improve tests.
  - Add support for runtime removal of queues.

- Remove unused event link.
- Make document version OCR submit view messages translatable.
- Make file caching purge view messages translatable.
- Make document file metadata submit view messages translatable.
- Fix asset transformations hash calculation.
- Fix asset image API view docstring.
- Fix repeated model manager definition in ``DocumentFilePage``
  models.
- Transformation improvements:

  - Fix wrong parameter in the ``ImageDraw.Draw`` usage of the
    ``TransformationDrawRectangle`` transformation.
  - Add sanity check to reject negative zoom values for the
    ``TransformationZoom`` transformation.

- Add warning message when users attempting to delete their own accounts.
- Convert the signal handler that triggers search indexing on many to many
  fields changes into a background task. Solves user interface blocking
  when changing the document type to index template association on large
  installations.
- Update Django from version 3.2.12 to 3.2.13.
- Retry search indexing task when the object is not found. There are
  situations where the broker will route the message to the workers faster
  than the database can commit the data.
- Fix favorite document links reacting to favorite documents beyond the
  active user. Closes GitLab issue #1104. Thanks to
  Biel Frontera (@bielfrontera) for the report and initial implementation.

4.2.4 (2022-04-29)
==================
- Fix the documentation paths to the OTP backends. Closes GitLab
  issue #1099. Thanks to Matthias Löblich (@startmat) for the
  report.
- Fix Docker pull counter.
- Remove repeated Whoosh backend line of code from merge.
- Add portainer installation files and documentation.
- Remove hardcoded search model variable name from ``search_box.html``
  template.
- Fix the search model API URL reference. Closes GitLab issue #1098. Thanks
  to Bastian (@Basti-Fantasti) for the report.
- Use the ``SEARCH_MODEL_NAME_KWARG`` instead of hard coding the search model
  API URL reference.
- Filter trashed documents from the tag document count column.
- Filter trashed documents from the cabinet document retrieval method. This
  brings code parity with tags which work in a very similar way.
- Improve Python 3.10 compatibility. Add a compatibility module to
  encapsulate import of the ``Iterable`` class. Improves GitLab issue #1083.
  Thanks to Bw (@bwakkie) for the report and code samples.
- Type cast LUT values when masking an asset for pasting via Pillow's
  ``point()``.
- Document metadata edit form validation updates:

  - Remove ``disabled`` attribute from the metadata type label field to
    avoid having its value removed when there is a validation error.
  - Remove the ``required`` flag from the value field when there is a
    required metadata for a document. The previous behavior cause the tabular
    form to display "(required)" in column title confusing users and causing
    them to think that all metadata type fields were required.
  - Raise validation error for specific required metadata entries and no for
    the entire form. This help users better understand which metadata field
    needs to be corrected.
  - Improve the required metadata validation logic to take into account
    existing values and empty forms when data was entered into the field
    but the update checkbox was left unchecked.

- Bulk object search indexing updates:

  - Retry failed bulk indexing tasks.
  - Add max retry value to ``task_index_search_models``.
  - Improve tasks error logging.

- Update the Debian Docker image from version 11.2-slim to 11.3-slim.
- Downgrade the Python Docker image from version 3.11-slim to 3.10-slim.
- Pin Jinja2 version to workaround Sphinx bug. Sphinx Jinja2 dependency is
  not pinned or immutable, and causes the installation of an incompatible
  version breaking builds.

4.2.3 (2022-04-01)
==================
- Add restart policy to the Traefik container definition.
- Remove duplicated ``Document.get_label`` method.
- Fix an issue where a staging folder would not tag uploaded
  documents.

4.2.2 (2022-03-21)
==================
- Ensure the object copy permission is required for the object copy link.
- Migrate old workflow ``EmailAction`` instances instead of sub-classing
  for backwards compatibility. Improves commit
  ``b522dac80f7f6cfb8c5db8a74d6d2d22bc8b281a`` and avoids a double entry in
  the workflow state action selection downdown list.
- Ensure new document and file links access works like their respective
  views. The links will be active when the access is granted for the source
  as well as the document/document type.
- Filter unread message count badge by message read permission.
- Update document metadata model field label from "Metadata type value"
  to "Metadata value".
- Fix document file signature serializer label.

4.2.1 (2022-02-16)
==================
- Merge improvements from version 4.1.6.

  - Append the text "signed" to the label of a signed document file instead
    of using the temporary filename used during signing.
  - Ensure the signed document file is used when the file downloaded is
    requested and when calculating the signed document file checksum.
    Solves issue in forum post 6149. Thanks to forum user @qra for the report
    and debug information.
  - Update IMAP source ``store commands`` to be optional.
  - Update email sources ``SSL`` checkbox to be optional.
  - Undo POP3 source context manager changes from commit
    c19040491e20c9a783ae6191613bc8c5f7acb038. It seems Python's email libraries
    do not have feature parity. ``imaplib`` was updated to support context
    managers but ``poplib`` was not.

- Update requirements to specify Python version 3.6 to 3.9.
- Update Django version 3.2.11 to 3.2.12.

4.2 (2022-02-12)
================
- Update Django to version 3.2.11.
- Update django-widget-tweaks from version 1.4.8 to 1.4.9.
- File staging sources updates:

  - Use ``StreamingHttpResponse`` to serve previews.
  - Support office document files for preview.
  - Fix extra brackets in the encoded and cached filenames.
  - Simplify image generation.
  - Use context manager to ensure preview images are always closed.

- Hide all links that depend on users being authenticated.
- Add support for return binary content in batch API requests as a base64
  string.
- Add support for dynamic field API serialization. This feature adds the
  URL query keys ``_fields_only`` and ``_fields_exclude``. Nested serializers
  are supported using the double underscore (``__``) separator.
- Refactor ``ResolverRelatedManager``.
- Move Docker templates to their own folder.
- Move the ``docker-dockerfile-update`` target to the Docker makefile.
- Update Docker image tags:

  - Postgresq from 10.18-alpine to 12.9-alpine.
  - Python from 3.8-slim to 3.11-slim.

- Update psycopg2 from version 2.8.6 to 2.9.2.
- Update redis client from version 3.5.3 to 4.0.2.
- Reduce the Sentry client default ``traces_sample_rate`` from 0.25 to 0.05.
- Add the ``run_initialsetup_or_performupgrade`` command to the Docker
  entrypoint.
- Docker Compose updates:

  - Add a Redis profile.
  - Default to RabbitMQ a broker.
  - Change default RabbitMQ image from 3.9-alpine to 3.9-management-alpine.
  - Improve Traefik configuration.
  - Add a dedicated network for Traefik.

- Completed the Whoosh backend and made it the default search backend.

    - Ensure all test models are deleted, including intermediate many
      to many models created automatically.
    - Update ``DetailForm`` usage for the new interface.
    - Move `flatten_list` to the common app.
    - ResolverPipeline updates:

      - Support ``resolver_extra_kwargs``.
      - Add queryset exclusion support to ``ResolverRelatedManager``.

    - Update related field resolution using pure Django
    - Solve all search indexing edge cases.
    - Models are indexed using smaller tasks to improve scalability.
    - Refactor ``ResolverRelatedManager``. Use Django's internal
      ``get_fields_from_path`` for related field introspection.
      Support more related field cases.
    - Trigger indexing on related model changes
    - Fix lock manager management command test.
    - Don't index `None` values in lists.
    - Unify the search test mixins.
    - Use ``TemporaryDirectory`` for test search backend. Do automatic
      clean up of the temporary index directory.
    - Remove the separate related model index signal handlers.
    - Make Whoosh the default search backend.
    - Support reverse many to many indexing.
    - Add indexing optimizations.
    - Rename methods for clarity.
    - Move the ``any_to_bool`` function to the common app.

- Update base image from Debian 10.10-slim to 11.1-slim.
- Move the ``parse_range`` utility from the documents app to the common app.
- Retry Whoosh LockErrors by encapsulating then in the general app exception
  ``DynamicSearchRetry``.
- Added the ``search_index_objects`` management command to trigger the
  queuing of search models from the CLI.
- Added the ``search_status`` management command to show indexing status of
  the search backend.
- Move SQLite check to the databases app.
- Add support for inclusion and exclusion regular expressions for watch
  folders. Closes GitLab issue #965. Thanks to Sven Gaechter (@sgaechter)
  for the request.
- MIME type app updates:

  - Add support for MIME type detection backends.
  - Add PERL ``mimetype`` backend.
  - Add Linux ``file`` command backend.
  - Rename ``mimetype`` app to ``mime_types``.

- Add a search backend for Elastic Search.
- Search app updates:

  - Support initializing the search backends.
  - Add method to reset backends.
  - Moved ``get_resolved_field_map`` and ``get_search_model_fields`` to the
    ``SearchBackend`` class.
  - Normalize true values for scope 0 ``match_all``.
  - Added a new task ``task_reindex_backend`` to abstract backend reindexing.
  - Add constant maximum retries value to the ``task_deindex_instance`` and
    ``task_index_instance`` tasks.
  - Add ranged search model indexing.
  - Add the ``search_slow`` queue for long running search tasks.
  - Support backend initialization, reset, and tear down.
  - Automatically add the ``id`` field as a search field for all search
    models.
  - Separate backend initialization from app initialization.

- Add Elasticsearch test container makefile targets.
- Unify the files ``.env`` and ``env_file``.
- Switch all standalone containers to use a ``prefetch-multiplier`` of ``1``.
- Change the Docker Compose network name from ``bridge`` to ``mayan``.
- Add the ``search_initialize`` and ``search_upgrade`` management commands.
  These are called automatically after the initial setup and after upgrades.
- Add new search settings called ``SEARCH_INDEXING_CHUNK_SIZE`` to set the
  number of objects to prepare when performing bulk indexing.
- Metadata validation and parsing updates:

  - Expand the parser and validator path fields to 224 characters.
  - Add automatic registration of parsers and validators.
  - Add support for passing arguments to parsers and validators.
  - Add a regular expression parser to replace values and a regular
    expression validator.

- Authentication refactor:

  - Subclass Django's authentication views to add multi form and multi factor
    authentication.
  - Add support for authentication backends. Authentication backends are
    able to control and customize the entire login process, including
    the forms presented to the user. Authentication backends can use mixins
    and can be subclassed to mix and expand their capabilities.
    Included authentication mixins: ``AuthenticationBackendRememberMeMixin``
    Included authentication backends:
    ``AuthenticationBackendModelDjangoDefault``,
    ``AuthenticationBackendModelEmailPassword``,
    ``AuthenticationBackendModelUsernamePassword``.
    Apps define authentication backends in the module
    ``authentication_backends.py``.
  - Removed the now unused ``EmailAuthBackend`` class.
  - New settings:

    - ``AUTHENTICATION_BACKEND`` which must be the dotted path
      to the backend used to process user authentication.
    - ``AUTHENTICATION_BACKEND_ARGUMENTS`` which is an optional YAML
      structure to pass to the authentication backend.

- Add Time based One Time Password (TOTP) support. To enable set the
  setting ``AUTHENTICATION_BACKEND`` to
  ``mayan.apps.authentication_otp.authentication_backends.AuthenticationBackendModelUsernamePasswordTOTP``
  for username and TOTP login. For email and TOTP logins use
  ``mayan.apps.authentication_otp.authentication_backends.AuthenticationBackendModelEmailPasswordTOTP``.
  New management commands to support OTP:

    - ``authentication_otp_disable``: disables OTP for a user
    - ``authentication_otp_initialize``: initializes the OTP state data for
      all users. This command is for debuging and maintenance in case the
      database migration does not correctly initialize the OTP state data
      for existing users.
    - ``authentication_otp_status``: display the OTP status for a user

- Add URL links to the document file and document version first pages
  to the document serializer in the API.
- Convert the download file deletion interval into a setting named
  ``DOWNLOAD_FILE_EXPIRATION_INTERVAL`` which defaults to 2 days.
- Convert the shared uploaded file deletion interval into a setting named
  ``SHARED_UPLOADED_FILE_EXPIRATION_INTERVAL`` which defaults to 7 days.
- Don't display API URL links to indexing instance and template parents that
  are also root nodes as these are not accessible.
- Register more models using ``DynamicSerializerField`` to display the
  canonical serializer of the model when referenced by other objects.
- For object that have children objects or that support nesting, the parent
  object ID is now added to the serializer. The layout is
  ``{parent object name}_id``. A few objects already provided the parent ID
  but with a different schema. These objects also now have the parent ID
  field with the new schema even if it displays a duplicate value. The old
  ID field is now deprecated and will be removed in version 5.0.
- Added a workflow state column displaying all created actions labels
  separated by a comma.
- Added the mailing profile created and edited events.
- User menu and views updates:

  - Reorganize all user links under a single "User details" link.
  - Allow editing the locale profile of users.
  - Allow editing the theme settings of users.
  - Unify user data related views.
  - Add "User theme edited" and "User locale profile edited" events.

- Update the Django debug view CSS and layout to match Django's original
  appearance.
- Support Django debug JavaScript code.
- Minor CSS optimization to the Django debug view.
- Add Docker Compose password randomizer.
- Include LDAP libraries and Python modules.
- Events app updates:

  - Use the correct attribute for fetching event types. Use ``id`` instead of
    ``name``.
  - Cache the event type instance in the StoredEvent model.
  - An incorrect event type ID will now return a KeyError instead of masking
    the exception and returning an error message. It is now up to the calling
    code which action to take when the event type ID is not correct.
  - The previous unknown event error message is now available as a literal
    named ``literals.TEXT_UNKNOWN_EVENT_ID``.

- Add workflow template transition trigger API. Closes GitLab
  issue #1044. Thanks to Ludovic Anterieur (@lanterieur) for
  the request and research.
- Fine tune workflow template permissions to require the view permission
  instead of the edit permission when applicable.
- Error log updates:

    - Added a global error log list to the tools menu.
    - Error log partitions now link to their underline object via content type
      too.
    - Error log partitions are now retrieve or created on demand.
    - Added cascade permission support to error log partitions and entries.

- Update the ``ObjectActionAPIView`` view to allow passing extra context to
  serializers.
- Add support for launching workflows from the API.
- Refactor language activation to work with Django 3.2.
- Added the mailing profile created and edited events.
- Remove workflow instance exception usage. Current state property is now
  inspected.
- Remove menu proxy inclusions. Model proxies are now included by default.
- Add menu proxy exclusions.
- Update the subject and body fields of the document email workflow action
  to be optional.
- Redirect to current user to user detail view after password change.
- Support two different ``psycopg2`` versions for upgrade testing.

4.1.9 (2022-04-24)
==================
- Remove hardcoded search model variable name from ``search_box.html``
  template.

4.1.8 (2022-04-23)
==================
- Fix the search model API URL reference. Closes GitLab issue #1098. Thanks
  to Bastian (@Basti-Fantasti) for the report.
- Use the ``SEARCH_MODEL_NAME_KWARG`` instead of hard coding the search model
  API URL reference.
- Merged changes from version 4.0.22:

  - Remove usage of flat values list in document checkout manager.
  - Remove usage of flat ``values_list`` queryset in metadata managers module.
  - Cleanup markup of the confirmation form.
  - Remove redundant modal close button.
  - Fix search proxies method decorator.
  - Reorganize converter office MIME type list.
  - Improve metadata validation error message.
  - Don't display API URL links to indexing instance and template parents that
    are also root nodes as these are not accessible.
  - Remove repeated partition file close call.
  - Update Django version 2.2.24 to 2.2.28.

- Reduce the Sentry client default ``traces_sample_rate`` from 0.25 to 0.05.
- Add keyword argument to ``self.stderr`` and ``self.stdout`` usage.
- In ``FilteredRelatedFieldMixin``, split retrieval of the queryset to
  avoid the exception handler from capturing an ``AttributeError`` that it
  shouldn't.
- Updated the ``subject`` and ``body`` fields of the document email
  workflow action to be optional.
- Migrate old workflow ``EmailAction`` instances instead of sub-classing
  for backwards compatibility. Improves commit
  ``b522dac80f7f6cfb8c5db8a74d6d2d22bc8b281a`` and avoids a double entry in
  the workflow state action selection dropbox.
- Partials navigation updates:

  - Streamline JavaScript partials navigation code.
  - Make the AJAX response redirect code configurable. New setting
    ``APPEARANCE_AJAX_REDIRECTION_CODE`` added.
  - Remove repeated AJAX redirection middleware.

- Add keyword arguments to zip file calls.
- ``PartialNavigation.js`` improvements.

  - Clean URL query on form submit and use form data as the URL query.
  - Remove dead code.
  - Use constants where appropriate.

- Backport new document link condition logic. Ensure new document and file
  links access works like their respective views. The links will be active
  when the access is granted for the source as well as the document/document
  type. Closes GitLab issue #1102. Thanks to Julian Marié (@Angelfs) for the
  report and debug information.
- Improve logic of the new document file link

  - Access the view user in a more reliable way.
  - Test the new file permission of the document and not
    of the document type.
  - If no document is present in the view exit fast.
  - Update tests.

4.1.7 (2022-04-01)
==================
- Backport fixes from version 4.2.3

  - Add restart policy to the Traefik container definition.
  - Remove duplicated ``Document.get_label`` method.
  - Fix an issue where a staging folder would not tag uploaded
    documents.
  - Fix document file signature serializer label.
  - Update document metadata model field label from "Metadata type value"
    to "Metadata value".
  - Filter unread message count badge by message read permission.
  - Update signature view permission label from
    "View details of document signatures" to "View document signature".
  - Ensure the object copy permission is required for the object copy link.
  - Fix ``GUNICORN_REQUESTS_JITTER`` documentation setting name reference.

4.1.6 (2022-02-15)
==================
- Append the text "signed" to the label of a signed document file instead
  of using the temporary filename used during signing.
- Ensure the signed document file is used when the file downloaded is
  requested and when calculating the signed document file checksum.
  Solves issue in forum post 6149. Thanks to forum user @qra for the report
  and debug information.
- Update IMAP source ``store commands`` to be optional.
- Update email sources ``SSL`` checkbox to be optional.
- Undo POP3 source context manager changes from commit
  c19040491e20c9a783ae6191613bc8c5f7acb038. It seems Python's email libraries
  do not have feature parity. ``imaplib`` was updated to support context
  managers but ``poplib`` was not.
- Update requirements to specify Python version 3.5 to 3.9.
- Update Django version 2.2.24 to 2.2.27.

4.1.5 (2022-02-03)
==================
- Fix CAA document links. Closes GitLab issue #1068. Thanks to
  Matthias Löblich (@startmat) for the report.
- Remove superfluous apostrophe character in sort heading markup.
- Fix email sources processing a single message but performing cleanup on
  multiple messages. The intended behavior is restore which processed one
  message and cleans up the processed message only.
- Fix reference to ``shared_uploaded_files`` before the variable being
  available.
- Use context managers for the IMAP and POP3 sources to remove the
  possibility of orphaned descriptors.
- Create error log entries for objects that existed before the last error
  log changes. Fix GitLab issue #1069. Thanks to Will Wright (@fireatwill)
  for the report.
- Expose the workflow template ``auto_launch`` field via the REST API.
  Thanks to forum user @qra for the request.
- Add ``EmailAction`` subclass for backwards compatibility with existing
  workflow state actions.
- Expose the checkout datetime, expiration datetime and user fields via the
  REST API. Thanks to forum user @qra for the request.
- Print configuration path value when failing to access error is raised.
- Fix references to the ``SourceBackendSANEScanner`` source backend class.
- Reorganize the testing setting modules.
- Remove unused MySQL testing setting module.

4.1.4 (2021-12-01)
==================
- Changes merged from versions 4.0.20 and 4.0.21.

  - Perform more strict cleanup of test models.
  - Clean up the test model app config cache after the test
    end not before the test model is created.
  - Improve lock manager test cases.
  - Add standalone Celery beat container.

- Fix document version first page thumbnail image resolution.
  Closes GitLab issue #1063. Thanks to Will Wright (@fireatwill)
  for the report and the patch.
- Add libjpeg and libpng to the dev setup target.
- Fix editing OCR content via the API.
- Fix the ``AdvancedSearchViewTestCaseMixin`` class. It had
  ``GenericViewTestCase`` as a base class when it is supposed to be a mixin
  and not have any.
- Add ``AutoHelpTextLabelFieldMixin``. This mixin tries to extract the
  label and help text from the model field when the serializer field does
  not specify any.
- Add filtering to the ``parent`` field of the index template node
  serializers. Restrict options to the current index template and allows
  removing the now redundant validation.
- Add ``index_template_root_node_id`` field to the index template
  serializer. Closes GitLab issue #1061. Thanks to
  Ludovic Anterieur(@lanterieur) for the report and initial implementation.
- Fix responsive menu close button triggering home navigation. Closes
  GitLab issue #1057. Thanks to Raimar Sandner (@PiQuer) for the report and
  debug information.
- JavaScript optimizations:

  - Cache argument length when in ``.fn.hasAnyClass``.
  - Configure fancybox just once.
  - Set converter image functions as ``async``.
  - Remove jQuery's ``one`` usage.

- Remove the error logger model locking and cache the model value instead
  at the time of registration. Closes GitLab issue #1065. Thanks to
  Will Wright (@fireatwill) for the report and debug information.
- Rename ``ErrorLog`` model to ``StoredErrorLog``. This change follow the
  normal paradigm when a service is provided by a model and a runtime class.
- Make the ``StoredErrorLog`` name field unique to ensure ``get_or_create``
  works in an atomic way.
- Create the error log partition when the model instance is created.
- Normalize the error log partition name format using a static method.
- Delete the error log partition on model instance deletion and not just the
  error log partition entries.
- Ensure a memory database is used when running the tests.

4.1.3 (2021-11-02)
==================
- Vagrant updates

  - Load installation value from ``config.env`` file.
  - Update supervisord during installation.
  - Setup the APT proxy during installation.
  - Change how APT and PIP proxies are defined to match the Docker build
    target.
  - Add makefile for vagrant.
  - Move devpi targets to the main makefile.

- Sentry client backend updates:

  - Add more SDK options.
  - Add typecasting to options.
  - Add debug logging.
  - Add Celery integration.
  - Add Redis Integration.
  - Lower the default value of ``traces_sample_rate`` from 1 to 0.25.
    This value is better suited for production deployments. Increase to 1
    for full debug information capture during development or testing.

- File staging sources updates:

  - Use ``StreamingHttpResponse`` to serve previews.
  - Support previews for office document files.
  - Fix extra brackets in the encoded and cached filenames.
  - Simplify image generation.
  - Use context manager to ensure preview images are always closed.

- Sources app updates:

  - Don't assume all source backends provide an upload form.
  - Improve SANE scanner error handling.
  - Fix logging of non interactive source errors.
  - Show interactive source processing as a message.

- Fix the copying of the bootstrap alert style.
- Optimize the copying of the boostrap alert style by executing it only
  in the root template. This runs the code just once instead of running it
  on each page refresh. The element ``#div-javascript-dynamic-content`` was
  also remove and it is now created and destroyed dynamically once just.
- Ensure that the ``resolved_object`` is injected into the context before
  passing the context to the link's ``check_condition`` method. Suspected
  cause of the GitLab issue #1052 and #1049. Thanks to Ludovic Anterieur
  (@lanterieur) and Johannes Bornhold (@joh5) for the reports and debug
  information.
- Converter updates:

  - Fix duplicate asset display. Closes GitLab issue #1053. Thanks to
    Ryan Showalter (@ryanshow) for the report.
  - Split the transformation ``cache_hash`` method to allow subclasses to
    modify how the cache hash is calculated.
  - Include the asset image hash into the asset transformation hash
    calculation. This change invalidates all cached page images that
    use an asset if the asset image is modified.
  - Improve the way the absolute coordinates of the percentage asset paste
    transformation are calculated.

- Use redirection instead of the ``output_file`` argument to allow the SANE
  scanner source to work with more SANE scanner versions.

4.1.2 (2021-10-27)
==================
- Don't insert the value ``ORGANIZATIONS_URL_BASE_PATH`` in the path
  then it is ``None``.
- Fix ``ModelTemplateField`` not displaying the ``initial_help_text``
  for the specific usage instance. The ``initial_help_text`` was
  being removed from the ``kwargs`` in the ``ModelTemplateField``
  as well as the super class.
- Workflows improvements.

  - Use the templating widget for the workflow document properties
    modification and the HTTP request actions.
  - Consolidate the workflow action help text.

- Fix issue when attempting to create a Document version page OCR update
  workflow action. Instead of the model class, the template form field now
  passes the ``app_label`` and the ``model_name`` of the model via the
  widget attributes to avoid Django's attribute template to attempt
  getting a string representation of the model.

4.1.1 (2021-10-26)
==================
- Move Docker Compose variables to the correct file. Move
  ``COMPOSE_PROJECT_NAME`` and ``COMPOSE_PROFILES`` to the
  .env file.
- Fix asset image generation. Closes GitLab issue #1047 for series 4.1.
  Thanks to Ryan Showalter (@ryanshow) for the report and debug information.
- Improve sidebar menu heading display logic.
- Fix leftover HTML markup in the server error dialog window.
- Remove redundant close button for the server error dialog window.
- Merged fixes and improvements from versions 4.0.17 and 4.0.18.
- Update PIP from version 21.2.4 to 21.3.1.
- Remove MySQL upgrade CD/CI testing pipeline stage until support is properly
  re-implemented for version 8.0.
- Add CD/CI triggers for local testing.
- Exclude all migration tests by tagging automatically at the
  ``MayanMigratorTestCase`` subclass definition.
- Support multiple environments per dependency.
- Update the ``wheel`` library to be a dependency of the ``build`` and the
  ``documentation`` environments to workaround a bug in PIP that causes
  ``"error: invalid command 'bdist_wheel'"``.

4.1 (2021-10-10)
================
- Add support for editing the document version page OCR content.
  Closes GitLab issue #592. Thanks for Martin (@efelon) for the
  request.
- Refactor sources app.

  - Add object permission support to source views.
  - Remove locking support from staging folder uploads.
  - Update staging preview to use new preview generation
    code.
  - Use streaming response to serve staging folder images.
  - Convert the sources from models into backend classes.
    The sources are now decoupled from the app. Each source
    backend can defined its own callbacks and use an unified
    background task.
  - Perform code reduction. Remove PseudoFile and SourceUploaded
    classes. Each source backend is now responsible for providing
    a list of shared uploaded files.

- Multiform improvements:

  - Support multi form extra kwargs.
  - Move the dynamic part of the multi form method to the end
    of the name.
  - Add a white horizontal ruler to separate the form
    instances.

- Consolidate the image generation task:

  - Remove document file, version, converter asset, and workflow template
    preview image generation.
  - Remove converter literal `TASK_ASSET_IMAGE_GENERATE_RETRY_DELAY`.
  - Remove workflow literals `TASK_GENERATE_WORKFLOW_IMAGE_RETRY_DELAY`.
  - Remove `document_states_fast` queue.
  - Remove documents literals
    `DEFAULT_TASK_GENERATE_DOCUMENT_FILE_PAGE_IMAGE_RETRY_DELAY` and
    `DEFAULT_TASK_GENERATE_DOCUMENT_VERSION_PAGE_IMAGE_RETRY_DELAY`.
  - Remove settings
    `DOCUMENT_TASK_GENERATE_DOCUMENT_FILE_PAGE_IMAGE_RETRY_DELAY` and
    `DOCUMENT_TASK_GENERATE_DOCUMENT_VERSION_PAGE_IMAGE_RETRY_DELAY`.

- Search updates

  - Remove `TASK_RETRY_DELAY` and use `retry_backoff`.
  - Add the tag color as a search field
  - Improve and simplify query cleaning up by doing so after the
    scopes are decoded.
  - Fix Whoosh reindexing after m2m fields perform a remove.
  - Fix Whoosh search for related m2m fields with multiple
    values.
  - Improve tests for edge cases.
  - Fix document version API tests module.
  - Variables renamed for clarity and to specify their purpose.
  - Process the 'q' parameter at the class and not in the
    backend.
  - Ignore invalid query fields.
  - Index for search on m2m signal.
  - Return empty results on an empty query.
  - Produce an empty scope 0 on an empty query.
  - Improve tests.
  - Add UUID field for all document child objects.

- Add detail view for groups.
- Show total permission when running the `purgepermissions` command.
- Add detail for file partitions.
- Add placeholder absolute links for announcements, workflow templates, quotas.
- Add detail view for stored permissions.
- Rename role setup views.
- Load user management first to allow patching
- Register ACL events when enabling ACLs. Objects that are registered to
  support ACLs will also be registered for ACL events to allow subscribing to
  ACL changes of the object.
- Allow bind either the events links, the subscription link, both or none.
- Improve workflow app navigation.
- Improve sidebar navigation.
- Improve clarity of the action dropdown sections.
- Make the index instance node value field an unique field among its own tree
  level. This prevents tree corruption under heavy load.
- Update dependencies:

  - Docker Compose from 1.29.1 to 1.29.2
  - PostgreSQL Docker image from 10.15-alpine to 10.18-alpine
  - RabbitMQ Docker image from 3.8-alpine to 3.9-alpine
  - Redis Docker images from 6.0-alpine to 6.2-alpine
  - psycopg2 from 2.8.6 to 2.9.1
  - psutil from 5.7.2 to 5.8.0
  - jQuery from 3.5.1 to 3.6.0
  - jquery-form from 4.2.2 to 4.3.0
  - jquery-lazyload from 1.9.3 to 1.9.7
  - urijs from 1.19.1 to 1.19.7
  - bleach from 3.1.5 to 4.0.0
  - jstree from 3.3.3 to 3.3.11
  - PyYAML from 5.3.1 to 5.4.1
  - django-model-utils from 4.0.0 to 4.1.1
  - requests from 2.25.1 to 2.26.0
  - sh from 1.14.1 to 1.14.2
  - devpi-server from 5.5.1 to 6.2.0
  - django-debug-toolbar from 3.1.2 to 3.1.4
  - django-extensions from 3.1.2 to 3.1.4
  - django-rosetta from 0.9.4 to 0.9.7
  - flake8 from 3.9.0 to 3.9.2
  - ipython from 7.22.0 to 7.26.0
  - safety from 1.9.0 to 1.10.3
  - transifex-client from 0.14.2 to 0.14.3
  - twine from 3.4.1 to 3.4.2
  - wheel from 0.36.2 to 0.37.0
  - Pillow from 7.1.2 to 8.3.1
  - packaging from 20.3 to 21.0
  - python_gnupg from 0.4.6 to 0.4.7
  - graphviz from 0.14 to 0.17
  - django-activity-stream from 0.8.0 to 0.10.0
  - pytz from 2020.1 to 2021.1
  - python-dateutil from 2.8.1 to 2.8.2
  - python-magic from 0.4.22 to 0.4.24
  - gevent from 20.4.0 to 21.8.0
  - gunicorn from 20.0.4 to 20.1.0
  - whitenoise from 5.0.1 to 5.3.0
  - cropperjs from 1.4.1 to 1.5.2
  - jquery-cropper from 1.0.0 to 1.0.1
  - django-cors-headers from 3.2.1 to 3.8.0
  - djangorestframework from 3.11.2 to 3.12.4
  - drf-yasg from 1.17.1 to 1.20.0
  - swagger-spec-validator from 2.5.0 to 2.7.3
  - dropzone from 5.7.2 to 5.9.2
  - extract-msg from 0.23.3 to 0.34.3
  - pycryptodome from 3.9.7 to 3.10.1
  - celery from 4.4.7 to 5.1.2
  - django-celery-beat from 2.0.0 to 2.2.1
  - coveralls from 2.0.0 to 3.2.0
  - django-test-migrations from 0.2.0 to 0.3.0
  - mock from 4.0.2 to 4.0.3
  - tox from 3.23.1 to 3.24.3
  - psutil from 5.7.0 to 5.80
  - furl from 2.1.0 to 2.1.2
  - django-test-migrations from 0.3.0 to 1.1.0

- Launch workflows when the type of the document is changed. Closes GitLab
  issue #863 "Start workflows when changing document type", thanks to
  Dennis Ploeger (@dploeger) for the request.
- Add support for deleting multiple metadata types in a single action.
- Tags app updates:

  - Use MultipleObjectDeleteView class.
  - Replace edit icon.
  - Code style updates.

- Move theme stylesheet sanitization to the save method.
- Remove final uses of .six library.
- Add support for clearing the event list.
- Events app updates:

  - Load all events at startup. Does not rely anymore of importing an event
    for it to become recognized.
  - Allow loading events by their name. Avoid doing direct imports when
    there circular dependencies.
  - Move the events app to the top of the installed apps to allow it to
    preload all events.
  - Only show the event clear and export links for object whose events
    that can be cleared and exported.

- ACLs apps updates:

  - The ACL edited event is now triggered only once when all permissions are
    changed.
  - The action object of the ACL edited event is now the content object and
    not the permission.

- Enable event subscriptions for workflow states, workflow state actions,
  and workflow transitions.
- Support deleting multiple roles in a single action.
- OCR app updates:

  - Use ``MultipleObjectDeleteView`` for the delete view.
  - Rename single and multiple delete view names.
  - Improve tests.

- Document comments app API updates:

  - Modernize code to use latest internal interfaces.
  - Exclude trashed documents.
  - Reduce serializers.
  - Return error 404 on insufficient access.

- Document indexing API updates:

  - Exclude trashed documents.
  - Split tests.
  - Add event checking to remaining tests.

- Events app API updates:

  - Return error 404 on insufficient permissions.
  - Modernize `APIObjectEventListView` to use latest interfaces
    and mixins.

- Document parsing app updates:

  - Update API to latest internal interfaces.
  - Add testing for multiple document file content delete views.
  - Speed up tests.
  - Add event checking to tests.
  - Use `MultipleObjectDeleteView` for the file content delete view.
  - Improve text string of the `DocumentFileContentDeleteView` view.

- Document signatures app updates:

  - Exclude trashed documents from the API.
  - Add event checking to tests.
  - Track user when uploading signature files.

- Workflows app updates:

  - Split API views.
  - Add trashed document test.
  - Code style updates.

- Smart link app refactor:

  - Exclude trashed documents from API.
  - Improve existing tests.
  - Add additional tests.
  - Rebuild the resolved smart link API and serializer.
  - Add a new permission to view resolved smart links. This permission needs
    to be granted for the smart link and for the document/document type.
  - Update API to return error 404 on insufficient access.
  - Remove unused test mixins.
  - Split view and API test modules.

- Documents app updates:

  - Exclude trashed documents from all API views.
  - New `valid` model managers for recently accessed, recently created, and
    favorite documents. These managers exclude trashed documents at the model
    level. The 'objects' manager for these model returns the unfiltered
    queryset.
  - Trashed document delete API now returns a 202 code instead of 204. The
    delete method now runs in the background in the same way as the trashed
    document delete view works in the UI. The return code was updated to
    reflect this internal change.
  - Track the user for the trashed document delete, restore and for the
    trash can empty methods.
  - Add event checking for some remaining tests.
  - Add additional tests.

- Add ``BackendDynamicForm``, a dynamic form for interacting with backends.
- Add a reusable backend class named ``mayan.apps.databases.classes.BaseBackend``.

- Refactor mailer app:

  - Allow sending document files and document versions as attachments.
  - Update the ``UserMailer`` model to work with the ``BackendModelMixin``
    mixin. This allows removing all backend managing code from the model.
  - Generate the dynamic form schema in the base backend class. Removes
    dynamic form schema from the views.
  - Use ``BackendDynamicForm`` and remove dynamic form code from the forms
    module.
  - Generalize document file and document version to support any type of
    object.
  - Update workflow action to send links to documents or attach the active
    versions.
  - Use the reusable ``BaseBackend`` class and remove explicit backend
    scaffolding.

- Improve test open file and descriptor leak detection.
- Close storage model file after inspection as Django creates a new
  file descriptor on inspection.
- Ensure the name and not the path is used. Compressed files can include
  path references, these are now scrubbed and only the filename of the file
  in the compressed archive is used.
- File handling was improved. Context managers are now used for temporary
  files and directories. This ensure file descriptors are closed and freed up
  in all scenarios.
- Add detached signature deleted event.
- Document signature app general improvements. Renamed links, icons and
  view for clarity. Split tests modules.
- Metadata API updates:

  - Unify document type metadata type serializers.
  - Update the permission layout to match the one of the views.
    The edit or view permission is now required for the document
    type as well as the metadata type.

- Add ``CONVERTER_IMAGE_GENERATION_MAX_RETRIES`` to control how many times
  the image regeration task will retry lock errors.
- Add support for appending all document file pages as a single document
  version.
- Moved signals, hooks and events outside of the document file creation
  transaction.
- Capture the user for the document version page reset and remap action
  events.
- Add conditions to the favorite document links.
- Update mailing icons.
- Remove submit button label and submit button icons.
- The ``performupgrade`` command won't try to hide critical errors and
  instead raise any exception to obtain the maximum amount of debug
  information.
- Add support to filter the add/remove choice form.
- Dependencies app updates:

  - Move the link to check for the latest version to the tools
    menu.
  - Checking for updates now required the view dependencies
    permission.

- Unify request resolution for navigation classes.
- Support retrieving a list of ``SourceColumn`` by name.
- Dashboard app updates:

  - Extend dashboard widget interfaces.
  - Add list dashboard widget.
  - Move dashboard CSS from the appearance app to the dashboards app.
  - Add dashboard list and detail views.
  - Add setting to select the default dashboard.
  - Add template tag to display the default dashboard in the home
    view.

- Refactor ``SourceColumn.get_for_source``.
- Add ``RecentlyAccessedDocumentProxy`` to allow adding a column with the
  creation date time.
- Navigation refactor:

  - Rewritten link to source matching code.
  - Rewritten menu resolution.
  - Pass the ``resolved_object`` to link conditions.

- Don't trigger the settings change flag on user language changes.
- Add settings to allow changing the default and the maximums
  REST API page size.
- Add support for service client backends to the platform app.
- Add Sentry.io service client backend.
- Support overriding form buttons.
- Improve metadata type form tab order. Disables metadata type name field
  to skip them during tabbing.
- Support step rewinding for the sources wizard.
- Add support for recoding email Message ID. The email source can now record
  an email Message ID from the header as it is processed into a documents.
  All documents created from the same email will have the same Message ID.
  Thanks to forum user qra (@qra) for the request.

- Improve `BaseBackend` class

  - Add deterministic parent base backend class detection.
  - Register backend class only to their respective parent base
    backend classes.

- Render main menu icons properly. The change in
  bbbb92edb85f192987fdfb4efc574bd79221b6ed removed literal CSS icon
  support. A single reference to the old CSS icon render was left behind
  which cause the icon object Python memory location to be rendered
  inline with the menu HTML. This cause the same menu to have different
  hashes when rendered by the different Gunicorn workers. Solved GitLab
  issue #1038. Thanks to Ludovic Anterieur (@lanterieur) for the report.
- Add setting to change the menu polling interval. Values specified in
  milliseconds. Use `None` to disable.
- Enforce ``CONVERTER_IMAGE_GENERATION_MAX_RETRIES`` setting and add logging
  message when the maximum retires are exhausted.
- Messaging app updates:

  - Add API views.
  - Exclude superusers and staff users from being message recipients.
  - Add dedicated create message form.
  - Use Select2 for the user selection field.
  - Add message edit permission. This permission is required in order to
    change the message read status.

- Add ``get_absolute_api_url`` method to download files, document versions
  and users. These URL are used to determine the message sender's API URL.
- Test view mixin updates:

  - Add a default ordering to the ``TestModel`` to silence warning.
  - Fix ``TestModel.save()`` method.
  - Support multiple test views per test case.
  - Allow subclasses to supply their own ``urlpatterns``.
  - Support passing arguments to ``add_test_view``.

- Add batch API request support.
- Adjust event registrations:

  - Register cabinet document add and remove events to the Document model too.
  - Register document file parsing events to the Document model too.
  - Rename label of the document parsed content deleted event.
  - Replace the ``DownloadFile`` content object registration from the
    ``Document`` model to the ``DocumentVersion`` model.
  - Register the document file created, edited events to the ``Document``
    model too.
  - Register the document version created, edited events to the ``Document``
    model too.
  - Register the document trashed event to the ``Document`` model too.
  - Remove the document file created event from the ``DocumentFile`` model.
  - Remove the document version created event from the ``DocumentVersion``
    model.
  - Register the document version page deleted event to the
    ``DocumentVersion`` model.
  - Remove the document version page deleted event from the
    ``DocumentVersionPage`` model.
  - Register the tag attached, removed events to the ``Document`` model too.
  - Register the web link navigated event to the ``Document`` model too.
  - Remove the document version page OCR edited event from the ``Document``
    model.
  - Register the document version OCR submitted, finished, content deleted
    events to the ``DocumentVersion`` model.

- Sort object and list facet links when using the list item view.
- Rename environment variable ``MAYAN_GUNICORN_JITTER`` to
  ``MAYAN_GUNICORN_REQUESTS_JITTER``.
- Support changing the operating system user when creating the supervisord
  file using the environment variable ``MAYAN_OS_USERNAME``.
- Reorder the Gunicorn arguments.
- Make the ``DJANGO_SETTINGS_MODULE`` environment variable an alias of
  ``MAYAN_SETTINGS_MODULE`` in the supervisord file.
- Add ``MAYAN_GUNICORN_TEMPORARY_DIRECTORY`` to the gunicorn invocation in
  the ``run_frontend.sh`` batch file.
- Frontend updates:

  - Ensure list groups use <ul> and <li> instead of plain <div>.
  - Move ``mayan_image.js`` to the converter app.
  - Update ``afterBaseLoad`` to work by defining a list of callbacks. This
    allows defining callbacks from different apps.
  - Set JavaScript callbacks and setup method to run in async mode.
  - Move static inline app CSS to individual CSS files.
- Fix workflow template API description text. Closes GitLab issue #1042.
  Thanks to Ludovic Anterieur (@lanterieur) for the report.
- Add document template state action API endpoints. Closes GitLab issue #1043
  Thanks to Ludovic Anterieur (@lanterieur) for the request.
- Pin jsonschema to version 3.2.0 to avoid errors with

4.0.22 (2022-04-22)
===================
- Filter unread message count badge by message read permission.
- Remove usage of flat values list in document checkout manager.
- Remove usage of flat ``values_list`` queryset in metadata managers module.
- Ensure the object copy permission is required for the object copy link.
- Update signature view permission label from
  "View details of document signature" to "View document signatures".
- Update document metadata model field label from "Metadata type value"
  to "Metadata value".
- Fix document file signature serializer label.
- Add restart policy to the Traefik container definition.
- Remove duplicated ``Document.get_label`` method.
- Add Docker Compose file port comment to remove when using Traefik.
- Print the path when failing to access the configuration file.
- Expose the workflow template ``auto_launch`` field via the REST API.
  Thanks to forum user @qra for the request.
- Cleanup markup of the confirmation form.
- Remove redundant modal close button.
- Fix search proxies method decorator.
- Reorganize converter office MIME type list.
- Improve metadata validation error message.
- Don't display API URL links to indexing instance and template parents that
  are also root nodes as these are not accessible.
- Remove repeated partition file close call.
- Update Django version 2.2.24 to 2.2.28.

4.0.21 (2021-11-29)
===================
- Perform more strict cleanup of test models.
- Clean up the test model app config cache after the test
  end not before the test model is created.
- Improve lock manager test cases.
- Add standalone Celery beat container.
- Backport transformation ``cache_hash`` method split.
  Moved to two functions to allow subclasses to modify
  how the cache hash is calculated.
- Backport asset image cache invalidation.
- Backport asset duplication fix.
- Backport asset percentage position calculation fix.
- Add an explicit default value for ``MEDIA_URL``. Ensures forward
  compatibility with future login dependency versions.
- Move meta tags to their own partial template.
- Add libjpeg and libpng to the dev setup target.

4.0.20 (2021-11-08)
===================
- Use overlay2 driver when using Docker in Docker
  in the GitLab CD/CI stages.
- Update gevent from version 20.4.0 to 21.8.0.
- Update gunicorn from version 20.0.4 to 20.1.0.
- Add more explicit serializer read only fields.

4.0.19 (2021-10-27)
===================
- Backported fixes from version 4.1.2:

  - ``ORGANIZATIONS_URL_BASE_PATH`` null value fix.
  - Fix ``ModelTemplateField`` not displaying the ``initial_help_text``.

4.0.18 (2021-10-21)
===================
- Add settings to allow changing the default and the maximum
  REST API page size.
- Ensure ``ORGANIZATIONS_URL_BASE_PATH`` is applied to properly
  trigger the root SPA template. Closes merge request !91. Thanks
  to Foo Bar(@stuxxn) for the original patch.
- Add support for setting validation.
- Validate the format of the ``ORGANIZATIONS_URL_BASE_PATH``
  setting.
- Smart setting test updates:

  - Add smart setting validation tests.
  - Add setting view tests.
  - Separate namespace and setting tests and mixins.

- Add MySQL workaround for unique document version activation added to
  migration documents 0067 in version 4.0.17.

4.0.17 (2021-10-18)
===================
- Backport workaround for swagger-spec-validator dependency
  bug. Pin jsonschema to version 3.2.0 to avoid errors with
  swagger-spec-validator 2.7.3. swagger-spec-validator does not specify a
  version for jsonschema
  (https://github.com/Yelp/swagger_spec_validator/blob/master/setup.py#L17),
  which installs the latest version 4.0.1. This version removes
  ``jsonschema.compat`` still used by swagger-spec-validator.
- Add ``project_url`` to the Python setup file.
- Add support for ``COMMON_EXTRA_APPS_PRE``. This setting works
  like ``COMMON_EXTRA_APPS`` but installs the new apps before the default
  apps. This allows the extra apps to override templates and other system
  data.
- Fix usage of ``.user.has_usable_password``. Use as a method not a flag.
  Fixes the `Change Password` link appearing even when using external
  authentication.
- Support blank app URL namespaces. These are used to register the
  ``urlpatterns`` of encapsulated libraries as top level named URLs.
- Add a stacked Font Awesome icon class.
- Ensure ``MAYAN_GUNICORN_TEMPORARY_DIRECTORY`` is exported and available to
  ``supervisord``.
- Always change the owner of ``/var/lib/mayan/``. Ensure that the ``mayan``
  operating system user can always read and write from and to the mounted
  volume.
- Fix asset image caching. Closes GitLab issue #1047 for series 4.0.
  Thanks to Ryan Showalter (@ryanshow) for the report and debug information.
- Expand help text of ``ORGANIZATIONS_INSTALLATION_URL`` and
  ``ORGANIZATIONS_URL_BASE_PATH`` settings. GitLab issue #1045. Thanks to
  bw (@bwakkie) for the report.
- Create the ``user_settings`` folder on upgrades too.
- Improve initial setup folder creation error logic. Add keyword arguments.
  Use storages app ``touch`` function.
- Ensure only one document version is active when migrating from version 3.5.
  Forum topic 9430. Thanks to forum user @woec for the report.

4.0.16 (2021-09-29)
===================
- Minor fixes merged from version 3.5.11.
- Remove duplicated makefile targets.
- Add keyword arguments to PIL methods.
- Quote parameters of remaining migration query.
- Track user when setting a version active.
- Fix menus randomly closing on refresh.
- Don't trigger the settings change flag on user language changes.
- Backport setting `CONVERTER_IMAGE_GENERATION_MAX_RETRIES`.
  This setting allows changing the image generation task maximum
  retry count. Celery's built in default value is 3, this setting
  increases that default to 7.

4.0.15 (2021-08-07)
===================
- Improve the document version export API endpoint.

  - Enable tracking the user and persisting the value for the events.
  - Change the view class form a custom mixin to be a subclass of
    `generics.ObjectActionAPIView` one.
  - Improve test to check for message creation after export.
  - Avoid returning an error when using the `GET` method for the view.

- Improve the `generics.ObjectActionAPIView` class.

  - Merge with `ActionAPIViewMixin`.
  - Add `action_response_status` for predetermined status codes.
  - Add message when the `.object_action` method is missing.

- Fix the view to mark all messages as read.
- Track the user when marking messages as read or unread.
- Fix action messages.

4.0.14 (2021-08-05)
===================
- Fix a regression in the document version page image cache maximum size
  setting callback.
- Fix converter layer priority exclusion for layers with a priority of 0.
  This fixes the preview layer priority when editing the redactions of pages
  that also contain transformations in other layers.

4.0.13 (2021-08-02)
===================
- Checkout test updates.

  - Silence debug output of tests.
  - Speed up tests using document stubs.

- Improve organization URL and host settings. Closes GitLab issues
  #966 and #1002. Thanks to None Given (@nastodon) and
  Bw (@bwakkie) for the reports.

  - Patch Django's HttpRequest object to override scheme
    and host.
  - Fix organization setting used to set the REST API URL
    base path.

- Track user for event when submitting a document version for OCR.
- Fix OCR version event texts.
- Update the document index list and document cabinet list links to require
  the same permission scheme as the views they reference.
- Add the document creation date time as a search field.

4.0.12 (2021-07-19)
===================
- Fix main menu active entry handling.
- Fix ID number in ``document_url`` attribute of the ``DocumentFile``
  and ``DocumentVersion`` serializers. Thanks to forum user @qra for the
  report. Topic 5794.
- Add API endpoint to display the list of valid transition options for a
  workflow instance. Thanks to forum user @qra for the report. Topic 5795.
- Add the workflow template content to the workflow instance API schema.
  Thanks to forum user @qra for the request. Topic 5795.
- Clarify purpose of project settings.
- Minor API serializer cleanups.
- Add explicit cabinet serializer read only fields.
- Fix multi scope search result initialization. Closes GitLab issue #1018.
  Thanks to Ryan Showalter (@ryanshow) for the report.
- Detect and report when a search scope does not specify a query.

4.0.11 (2021-07-06)
===================
- Update date time copy code from migration document:0063 to work with
  database that store time zone information and those that don't.
- Switch deployment instructions to use ``venv`` instead of ``virtualenv``.
- Add support for using local PIP cache to build Docker images.
- Add a Vagrant setup for testing. Integrates project
  https://gitlab.com/mayan-edms/mayan-edms-vagrant. Closes GitLab issue
  #937. Thanks to Max Kornyev (@mkornyev) for the report.
- Improve ``user_settings_folder`` variable creation. Works with
  ``MEDIA_ROOT`` paths with and without a trailing slash.
- The GitLab CI upgrade tests now update a test document to populate the
  older version install and trigger more migration code paths.
- Update all shell usage from ``bash`` to ``sh``. ``sh`` symlinks to ``dash``
  in the Docker image. This also expands the usability of the supervisor
  file for direct deployments in more operating systems. Closes GitLab
  issue #1013. Thanks to joh-ku (@joh-ku) for the report.
- Replace the ``wait.sh`` file with a Python alternative that can wait on
  network ports or PostgreSQL directly as a client.
- Upgrade ``supervisord`` from Debian buster version 3.3.5-1 to Debian
  bullseye version 4.2.2-2. This version uses Python3 and was the last
  dependency that required installing Python2 in the Docker image.
- Add the ``id`` field as sortable field in all the API that have ordering
  enabled.

4.0.10 (2021-07-02)
===================
- Simplify code block to delete OCR content of a document version.
- Make document version timestamp time zone aware before copying them over
  during migration.
- Split duplicates migration query into two separate queries to increase
  compatibility with database managers.
- Add support to the GitLab CI for local apt proxies.

4.0.9 (2021-06-29)
==================
- Improve scope search.

  - Support more than two source scopes per operator.
  - Support ``match_all`` logic per scope.
  - Support returning a single scope without using the operator output.
  - Disable search limits when multiple scopes are specified.
  - Add separate query decoding method.

- Increase the padding of the main menu panel anchors. Closes GitLab issue
  #1004. Thanks to Bw (@bwakkie) for the report.
- Rotate the main menu accordion indicator when opened or closed.
- Optimize jQuery usage of the $(this) object. Remove some unused jQuery
  code from the document card update methods.
- Add more uses of ``update_fields`` to ``.save()`` methods.
- Simplify logic using the document parser content update using
  ``update_or_create``.
- Raise document list errors on debug or testing.

4.0.8 (2021-06-23)
==================
- Update PIP to version 21.1.2.
- Use longer version of the Celery worker option.
- Make optional the `user_id` argument of
  `task_document_file_page_image_generate`.
- Another round of worker queue assignments tuning.
- Simplify the GPG temporary home preparation. A temporary directory context
  manager is now used that also guarantees that the temporary folder will be
  removed even on failures.
- Don't assume all signatures provide a ``date_time`` field.
- Optimize file and version page image API. Load the page object only once
  per request.
- Unify the supervisord templates. The direct deployment and the Docker image
  now use the same supervisord template.
- Email the active document version. Instead of emailing the latest updated
  document file, the document emailing with attachment will now export the
  active version and email that as an attachments. This mimics more closely
  the existing behavior of this feature before the document version were
  separated into versions and files.
- Update Django version 2.2.23 to 2.2.24.
- Improve Docker Compose installation and upgrade instructions.
- Fix the document type button not appearing. Update the cascade condition
  of the document type setup link to display when there are not document
  types created.
- Don't cache the missing items template to allow it to be removed when
  the missing items are fixed.
- Event testing improvements for several apps.
- The date and time of document version timestamps are now carried over
  during the upgrade from version 3.5.x to 4.0.x.
- Update the file metadata submit actions to keep track of the user and apply
  it to the events.
- Update the document parsing submit actions to keep track of the user and
  apply it to the events.
- Apply small optimization to ``MultipleObjectViewMixin``
  ``.get_object_list()`` method. The method now reuses the existing
  ``pk_list`` variable.
- Fixed an issue with the document metadata add and edit actions which
  prevented the user value to be ignored at the event commit.
- Convert the GitLab CI and Dockerfile into platform templates.
- Update Docker base image from Debian:10.8-slim to Debian:10.10-slim.
- Add config entry ``DEFAULT_USER_SETTINGS_MODULE``.
- Add serializer explicit read only fields.
- Optimize documents app saves with `update_fields`.

4.0.7 (2021-06-11)
==================
- Fix typo in the CELERY_MAX_TASKS_PER_CHILD_ARGUMENT environment
  variable.

4.0.6 (2021-06-10)
==================
- Fix celery argument names in supervisord template. Set correct attribute
  names max-tasks-per-child and max-memory-per-child when starting celery
  workers. Closes #998. Thanks to joh-ku (@joh-ku) for the report and patch.
- Use different environment when composing the child limits arguments.
  Update CELERY_MAX_MEMORY_PER_CHILD and CELERY_TASKS_MEMORY_PER_CHILD
  to use a separate argument variable, like CELERY_CONCURRENCY.

4.0.5 (2021-06-08)
==================
- Turn the release notes upgrade instructions into a partial template.
- Add support for Celery's max memory and tasks. Support
  ``--max-memory-per-child`` and ``--max-tasks-per-child`` using
  the environment variables ``MAYAN_WORKER_X_MAX_MEMORY_PER_CHILD``
  and ``MAYAN_WORKER_X_MAX_TASKS_PER_CHILD``.
- Add commented Docker compose database port entry.
- Support Gunicorn's ``--limit-request-line`` via the
  ``MAYAN_GUNICORN_LIMIT_REQUEST_LINE`` environment variable.
- Improve the Docker image environment variables chapter. Include missing
  variables and automate displaying the default values of several.
  Organize variables by topic.
- Exclude trashed documents from the workflow runtime proxy document count.
- Fix metadata form ``KeyError`` exception when required metadata is missing.
  Closes GitLab issue #997. Thanks to Raimar Sandner (@PiQuer) for the report
  and debug information.
- Document file and version page image updates:

  - Improve document version page base image cache invalidation on source
    image transformation updates.
  - Optimize transformation list generation by replacing several loops with
    list extensions.
  - Avoid using the source content transformations when calculating the
    document version transformation list hash. This cause duplicated document
    version page transformation in some cases. Closes GitLab issue #996.
    Thanks to Reinhard Ernst (@reinhardernst) for the report and debug
    information.
  - Improve document version page image API URL hash uniqueness generation.
    Ensure browsers do not use a cached document version page image when
    the transformations of the source object of the version are updated.

4.0.4 (2021-06-05)
==================
- Merge updates from version 3.5.10

  - Remove event decorator database transaction
    Solves workflows not being launched on document creation. Closes
    GitLab issue #976 and issue #990, thanks to users Megamorf (@megamorf),
    A F (@adzzzz) for the reports and debug information.

4.0.3 (2021-06-03)
==================
- Merge updates from version 3.5.9

  - Fix user model theme related field error after deleting a theme already
    assigned to a user. Closes GitLab issue #972. Thanks to Niklas Maurer
    (@nmaurer) for the report.
  - Add duplicate document tool tests.
  - Speed up some OCR view tests.
  - Add explicit Docker logout repository in CD/CI jobs.
  - Fix permission required for the document content error list link to match
    the permission required for the document parsed content error list view.
    GitLab issue #954. Thanks to Ilya Pavlov (@spirkaa) for the report.
  - Fix permission required for the OCR content delete link to match the
    permission required for the OCR content delete view. GitLab issue #954.
    Thanks to Ilya Pavlov (@spirkaa) for the report.

- Update dependency versions:

  - django-solo from version 1.1.3 to 1.1.5.
  - python-magic from version 0.4.15 to 0.4.22

- Makefile updates

  - Unify Docker test with staging targets.
  - Replace underscore in target names with hyphen for uniformity.
  - Add Redis Docker test targets.

- Lock manager updates

  - Rename get_instance() method to get_backend(). This method
    returns a class and not an instance.
  - Add management command tests.
  - Add optional _initialization method for backends.
  - Update the RedisLock backend to use a connection pool.

- Update Docker entrypoint template to support default worker
  concurrency values. Now correctly passes the default concurrency
  value of the D class worker.
- Updated REST API examples for version 4 of the API.

4.0.2 (2021-05-25)
==================
- Messaging app updates:

    - Add links to set messages as unread.
    - Automatically set messages as read upon accessing them. GitLab issue
      #981, thanks to Ilya Pavlov (@spirkaa) for the report.
    - Disable links to mark messages as read or unread based on the state of
      the message.

- Clarify Redis and Lock manager upgrade steps.
- Action dropdown template updates:

  - Move dropdown template partial to the navigation app.
  - Remove unused {{ link_extra_classes }}.
  - Remove obsolete dropdown HTML markup.

- Fix action menu disabled link appearance.
- Correct user_settings folder creation step. Closes GitLab issue #984.
  Thanks to Matthias Löblich (@startmat) for the report.
- Ensure the API authentication has completed before doing initial filtering.
  Fixes API views returning 404 errors when using token authentication.
- Minor source string fixes.
- Update Django REST framework from version 3.11.0 to 3.11.2.
- Update PIP from version 21.0.1 to 21.1.1.
- Update django-mptt from version 0.11.0 to 0.12.0.
- Add ordering to cabinets. Closes GitLab issue #986. Thanks to Hanno Zulla
  (@hzulla) for the report.

4.0.1 (2021-05-20)
==================
- Fix group and user setup link conditional disable not working as
  expected.
- Fix Docker environment variables documentation chapter regarding
  worker concurrency.
- Add troubleshooting section regarding document file access after upgrade
  to version 4.0.
- Allow migration of the settings ``DOCUMENTS_STORAGE_BACKEND`` and
  ``DOCUMENTS_STORAGE_BACKEND_ARGUMENTS`` for more situations.

4.0 (2021-05-19)
================
- Add document version page list reset.
- Add document version page delete.
- Add document version hash from content object.
- Improve file and version page max page calculation.
- Add version page navigation.
- Support document file deletion.
- Move document download code to document file.
- Add document file permissions.
- Move page count update to document file.
- Several renames for consistency. Use the major, minor, verb order
  for variable names in more places.
- Point document to latest document version. This removes the document page
  views and makes them aliases of the document version pages views.
- Add document version deletion.
- Add document file properties view.
- Remove page disabling/enabling.
- Add document version page model.
- Add caches, settings and handlers for the document version cache.
- Add document version page image API.
- Rename ``DocumentPage`` model to ``DocumentFilePage``.
- Invert the document and OCR migrations dependency. Makes the OCR migration
  dependent on the documents app migration. This allows disabling the OCR app.
- New event ignore and keep attribute options
- No results template for file list view.
- Fixed version page append
- Convert document model save method to use event decorator.
- Update file hooks to work when there is not previous file.
- Remove all remaining orientation support. Remove rotation test files.
- Add multi document version delete.
- Add a generic multi item delete view.
- Longer document file action texts.
- Document stub recalculation by file save and delete
- Better document version page remap
- Reorganize and split document model tests
- Add file upload mixin method.
- Unify the action dropdown instances into a new partial called
  ``appearance/partials/actions_dropdown.html``.
- Move the ``related`` menu from the "Actions" to the ``facet`` area.
- Add sources to their own menu.
- Add ``mode`` argument to SharedUploadedFile.
- Split document app model tests into separate modules.
- Split document app test mixins into separate modules.
- Fix the appearance of the automatically generated view titles.
- Add a new "Return" menu for secondary object views.
- Use the "Return" menu for the document version, document version page,
  document file, and document file page views.
- Remove the "File..." reference to the document file form fields as these
  are now obvious.
- Add more return links. From document version to version list, from
  document file to document file list, from document version page to
  document, from document file page to document.
- Add document version edit view. Allows editing the document version comment.
- Improve the return links with the chevron as the uniform secondary icon.
- Rename the document view, document version view and document file views to
  document preview, document file preview and document version preview.
- Enable more cabinets, checkouts, document comments, metadata, linking,
  mailer, mirroring, web links apps.
- Allow using staging folders for new document file uploads.
- Add conditional source link highlighting.
- Add document version create view and permission.
- Add validation and test for repeated document version page numbers.
- Improve page remap code and add annotated content object list support.
- Don't display the file upload link on the document file delete view.
- Update shared upload file to allow storing the original filename.
- Upload the new document file upload code path to conserve the original
  filename.
- Rename ``DeletedDocument`` to ``TrashedDocument``, same with the
  corresponding trashed fields and manager methods.
- Add document file download event.
- Update Dropzone from version 5.4.0 to 5.7.2.
- Rename all instances of ``icon_class`` to ``icon`` as only icon instances
  are used now in every app.
- Add icons to the mark notification as seen and mark all notification as
  seen links.
- Switch both view to mark notification as read to use the POST request
  via a confirmation view.
- Return the event type subscription list sorted by namespace label and event
  type label.
- Make the search fields more uniform and add missing ones.
- Add full label for search parent fields.
- Add events for the document type quick label model.
- Add dedicated API endpoints for the document type quick label model.
- Update the file cache partition purge view to be a generic view that can
  be called using the content type of an object. Adds a new file cache
  partition purge permission.
- Added ``ContentTypeTestCaseMixin``.
- Include ``EventTestCaseMixin`` as part of the base test case mixin.
- Rename usage of "recent document" to the more explicit "recently
  accessed document". This was done at the mode, view and API level.
  The recently accessed document API will now require the document view
  permission.
- Rename the document model ``date_added`` field to ``datetime_created`` to
  better reflect the purpose of the field.
- Add a ``RecentlyCreatedDocument`` proxy and associate the recent document
  columns to it.
- Move the recently created document query calculation to its own model
  manager.
- Add the recently created document API.
- Add favorite documents API.
- Rename the ``misc_models.py`` module to ``duplicated_document_models.py``.
- Split the ``document_api_views.py`` modules into ``document_api_views.py``
  and ``trashed_document_api_views.py``.
- Add date time field to the favorite documents models to ensure deterministic
  ordering when deleting the oldest favorites.
- Rename the setting ``DOCUMENTS_RECENT_ACCESS_COUNT`` to
  ``DOCUMENTS_RECENTLY_ACCESSED_COUNT``, and ``DOCUMENTS_RECENT_ADDED_COUNT``
  to ``DOCUMENTS_RECENTLY_CREATED_COUNT``. Config file migrations and
  migration tests were added. Environment and supervisor settings need to be
  manually updated.
- Document stubs without a label will now display their ID as the label.
  This allows documents without files or versions to be accessible via the
  user interface.
- Add the reusable ObjectActionAPIView API view. This is a view that can
  execute an action on an object from a queryset from a POST request.
- Improve proxy model menu link resolution. Proxy model don't need at least
  one bound link anymore to trigger resolution of all the parent model links.
  The inclusion logic is now reverse and defaults to exclusion. Menu need to
  be configured explicitly enable to proxy model link resolution using the new
  ``.add_proxy_inclusions(source)`` method.
- Move the duplicated documents code to its own app.
- Add duplication backend support to the duplicates app.
- Add duplicates app API.
- Add support for search model proxy registration.
- Remove the ``views`` arguments from the SourceColumn class. Use models
  proxies instead to customize the columns of a model based on the view
  displayed.
- Add document type change workflow action.
- Rename WizardStep to DocumentCreateWizardStep. This change better reflects
  its purpose and interface.
- Move DocumentCreateWizardStep to the sources.classes module.
- Add automatic loading support for the ``wizard_step`` modules. It is no
  longer necessary to import these modules inside the App's .ready() method.
- Update API endpoints to use explicit primary key URL keyword arguments.
- Split workflow models module into separate modules.
- Remove usage of Document.save(_user). The event_actor attribute is used
  instead.
- Convert the key creation and expiration fields to date and time fields.
- Add creation and download events for keys.
- Add event subscription for keys.
- Include time of document signatures. Closes GitLab issue #941. Thanks
  to forum user Tomek (@tkwoka) for the report and additional
  information.
- Add document signature tool to refresh the content of existing signatures
  when there are database or backend changes.
- Moved ``ObjectLinkWidget`` to the views app.
- Add global ACL list view.
- ``appearance_app_templates`` now passes the request to the templates being
  rendered.
- Remove the user impersonation fragment form the ``base.html`` template and
  moved it to its own viewport template.
- Enable subscribing to user impersonation events.
- Enable impersonation permission for individual users.
- Allow impersonating users from the user list view.
- Update jQuery from version 3.4.1 to 3.5.1.
- Move user language and timezone code from the `common` app to a new app
  called `locales`.
- Move common and smart settings app `base` template markup to their own
  apps via the `viewport` app template.
- Rename document comment model's `comment` field to `text`.
- Support sorting document comments by user or by date.
- Increase the size of the ``Lock`` lock manager model ``name`` field to a
  255 char field. Closes GitLab issue #939. Thanks to Will Wright
  (@fireatwill) for the report and investigation.
- Add example usage for the ``COMMON_EXTRA_APPS`` and
  ``COMMON_DISABLED_APPS``. Closes GitLab issue #929. Thanks to Francesco
  Musella (@francesco.musella-biztems) for the report.
- Reorganize mixins. Add a suffix to specify the purpose of the mixin and
  move them to different module when appropriate.
- Refactored the notification generation for efficiency, scalability and
  simplicity. Only users subscribed to events are queued for notifications.
  Content types of event targets and action objects is reused from the action
  model instead of gathering from inspection. Nested loop removed and lowered
  to a single loop.
- Optimize SourceColumn resolution. Support column exclusion for all object
  types. Ensure columns are not repeated when resolved even if they were
  defined multiple times. Improve docstring for the resolution logic in each
  level. Remove unused ``context`` parameter. Add SourceColumn tests.
- Support defining the default ``SearchModel``. This allows removing the hard
  coded search model name from the search template and allows third party
  apps to define their own default ``SearchModel``.
- Update MySQL Docker image from version 5.7 to 8.0. PostreSQL image from version
  10.14 to 10.15. Redis image from version 5.0 to 6.0.
- Move time delays from test and into its own test mixin. Remove MySQL test delays.
- Standardize a class for the widgets of the class ``SourceColumn`` named
  ``SourceColumnWidget``.
- The cabinet view permission is now required for a document, to be able to
  view which cabinets contain that document. This change mirrors the
  permission layout of the metadata and tag apps.
- File caching now uses the same lock for all file methods. This ensures that
  a cache file that is being deleted or purge is not open for reading and
  vice versa.
- A method decorator was added to the lock manager app to ease usage of the
  same lock workflow in methods of the same class.
- The error handling of the ``CachePartitionFile`` methods was improved.
  This ensures proper clean up of stray storage files on model file creation
  error. The model now avoids accessing the model file for clean up on model
  file creation error, which would raise a hard to understand and diagnose
  missing file entry error. The model now avoids updating cache size on
  either model or storage file creation error.
- Support disabling form help texts via ``form_hide_help_text``.
- Docker image tagging layout has been updated. Images are tagged by version
  and series. Series have the 's' prefix and versions have the 'v' prefix.
- Added API endpoints for the Assets model.
- Added cached image generation for assets.
- Added asset detail view with image preview.
- Added a detail view for the cache model.
- Added the ``image_url`` field to the Workflow template serializer.
- Added retry support for the workflow preview generation task.
- Updated the autoadmin app to use the login template ``login_content``
  template hook. This allows the autoadmin app to show login information
  without directly modifying the login template.
- Update tags app to improve user event tracking on view and API.
- Support deleting multiple document files.
- Track document file deletion event user in views.
- Rename ``setting_workflowimagecache_storage`` to
  ``setting_workflow_image_cache_storage_backend``.
- Support collapsing the options of the menus "list facet" and "object" when
  in list view mode. This behavior is controlled with the new settings:
  ``COMMON_COLLAPSE_LIST_MENU_LIST_FACET`` and
  ``COMMON_COLLAPSE_LIST_MENU_OBJECT``. Both default to ``False``.
- Added a check to the task manager app to ensure all defined tasks are
  properly configure in their respective ``queues.py`` modules.
- ACL apps updates: Add ACL deleted event, track action actor in API and
  views. Simply API views using REST API mixins. Update API views to return
  404 errors instead of 403, move global ACL list to the setup menu,
  model that are registered for ACLs are now also automatically register
  events in order to receive the ACL deleted event, improve tests and add more
  test cases.
- Update AddRemoveView to only call the underlying add or remove methods only
  if there are objects to act upon instead of calling the method with an
  empty queryset which would trigger unwanted events.
- Add ``ExternalContentTypeObjectAPIViewMixin`` to the REST API app. This
  mixin simplifies working with models that act upon another object via
  their Content Type, such as the ACLs.
- Update the ACL app to support multiple foreign object permission
  inheritance. Support for ``GenericForeignKey`` non default ``ct_field``,
  and ``fk_field`` was also added.
- Added support to export the global events list, object events list and
  user events list.
- Registering a model to receive events will cause it to have the object
  event view and object event subscription links bound too. This can
  be disabled with the `bind_links` argument. The default menu to bind the
  links is the "List facet". This can be changed via the ``menu`` argument.
- Change the format of the ``file_metadata_value_of`` helper. The driver
  and metadata entry are now separated by a double underscore instead of a
  single underscore. This allows supporting drivers and entries that might
  contain an underscore themselves.
- Add ``databases`` app to group data and models related code.
- Add class support for scoped searches. GitLab issue #875.
- Add sorting support to the API.
- Updated how the user interface column sorting works. The code was
  simplified by using a single query variable. The code was expanded
  to support multiple fields in the future. The URL query key used for
  column sorting was changed to match the API sorting.a
- Added the ``databases`` app. This app groups data and models related code.
- Added a patch for Django's ``Migration`` class to display time delta for
  each migration during development.
- Docker Compose updates:

    - Use profiles for extra containers.
    - Converted to use extensions to remove duplicated markup.
    - A new container was added to mount an index.
    - Added support for Traefik.
    - Added sample .env file.
    - Update required Docker Compose to version 1.28.

- Add a third document filename generator that used an UUID plus the original
  filename of the uploaded file. This generator has the advantage of producing
  unique filename while also preserving the original filename for reference.
- Add support for the "Reply To" field for sending documents via email and
  for the mailing workflow actions. Closes GitLab issue #864. Thanks to
  Kevin Pawsey (@kevinpawsey) for the request.
- Allow customization of the error condition when generating document images.
  This allows displaying more icons in addition to the generic document
  image error with additional contextual information and popup messages
  explaining the actual error condition.
- Add key attributes to the document signature serializers. Forum topic 5085.
  Thanks to forum user @qra for the request.
- Added key attributes to the document signature model as calculated
  properties.
- Move detached signature upload from the created endpoint to a
  new /uploaded endpoint.
- Added document signature events.
- Refactored the workflows app.

    - Rebalance permissions needed to transition a workflow instance.
      The workflow instance transition permission is now needed for
      the document and for either the transition or the workflow.
    - Add more tests including trashed document tests.
    - Split API tests into instance and template tests.
    - Add `workflow-instance-log-entry-detail` end point.
    - Add parent URL fields to serializers.
    - Allow passing extra data when transitioning a workflow via the API.
    - Limit state options to workflow when using the API. This matches
      the UI behavior.

- Renamed the AddRemove view ``main_object_method_add`` to
  ``main_object_method_add_name`` and ``main_object_method_remove`` to
  ``main_object_method_add_remove_name``.
- Add ``has_translations`` flag to MayanAppConfig to indicate if the app
  should have its translation files processed or ignored. Defaults to
  ``True``.
- Dependency version upgrades:

  - coverage from 5.1 to 5.5.
  - Django to 2.2.23.
  - django-debug-toolbar to 3.2.
  - django-extensions to 3.1.2.
  - django-rosetta to 0.9.4.
  - django-silk to 4.1.0.
  - flake8 to 3.9.0.
  - ipython to 7.22.0.
  - pycounty to 20.7.3.
  - requests to 2.25.1.
  - Sphinx to 3.5.4.
  - sh to 1.14.1.
  - sphinx-autobuild to 2021.3.14.
  - sphinx-sitemap to 2.2.0.
  - sphinxcontrib-spelling to 7.1.0.
  - tornado to 6.1.
  - tox from 3.14.6 to 3.23.1.
  - transifex-client to 0.14.2.
  - twine to 3.4.1.
  - wheel to 0.36.2.

- Fix sub workflow launch state action.
- Convert the workflow instance creation to a background task.
- File caching app updates

  - Add cache partition purge event.
  - Use new event decorator.
  - Use related object as the cache partition purge event action object.
  - Allow cache prune to retry on LockError.
  - Add maximum cache prune failure counter.
  - Remove possible cache file lock name collision.

- Add locking to the duplicated document scan code to workaround race
  condition in Django bug #19544 when adding duplicated documents via
  the many to many field ``.add()`` method.
- Remove the default queue. All tasks must now be explicitly assigned to an
  app defined queue.
- Update file cache to use and LRU style eviction logic.
- Only prune caches during startup if their maximum size changed.
- Add detection of excessive cache pruning when cache size is too small for
  the workload.
- Detect and avoid duplicated queue names.
- Add a fourth class of worker.
- Re-balance queues.
- Rename workers from ``fast``, ``medium``, and ``slow`` to ``A`` (fast),
  ``B`` (new workers), ``C`` (medium), ``D`` (slow).
- Add support for passing custom nice level to the workers when using the
  Docker image ``run_worker`` command. The value is passed via the
  ``MAYAN_WORKER_NICE_LEVEL`` environment variable. This variable defaults to
  ``0``.
- Avoid adding a transformation to a layer for which it was
  not registered.
- Add LayerError exception.
- Fix redaction ACL support.
- Add support for typecasting the values used to filter the ACL object
  inherited fields.
- Rename the ``mayan_settings`` directory, which is used to allow custom
  setting modules, to the more intuitive ``user_settings``.
