from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123'); print('Superuser created')
