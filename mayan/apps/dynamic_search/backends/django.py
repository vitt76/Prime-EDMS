import hashlib
import json
import logging

from django.core.cache import cache
from django.db.models import Q
from django.utils.encoding import force_text

from ..classes import SearchBackend, SearchModel
from ..literals import QUERY_PARAMETER_ANY_FIELD

from .literals import (
    QUERY_OPERATION_AND, QUERY_OPERATION_OR, TERM_NEGATION_CHARACTER,
    TERM_OPERATION_OR, TERM_OPERATIONS, TERM_QUOTES, TERM_SPACE_CHARACTER
)
logger = logging.getLogger(name=__name__)

# Priority fields for simple search optimization
# These fields are searched first for parameter 'q' to improve performance
SIMPLE_SEARCH_PRIORITY_FIELDS = [
    'label',  # Document label - most common search
    'files__filename',  # Filename - very common search
    'description',  # Description - common search
    'uuid',  # UUID - sometimes searched
    # DAM-enhanced fields
    'ai_analysis__ai_description',
    'ai_analysis__ai_tags',
    'ai_analysis__categories',
    'ai_analysis__people',
    'ai_analysis__locations',
    'ai_analysis__alt_text',
    'ai_analysis__ai_provider'
]


class DjangoSearchBackend(SearchBackend):
    def _get_status(self):
        result = []

        for search_model in SearchModel.all():
            queryset = search_model.get_queryset()

            result.append(
                '{}: {}'.format(
                    search_model.label, queryset.count()
                )
            )

        return '\n'.join(result)
    
    def cleanup_query(self, query, search_model):
        """
        Оптимизированная версия cleanup_query для Django backend.
        Для простого поиска (параметр 'q') копирует значение только в приоритетные поля,
        а не во все 36+ полей, что значительно ускоряет поиск.
        """
        # Проверяем, является ли это простым поиском
        is_simple_search = QUERY_PARAMETER_ANY_FIELD in query and len(query) == 1
        
        if is_simple_search:
            # Для простого поиска копируем только в приоритетные поля
            value = query[QUERY_PARAMETER_ANY_FIELD]
            if value is not None:
                value_stripped = value.strip() if isinstance(value, str) else str(value)
                if value_stripped:
                    # Используем только приоритетные поля вместо всех
                    clean_query = {key: value_stripped for key in SIMPLE_SEARCH_PRIORITY_FIELDS}
                    return clean_query
        
        # Для расширенного поиска используем стандартную логику
        return super().cleanup_query(query=query, search_model=search_model)

    def _search(
        self, query, search_model, user, global_and_search=False,
        ignore_limit=False
    ):
        # Кеширование результатов поиска для оптимизации производительности
        # Кешируем только для простых запросов (не для расширенного поиска)
        cache_enabled = True
        cache_key = None
        
        # Создаем ключ кеша только для простых запросов
        if cache_enabled and 'q' in query and len(query) == 1:
            cache_key = self._get_cache_key(query, search_model, user, global_and_search)
            
            # Пытаемся получить из кеша
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug('Search cache HIT: %s', cache_key[:50] if cache_key else 'N/A')
                # Возвращаем queryset с закешированными ID
                base_queryset = search_model.get_queryset()
                if hasattr(base_queryset.model, 'document_type'):
                    base_queryset = base_queryset.select_related('document_type')
                return base_queryset.filter(pk__in=cached_result)
        
        logger.debug('Search cache MISS: %s', cache_key[:50] if cache_key else 'N/A')
        
        search_query = self.get_search_query(
            global_and_search=global_and_search, query=query,
            search_model=search_model
        )

        # Log search query for debugging
        logger.info(
            'DjangoSearchBackend search: query=%s, django_query=%s',
            query, search_query.django_query
        )

        # Get base queryset using the search model's manager
        base_queryset = search_model.get_queryset()
        
        # Optimize queryset for search performance
        # Use select_related for ForeignKey relationships to avoid N+1 queries
        # Use prefetch_related for reverse ForeignKey/ManyToMany relationships
        if hasattr(base_queryset.model, 'document_type'):
            base_queryset = base_queryset.select_related('document_type')
        
        # Apply search filter
        if search_query.django_query:
            # Оптимизация: сначала получаем только ID через values_list
            # Это быстрее, чем distinct() на полных объектах
            result_ids = base_queryset.filter(
                search_query.django_query
            ).values_list('id', flat=True).distinct()
            
            # Затем загружаем объекты по ID
            queryset = base_queryset.filter(pk__in=result_ids)
        else:
            # If no query, return empty queryset
            queryset = base_queryset.none()
        
        # Кешируем результаты (только ID для экономии памяти)
        if cache_enabled and cache_key:
            # Ограничиваем до 1000 результатов для кеширования
            result_ids_list = list(queryset.values_list('pk', flat=True)[:1000])
            # Кешируем на 5 минут (300 секунд)
            cache.set(cache_key, result_ids_list, 300)
            logger.debug('Search results cached: %d IDs', len(result_ids_list))
        
        # Log results count for debugging (only in debug mode to avoid performance impact)
        if logger.isEnabledFor(logging.DEBUG):
            result_count = queryset.count()
            logger.debug(
                'DjangoSearchBackend search results: %d documents found',
                result_count
            )
        
        # Additional debug logging for empty results (only in debug mode)
        if logger.isEnabledFor(logging.DEBUG) and query:
            result_count = queryset.count() if not hasattr(queryset, '_result_cache') else len(queryset)
            if result_count == 0:
                # Get the search term from query
                search_term = query.get('q', '') or str(query)
                logger.debug(
                    'DjangoSearchBackend search returned 0 results for query: %s, '
                    'django_query: %s',
                    search_term, search_query.django_query
                )
            
            # Additional debugging: test direct ORM search (only in debug mode)
            if logger.isEnabledFor(logging.DEBUG) and 'q' in query:
                test_term = query['q'].strip()
                if test_term:
                    # Test direct search on files__filename
                    direct_results = base_queryset.filter(
                        files__filename__icontains=test_term
                    ).distinct().count()
                    logger.debug(
                        'Direct ORM search test (files__filename__icontains="%s"): %d results',
                        test_term, direct_results
                    )
                    
                    # Test search on label
                    label_results = base_queryset.filter(
                        label__icontains=test_term
                    ).distinct().count()
                    logger.debug(
                        'Direct ORM search test (label__icontains="%s"): %d results',
                        test_term, label_results
                    )

        return queryset
    
    def _get_cache_key(self, query, search_model, user, global_and_search):
        """Генерирует уникальный ключ кеша для запроса."""
        # Сортируем query для консистентности
        query_str = json.dumps(sorted(query.items()), sort_keys=True)
        user_id = user.pk if user and hasattr(user, 'pk') else 'anonymous'
        key_data = f"{search_model.get_full_name()}:{user_id}:{global_and_search}:{query_str}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"search:{key_hash}"

    def get_search_query(
        self, query, search_model, global_and_search=False
    ):
        return SearchQuery(
            global_and_search=global_and_search, query=query,
            search_model=search_model
        )


