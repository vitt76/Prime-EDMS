#!/bin/bash
docker run -d \
  --name prime-edms_app_1 \
  --network prime-edms_default \
  -p 80:8000 \
  -p 443:8443 \
  -e MAYAN_COMMON_EXTRA_APPS="['mayan.apps.converter_pipeline_extension']" \
  -e MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.postgresql','NAME':'mayan','PASSWORD':'mayandbpass','USER':'mayan','HOST':'prime-edms_postgresql_1'}}" \
  -e MAYAN_CELERY_BROKER_URL="amqp://mayan:mayanrabbitpass@prime-edms_rabbitmq_1:5672/mayan" \
  -e MAYAN_CELERY_RESULT_BACKEND="redis://:mayanredispassword@prime-edms_redis_1:6379/1" \
  -e MAYAN_LOCK_MANAGER_BACKEND="mayan.apps.lock_manager.backends.redis_lock.RedisLock" \
  -e MAYAN_LOCK_MANAGER_BACKEND_ARGUMENTS="{'redis_url':'redis://:mayanredispassword@prime-edms_redis_1:6379/2'}" \
  --env-file app.env \
  --volume mayan_data:/var/lib/mayan \
  --volume $(pwd)/config.yml:/opt/mayan-edms/config.yml \
  prime-edms_app
