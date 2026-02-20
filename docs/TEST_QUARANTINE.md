# Test Quarantine Log

Тесты, временно отключённые (test.skip) до рефактора или исправления окружения. Не скипать тесты безопасности и tenant isolation.

| Файл | Тест | Причина | Sprint для фикса |
|------|------|---------|------------------|
| useIntersectionObserver.spec.ts | создание observer / custom options | composable вызывается вне компонента — onMounted не срабатывает | Sprint 2 |
| VirtualScroller.spec.ts | части тестов по числам (visible range, buffer) | привязка к внутренним размерам/реализации | Sprint 2 |
| AdminReportsPage.spec.ts | все | reportsStore.usageMetrics — структура store изменилась | Sprint 2 cleanup |
| MetadataPanel.spec.ts | несколько | разметка/селекторы устарели | Sprint 2 |
| ChartComponent.spec.ts | updates chart when data changes | vi.mock Chart.js + getContext в тесте | Sprint 2 |