class FieldQuery:
    def __init__(self, search_field, search_term_collection):
        query_operation = QUERY_OPERATION_AND
        self.django_query = None
        # Ленивая инициализация parts - только для отладки (__str__)
        self._parts = None
        self._search_field = search_field
        self._search_term_collection = search_term_collection

        for term in search_term_collection.terms:
            if term.is_meta:
                # It is a meta term, modifies the query operation
                # and is not searched
                if term.string == TERM_OPERATION_OR:
                    query_operation = QUERY_OPERATION_OR
            else:
                # For Django backend, transformation functions are used for field values
                # during indexing (Whoosh/Elasticsearch), not for search terms.
                # For JSON fields like ai_tags, we search directly without transformation
                # because Django ORM handles JSON field lookups natively.
                # Only apply transformation if it's a simple transformation like UUID formatting
                # (which transforms the search term, not the field value)
                if search_field.transformation_function:
                    # Check if this is a term transformation (like UUID) or field value transformation
                    # Term transformations take a string and return a string (e.g., UUID formatting)
                    # Field value transformations take a value (list/dict) and return a string (e.g., JSON arrays)
                    # For Django backend, we only apply term transformations, not field value transformations
                    try:
                        # Try calling with the term string - if it works, it's a term transformation
                        result = search_field.transformation_function(term.string)
                        # If result is a string and different from input, it's likely a term transformation
                        if isinstance(result, str):
                            term_string = result
                        else:
                            # Field value transformation - skip it for Django backend
                            term_string = term.string
                    except (TypeError, AttributeError):
                        # Field value transformation - skip it for Django backend
                        term_string = term.string
                else:
                    term_string = term.string

                # For related fields (like files__filename), ensure we search through valid related objects
                # Django ORM will automatically handle the relationship lookup
                field_path = search_field.field
                
                # Оптимизация для JSON полей: используем нативные PostgreSQL JSON lookup'ы
                # Это намного быстрее, чем transformation функции
                is_json_array_field = (
                    'ai_tags' in field_path or 
                    'categories' in field_path or 
                    'people' in field_path or 
                    'locations' in field_path or
                    'dominant_colors' in field_path
                )
                
                if is_json_array_field:
                    # Для JSON массивов используем contains для поиска элемента в массиве
                    # PostgreSQL JSONB содержит оператор @> работает быстрее
                    # Используем __contains с массивом для поиска в JSON массиве
                    try:
                        # Пытаемся использовать нативный JSON contains lookup
                        # Для PostgreSQL это будет использовать оператор @>
                        q_object = Q(
                            **{f'{field_path}__contains': [term_string]}
                        )
                    except Exception:
                        # Fallback на icontains, если contains не работает
                        q_object = Q(
                            **{f'{field_path}__icontains': term_string}
                        )
                else:
                    # Для обычных полей используем icontains
                    lookup = 'icontains'
                    q_object = Q(
                        **{f'{field_path}__{lookup}': term_string}
                    )
                if term.negated:
                    q_object = ~q_object

                if self.django_query is None:
                    self.django_query = q_object
                else:
                    if query_operation == QUERY_OPERATION_AND:
                        self.django_query &= q_object
                    else:
                        self.django_query |= q_object

    @property
    def parts(self):
        """Ленивая инициализация parts для обратной совместимости."""
        if self._parts is None:
            self._parts = []
            for term in self._search_term_collection.terms:
                if not term.is_meta:
                    self._parts.append(force_text(s=self._search_field.label))
                    self._parts.append(force_text(s=term))
                else:
                    self._parts.append(term.string)
        return self._parts

    def __str__(self):
        if self._parts is None:
            # Инициализируем parts только если нужно
            _ = self.parts
        return ' '.join(self.parts)


