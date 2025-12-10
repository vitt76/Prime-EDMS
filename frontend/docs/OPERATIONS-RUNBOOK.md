# 🛠️ Operations Runbook
## Руководство по эксплуатации DAM Frontend

**Версия:** 1.0  
**Дата:** 2025-01-27  
**Для:** DevOps, On-Call Engineers

---

## 📑 Содержание

1. [Deployment Procedures](#deployment-procedures)
2. [Rollback Procedures](#rollback-procedures)
3. [Monitoring & Alerts](#monitoring--alerts)
4. [Common Issues & Solutions](#common-issues--solutions)
5. [Emergency Contacts](#emergency-contacts)
6. [Maintenance Windows](#maintenance-windows)

---

## 🚀 Deployment Procedures

### Pre-Deployment Checklist

- [ ] Code reviewed and approved
- [ ] Tests passing (unit, integration, E2E)
- [ ] Security scan passed
- [ ] Performance tests passed
- [ ] Database migrations tested
- [ ] Backup created
- [ ] Rollback plan ready

### Deployment Steps

**1. Staging Deployment**

```bash
# 1. Checkout release branch
git checkout release/v1.0.0

# 2. Build frontend
cd frontend
pnpm install
pnpm build

# 3. Run tests
pnpm test
pnpm test:e2e

# 4. Deploy to staging
# (Follow your deployment process)
```

**2. Staging Verification**

- [ ] Smoke tests pass
- [ ] All features work
- [ ] Performance acceptable
- [ ] No errors in logs

**3. Production Deployment**

```bash
# 1. Tag release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 2. Deploy to production
# (Follow your deployment process)

# 3. Verify deployment
curl https://dam.local/health
```

**4. Post-Deployment Verification**

- [ ] Health check passes
- [ ] Smoke tests pass
- [ ] Monitoring shows healthy
- [ ] No errors in logs
- [ ] User feedback positive

---

## ⏪ Rollback Procedures

### Automatic Rollback

**Triggers:**
- Error rate > 5%
- Response time > 2s
- Health check fails
- Critical errors detected

**Process:**
1. Automatic rollback triggered
2. Previous version restored
3. Team notified
4. Investigation started

### Manual Rollback

**Steps:**

```bash
# 1. Identify current version
git log --oneline -1

# 2. Identify previous stable version
git log --oneline -10

# 3. Rollback to previous version
git checkout <previous-version-tag>

# 4. Rebuild and deploy
pnpm build
# Deploy previous version

# 5. Verify rollback
curl https://dam.local/health
```

**Database Rollback:**

```bash
# If migrations need rollback
python manage.py migrate <app> <previous-migration>

# Or restore from backup
pg_restore -d dam_db backup.dump
```

**Time Target:** < 15 minutes

---

## 📊 Monitoring & Alerts

### Key Metrics

**Application Metrics:**
- Error rate (target: < 0.1%)
- Response time p95 (target: < 500ms)
- Request rate
- Active users

**Infrastructure Metrics:**
- CPU usage (alert: > 80%)
- Memory usage (alert: > 80%)
- Disk usage (alert: > 85%)
- Network traffic

**Business Metrics:**
- Upload success rate
- Search success rate
- User satisfaction

### Alert Configuration

**P0 - Critical (Immediate Response):**
- System down
- Error rate > 5%
- Database connection lost
- **Response Time:** < 15 minutes

**P1 - High (Urgent):**
- Error rate > 1%
- Response time > 2s
- High memory usage
- **Response Time:** < 1 hour

**P2 - Medium:**
- Error rate > 0.5%
- Performance degradation
- **Response Time:** < 4 hours

**P3 - Low:**
- Minor issues
- **Response Time:** < 24 hours

### Monitoring Tools

**Sentry (Error Tracking):**
- URL: https://sentry.io/dam-project
- Alerts: Email, Slack, PagerDuty

**DataDog (Metrics):**
- URL: https://app.datadoghq.com/dam
- Dashboards: Performance, Infrastructure, Business

**Custom Monitoring:**
- Health check endpoint: `/health`
- Metrics endpoint: `/metrics`

---

## 🔧 Common Issues & Solutions

### Issue 1: High Error Rate

**Symptoms:**
- Error rate > 1%
- Users reporting issues
- Alerts firing

**Diagnosis:**
```bash
# Check Sentry for errors
# Check application logs
tail -f /var/log/dam/app.log | grep ERROR

# Check database
psql -d dam_db -c "SELECT * FROM error_log ORDER BY timestamp DESC LIMIT 10;"
```

**Solutions:**
1. **API errors:**
   - Check backend health
   - Check API rate limits
   - Check database connections

2. **Frontend errors:**
   - Check browser console
   - Check CDN status
   - Check build integrity

3. **Database errors:**
   - Check connection pool
   - Check query performance
   - Check disk space

**Escalation:**
- If error rate > 5%: Immediate rollback
- If persists > 1 hour: Escalate to team lead

---

### Issue 2: Slow Response Times

**Symptoms:**
- Response time > 1s
- Users complaining
- Timeout errors

**Diagnosis:**
```bash
# Check API response times
curl -w "@curl-format.txt" https://dam.local/api/v4/dam/assets/

# Check database queries
# Use Django Debug Toolbar or similar

# Check CDN performance
# Check network latency
```

**Solutions:**
1. **API slow:**
   - Check database query performance
   - Check cache hit rate
   - Check external API calls
   - Scale up if needed

2. **Frontend slow:**
   - Check bundle size
   - Check CDN cache
   - Check image optimization
   - Check lazy loading

3. **Database slow:**
   - Check slow queries
   - Add indexes if needed
   - Optimize queries
   - Scale database if needed

---

### Issue 3: High Memory Usage

**Symptoms:**
- Memory usage > 80%
- Application slow
- OOM errors

**Diagnosis:**
```bash
# Check memory usage
free -h
ps aux | grep dam

# Check for memory leaks
# Use profiling tools
```

**Solutions:**
1. **Memory leak:**
   - Restart application
   - Investigate leak
   - Fix in next release

2. **High load:**
   - Scale horizontally
   - Optimize memory usage
   - Add more resources

---

### Issue 4: Database Connection Issues

**Symptoms:**
- Connection errors
- Timeout errors
- High connection count

**Diagnosis:**
```bash
# Check database connections
psql -d dam_db -c "SELECT count(*) FROM pg_stat_activity;"

# Check connection pool
# Check database logs
```

**Solutions:**
1. **Connection pool exhausted:**
   - Increase pool size
   - Check for connection leaks
   - Restart application

2. **Database down:**
   - Check database health
   - Restart database if needed
   - Failover to replica

---

### Issue 5: CDN/Cache Issues

**Symptoms:**
- Slow asset loading
- 404 errors for assets
- Cache not updating

**Diagnosis:**
```bash
# Check CDN status
curl -I https://cdn.dam.local/asset.jpg

# Check cache headers
curl -I https://dam.local/ | grep -i cache

# Check CDN logs
```

**Solutions:**
1. **Cache not updating:**
   - Purge CDN cache
   - Check cache headers
   - Update cache strategy

2. **CDN down:**
   - Failover to origin
   - Check CDN provider status
   - Contact CDN support

---

## 📞 Emergency Contacts

### On-Call Rotation

**Week 1:**
- Primary: [Name] - [Phone] - [Email]
- Secondary: [Name] - [Phone] - [Email]

**Week 2:**
- Primary: [Name] - [Phone] - [Email]
- Secondary: [Name] - [Phone] - [Email]

### Escalation Path

**Level 1: On-Call Engineer**
- Response: < 15 minutes
- Can resolve: P1-P3 issues

**Level 2: Team Lead**
- Response: < 1 hour
- Escalate: P0 issues, complex P1

**Level 3: Engineering Manager**
- Response: < 2 hours
- Escalate: System-wide issues

**Level 4: CTO/CDTO**
- Response: < 4 hours
- Escalate: Critical business impact

### Communication Channels

**Slack:**
- #dam-oncall - On-call channel
- #dam-incidents - Incident tracking
- #dam-alerts - Alert notifications

**PagerDuty:**
- Integration configured
- Escalation policies set

**Email:**
- oncall@dam.local - On-call email
- incidents@dam.local - Incident reports

---

## 🔄 Maintenance Windows

### Scheduled Maintenance

**Regular Maintenance:**
- **Frequency:** Weekly
- **Day:** Sunday
- **Time:** 02:00-04:00 UTC
- **Duration:** 2 hours
- **Notification:** 48 hours before

**Planned Updates:**
- **Frequency:** Monthly
- **Day:** First Sunday
- **Time:** 02:00-06:00 UTC
- **Duration:** 4 hours
- **Notification:** 1 week before

### Maintenance Checklist

**Before Maintenance:**
- [ ] Users notified
- [ ] Maintenance window scheduled
- [ ] Backup created
- [ ] Rollback plan ready
- [ ] Team on standby

**During Maintenance:**
- [ ] System in maintenance mode
- [ ] Updates applied
- [ ] Tests run
- [ ] Monitoring active

**After Maintenance:**
- [ ] System verified
- [ ] Users notified
- [ ] Post-maintenance report

---

## 📋 Health Check Endpoints

### Application Health

```bash
# Health check
curl https://dam.local/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-27T10:00:00Z"
}
```

### API Health

```bash
# API health
curl https://dam.local/api/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected",
  "version": "1.0.0"
}
```

### Metrics Endpoint

```bash
# Metrics (Prometheus format)
curl https://dam.local/metrics
```

---

## 🔍 Troubleshooting Commands

### Application Logs

```bash
# View recent logs
tail -f /var/log/dam/app.log

# Search for errors
grep ERROR /var/log/dam/app.log | tail -20

# Search for specific user
grep "user_id:123" /var/log/dam/app.log
```

### Database Queries

```bash
# Check active connections
psql -d dam_db -c "SELECT count(*) FROM pg_stat_activity;"

# Check slow queries
psql -d dam_db -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Check table sizes
psql -d dam_db -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

### Cache Status

```bash
# Check Redis cache
redis-cli INFO stats

# Check cache keys
redis-cli KEYS "dam:*" | head -20

# Clear cache (if needed)
redis-cli FLUSHDB
```

---

## 📊 Performance Tuning

### Frontend Optimization

**If performance degrades:**
1. Check bundle size
2. Check image optimization
3. Check lazy loading
4. Check CDN cache hit rate
5. Check API response times

### Backend Optimization

**If API slow:**
1. Check database query performance
2. Check cache hit rate
3. Check connection pool
4. Check external API calls
5. Scale horizontally if needed

---

**Документ создан:** 2025-01-27  
**Версия:** 1.0  
**Статус:** ✅ Ready for Operations

















