"""
Health check endpoint for monitoring system status.

Checks database connectivity, cache availability, and overall system health.
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
import time


@extend_schema(
    tags=['Monitoring'],
    summary='Health check endpoint',
    description='Check system health including database, cache, and service availability. No authentication required.',
    auth=[],
    responses={
        200: inline_serializer(
            name='HealthCheckResponse',
            fields={
                'status': serializers.CharField(),
                'timestamp': serializers.DateTimeField(),
                'checks': serializers.DictField(),
            }
        )
    }
)
@method_decorator(csrf_exempt, name='dispatch')
class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring.
    
    Returns:
    - status: "healthy" or "unhealthy"
    - timestamp: Current server time
    - checks: Individual component health status
    
    No authentication required for monitoring systems.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'checks': {}
        }
        
        # Check database connectivity
        db_healthy = self._check_database()
        health_status['checks']['database'] = {
            'status': 'healthy' if db_healthy else 'unhealthy',
            'response_time_ms': None
        }
        
        # Check cache connectivity
        cache_healthy, cache_time = self._check_cache()
        health_status['checks']['cache'] = {
            'status': 'healthy' if cache_healthy else 'unhealthy',
            'response_time_ms': cache_time
        }
        
        # Overall health status
        if not db_healthy or not cache_healthy:
            health_status['status'] = 'unhealthy'
            return JsonResponse(health_status, status=503)
        
        return JsonResponse(health_status, status=200)
    
    def _check_database(self):
        """Check if database is accessible."""
        try:
            start = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True
        except Exception as e:
            print(f"Database health check failed: {e}")
            return False
    
    def _check_cache(self):
        """Check if cache (Redis) is accessible."""
        try:
            start = time.time()
            cache.set('health_check', 'ok', 10)
            result = cache.get('health_check')
            end = time.time()
            response_time = round((end - start) * 1000, 2)
            return result == 'ok', response_time
        except Exception as e:
            print(f"Cache health check failed: {e}")
            return False, None


@extend_schema(
    tags=['Monitoring'],
    summary='Readiness check endpoint',
    description='Check if the application is ready to accept requests. Returns 200 if ready, 503 if not.',
    auth=[],
    responses={
        200: inline_serializer(
            name='ReadinessCheckResponse',
            fields={
                'status': serializers.CharField(),
                'ready': serializers.BooleanField(),
            }
        )
    }
)
@method_decorator(csrf_exempt, name='dispatch')
class ReadinessCheckView(APIView):
    """
    Readiness check endpoint for Kubernetes/load balancers.
    
    Returns 200 if application is ready to serve traffic.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Check critical components
        db_ready = self._check_database()
        
        if db_ready:
            return JsonResponse({
                'status': 'ready',
                'ready': True
            }, status=200)
        else:
            return JsonResponse({
                'status': 'not_ready',
                'ready': False
            }, status=503)
    
    def _check_database(self):
        """Quick database check."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except:
            return False


@extend_schema(
    tags=['Monitoring'],
    summary='Liveness check endpoint',
    description='Check if the application process is alive. Always returns 200 if the process is running.',
    auth=[],
    responses={
        200: inline_serializer(
            name='LivenessCheckResponse',
            fields={
                'status': serializers.CharField(),
                'alive': serializers.BooleanField(),
            }
        )
    }
)
@method_decorator(csrf_exempt, name='dispatch')
class LivenessCheckView(APIView):
    """
    Liveness check endpoint for Kubernetes.
    
    Returns 200 as long as the process is running.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return JsonResponse({
            'status': 'alive',
            'alive': True
        }, status=200)