class SearchQuery:
    def __init__(self, query, search_model, global_and_search=False):
        self.django_query = None
        # Ленивая инициализация text - только для отладки
        self._text = None
        
        # Кешируем результат get_search_fields() - избегаем множественных вызовов
        all_search_fields = search_model.get_search_fields()
        
        # Debug logging for query processing (только если включен debug)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                'SearchQuery.__init__: query=%s, search_model=%s, fields_count=%d',
                query, search_model.get_full_name(), len(all_search_fields)
            )

        # For simple search (parameter 'q'), optimize by searching only in key fields
        # This significantly improves performance by avoiding huge OR queries across all 36+ fields
        is_simple_search = 'q' in query and len(query) == 1
        
        if is_simple_search:
            # Get search fields in priority order - используем кешированный список
            search_fields = []
            # Создаем словарь для быстрого поиска полей
            field_dict = {sf.field: sf for sf in all_search_fields}
            for field_name in SIMPLE_SEARCH_PRIORITY_FIELDS:
                if field_name in field_dict:
                    search_fields.append(field_dict[field_name])
        else:
            # For advanced search, filter empty fields BEFORE processing
            # Обрабатываем только заполненные поля из запроса
            filled_fields = {
                k: v for k, v in query.items()
                if k != '_match_all' and v and (
                    isinstance(v, str) and v.strip() or not isinstance(v, str)
                )
            }
            
            if filled_fields:
                # Создаем словарь для быстрого поиска полей
                field_dict = {sf.field: sf for sf in all_search_fields}
                search_fields = [
                    field_dict[k] for k in filled_fields.keys()
                    if k in field_dict
                ]
            else:
                # Если нет заполненных полей, возвращаем пустой queryset
                search_fields = []

        # Собираем все Q-объекты в список для более эффективного объединения
        q_objects = []
        search_value = None
        
        # Для простого поиска получаем значение один раз
        if is_simple_search and 'q' in query:
            search_value = query.get('q', '').strip()

        for search_field in search_fields:
            # Для простого поиска используем предварительно полученное значение
            if is_simple_search and search_value is not None:
                field_value = search_value
            else:
                field_value = query.get(search_field.field, '').strip()

            # Skip empty fields to avoid unnecessary processing
            if not field_value:
                continue

            # Debug logging for each field (только если включен debug)
            if logger.isEnabledFor(logging.DEBUG) and field_value:
                logger.debug(
                    'SearchQuery processing field: %s = "%s"',
                    search_field.field, field_value
                )

            # Оптимизация: для простых случаев (без кавычек, OR, отрицаний) используем быстрый путь
            search_term_collection = SearchTermCollection(text=field_value)

            field_query = FieldQuery(
                search_field=search_field,
                search_term_collection=search_term_collection
            )

            if field_query.django_query:
                q_objects.append(field_query.django_query)
                
                # Создаем text только если нужно логирование
                if logger.isEnabledFor(logging.DEBUG):
                    if self._text is None:
                        self._text = []
                    self._text.append('({})'.format(force_text(s=field_query)))
                    if global_and_search:
                        self._text.append('AND')
                    else:
                        self._text.append('OR')

        # Объединяем все Q-объекты за один раз - более эффективно
        if q_objects:
            if global_and_search:
                # Для AND объединяем через &=
                self.django_query = q_objects[0]
                for q_obj in q_objects[1:]:
                    self.django_query &= q_obj
            else:
                # Для OR объединяем через |=
                self.django_query = q_objects[0]
                for q_obj in q_objects[1:]:
                    self.django_query |= q_obj
        else:
            # If no query was created, return empty query (will match nothing)
            self.django_query = Q()
        
        # Debug logging for empty queries (только если включен debug)
        if logger.isEnabledFor(logging.DEBUG) and query:
            # Check if django_query is effectively empty
            is_empty_query = (
                self.django_query is None or 
                (hasattr(self.django_query, 'children') and len(self.django_query.children) == 0 and 
                 not hasattr(self.django_query, 'connector'))
            )
            
            if is_empty_query:
                # Check if query has non-empty values
                has_non_empty = any(
                    v and (isinstance(v, str) and v.strip() or not isinstance(v, str))
                    for v in query.values()
                )
                
                if has_non_empty:
                    logger.warning(
                        'SearchQuery created empty query for non-empty input: query=%s, '
                        'search_model=%s, fields_count=%d, search_fields=%s',
                        query, search_model.get_full_name(), len(all_search_fields),
                        [f.field for f in all_search_fields][:10]
                    )

    @property
    def text(self):
        """Ленивая инициализация text для обратной совместимости."""
        if self._text is None:
            return []
        return self._text

    def __str__(self):
        if self._text:
            return ' '.join(self._text[:-1])
        return ''


