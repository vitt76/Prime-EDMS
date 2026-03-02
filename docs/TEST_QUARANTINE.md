# Test Quarantine Log

Тесты, временно отключённые (test.skip) до рефактора или исправления окружения. Не скипать тесты безопасности и tenant isolation.

| Файл | Тест | Причина | Sprint для фикса |
|------|------|---------|------------------|
| useIntersectionObserver.spec.ts | создание observer / custom options | composable вызывается вне компонента — onMounted не срабатывает | Sprint 2 |
| VirtualScroller.spec.ts | 2 минорных теста (клавиатура и edge case с нулевой высотой) | jsdom не поддерживает нативную прокрутку scrollTop на 100% | Sprint 3 |
| AdminReportsPage.spec.ts | все | reportsStore.usageMetrics — структура store изменилась | Sprint 2 cleanup |
| MetadataPanel.spec.ts | несколько | разметка/селекторы устарели | Sprint 2 |
| BulkTagModal.spec.ts | мокинг Pinia и vm Wrapper | тест обращается к vm модалки до рендера содержимого | Sprint 3 |
| GalleryView.accessibility.spec.ts | axe toHaveNoViolations | конфликты импортов Chai matcher | Sprint 3 |
| retry.spec.ts | с таймерами / fake timers | задержки и onRetry не совпадают с fake timers | Sprint 3 |
