"""
Простой скрипт для проверки работы функций валидации размера файлов.
Можно запустить напрямую для быстрой проверки.
"""
import os
import sys
import django

# Настройка Django окружения
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.base')
django.setup()

from mayan.apps.dam.utils import get_max_file_size_for_mime_type, format_file_size


def test_format_file_size():
    """Тест форматирования размеров."""
    print("Testing format_file_size()...")
    
    test_cases = [
        (512, "512 B"),
        (1024, "1.0 KB"),
        (2048, "2.0 KB"),
        (1024 * 1024, "1.0 MB"),
        (20 * 1024 * 1024, "20.0 MB"),
        (15.5 * 1024 * 1024, "15.5 MB"),
    ]
    
    for size_bytes, expected in test_cases:
        result = format_file_size(int(size_bytes))
        status = "✓" if result == expected else "✗"
        print(f"  {status} {size_bytes} bytes -> {result} (expected: {expected})")
        if result != expected:
            print(f"    ERROR: Expected {expected}, got {result}")
            return False
    
    print("  All format_file_size tests passed!\n")
    return True


def test_get_max_file_size():
    """Тест получения лимитов по MIME типам."""
    print("Testing get_max_file_size_for_mime_type()...")
    
    test_cases = [
        ('image/jpeg', 20 * 1024 * 1024),
        ('image/png', 20 * 1024 * 1024),
        ('image/tiff', 50 * 1024 * 1024),
        ('image/x-canon-cr2', 50 * 1024 * 1024),
        ('application/pdf', 30 * 1024 * 1024),
        ('application/msword', 15 * 1024 * 1024),
        ('text/plain', 15 * 1024 * 1024),
        ('video/mp4', 500 * 1024 * 1024),
        ('audio/mpeg', 100 * 1024 * 1024),
        ('application/unknown', 15 * 1024 * 1024),
        ('', 15 * 1024 * 1024),
    ]
    
    for mime_type, expected in test_cases:
        result = get_max_file_size_for_mime_type(mime_type)
        status = "✓" if result == expected else "✗"
        expected_mb = expected / (1024 * 1024)
        result_mb = result / (1024 * 1024)
        print(f"  {status} {mime_type or '(empty)'} -> {result_mb} MB (expected: {expected_mb} MB)")
        if result != expected:
            print(f"    ERROR: Expected {expected_mb} MB, got {result_mb} MB")
            return False
    
    print("  All get_max_file_size_for_mime_type tests passed!\n")
    return True


def test_integration():
    """Интеграционный тест: проверка размера файла."""
    print("Testing file size validation logic...")
    
    # Симуляция проверки файла
    test_files = [
        {'mime_type': 'image/jpeg', 'size': 10 * 1024 * 1024, 'should_pass': True},
        {'mime_type': 'image/jpeg', 'size': 25 * 1024 * 1024, 'should_pass': False},
        {'mime_type': 'application/pdf', 'size': 25 * 1024 * 1024, 'should_pass': True},
        {'mime_type': 'application/pdf', 'size': 35 * 1024 * 1024, 'should_pass': False},
        {'mime_type': 'image/tiff', 'size': 45 * 1024 * 1024, 'should_pass': True},
        {'mime_type': 'image/tiff', 'size': 55 * 1024 * 1024, 'should_pass': False},
    ]
    
    for test_file in test_files:
        mime_type = test_file['mime_type']
        size = test_file['size']
        should_pass = test_file['should_pass']
        
        max_size = get_max_file_size_for_mime_type(mime_type)
        passes = size <= max_size
        
        status = "✓" if passes == should_pass else "✗"
        size_str = format_file_size(size)
        max_size_str = format_file_size(max_size)
        
        print(f"  {status} {mime_type} ({size_str}) - limit: {max_size_str} - {'PASS' if passes else 'FAIL'}")
        
        if passes != should_pass:
            print(f"    ERROR: Expected {'PASS' if should_pass else 'FAIL'}, got {'PASS' if passes else 'FAIL'}")
            return False
    
    print("  All integration tests passed!\n")
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("File Size Validation Tests")
    print("=" * 60)
    print()
    
    results = []
    results.append(test_format_file_size())
    results.append(test_get_max_file_size())
    results.append(test_integration())
    
    print("=" * 60)
    if all(results):
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)