class SearchTerm:
    def __init__(self, negated, string, is_meta):
        self.negated = negated
        self.string = string
        self.is_meta = is_meta

    def __str__(self):
        if self.is_meta:
            return ''
        else:
            return '{}contains "{}"'.format(
                'does not ' if self.negated else '', self.string
            )


class SearchTermCollection:
    def __init__(self, text):
        """
        Takes a text string and returns a list of dictionaries.
        Each dictionary has two key "negated" and "string"

        String 'a "b c" d "e" \'f g\' h -i -"j k" l -\'m n\' o OR p'

        Results in:
        [
            {'negated': False, 'string': 'a'}, {'negated': False, 'string': 'b c'},
            {'negated': False, 'string': 'd'}, {'negated': False, 'string': 'e'},
            {'negated': False, 'string': 'f g'}, {'negated': False, 'string': 'h'},
            {'negated': True, 'string': 'i'}, {'negated': True, 'string': 'j k'},
            {'negated': False, 'string': 'l'}, {'negated': True, 'string': 'm n'},
            {'negated': False, 'string': 'o'}, {'negated': False, 'string': 'OR'},
            {'negated': False, 'string': 'p'}
        ]
        
        Оптимизация: для простых случаев (без кавычек, OR, отрицаний) 
        используем быстрый путь через split().
        """
        self.terms = []
        
        # Быстрый путь для простых случаев (без кавычек, OR, отрицаний)
        # Проверяем, есть ли сложные конструкции
        has_quotes = any(q in text for q in TERM_QUOTES)
        has_or = TERM_OPERATION_OR in text
        has_negation = TERM_NEGATION_CHARACTER in text
        
        if not (has_quotes or has_or or has_negation):
            # Простой случай - используем быстрый путь
            words = text.split()
            for word in words:
                if word:
                    self.terms.append(
                        SearchTerm(
                            is_meta=False, negated=False,
                            string=word
                        )
                    )
            return
        
        # Сложный случай - используем полный парсинг
        inside_quotes = False
        negated = False
        term_letters = []

        for letter in text:
            if letter in TERM_QUOTES:
                if inside_quotes:
                    if term_letters:
                        term_string = ''.join(term_letters)
                        negated = False
                        if term_string.startswith(TERM_NEGATION_CHARACTER):
                            term_string = term_string[1:]
                            negated = True

                        self.terms.append(
                            SearchTerm(
                                is_meta=False, negated=negated,
                                string=term_string
                            )
                        )
                        negated = False
                        term_letters = []

                inside_quotes = not inside_quotes
            else:
                if not inside_quotes and letter == TERM_SPACE_CHARACTER:
                    if term_letters:
                        term_string = ''.join(term_letters)
                        if term_string in TERM_OPERATIONS:
                            is_meta = True
                        else:
                            is_meta = False

                        if is_meta:
                            negated = False
                        else:
                            negated = False
                            if term_string.startswith(TERM_NEGATION_CHARACTER):
                                term_string = term_string[1:]
                                negated = True

                        self.terms.append(
                            SearchTerm(
                                is_meta=is_meta, negated=negated,
                                string=term_string
                            )
                        )
                        negated = False
                        term_letters = []
                else:
                    term_letters.append(letter)

        if term_letters:
            term_string = ''.join(term_letters)
            negated = False
            if term_string.startswith(TERM_NEGATION_CHARACTER):
                term_string = term_string[1:]
                negated = True

            self.terms.append(
                SearchTerm(
                    is_meta=False, negated=negated,
                    string=term_string
                )
            )

    def __str__(self):
        result = []
        for term in self.terms:
            if term.is_meta:
                result.append(term.string)
            else:
                result.append(force_text(s=term))

        return ' '.join(result)
