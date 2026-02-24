from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiExample

from api.models import UserProfile, Device
from .serializers import DeviceRegistrationSerializer, DeviceSerializer
from ...utils import success_response, error_response
from ...throttling import DataModificationRateThrottle


@extend_schema(
    tags=['Device Registration'],
    summary='Register device',
    description='Register a new device and create associated user profile. This is the first endpoint to call when app launches.',
    request=DeviceRegistrationSerializer,
    responses={200: DeviceSerializer, 201: DeviceSerializer},
    examples=[
        OpenApiExample(
            'Register Device',
            value={
                'device_id': 'unique_device_identifier',
                'device_type': 'iOS',
                'app_version': '1.0.0',
                'region': 'US'
            },
            request_only=True
        )
    ]
)
@method_decorator(csrf_exempt, name='dispatch')
class RegisterDeviceView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [DataModificationRateThrottle]  # Rate limit: 30 requests per minute
    """
    Register a new device and create associated user profile.
    
    Expected payload:
    {
        "device_id": "unique_device_identifier",
        "device_type": "iOS/Android/Web",
        "app_version": "1.0.0",
        "region": "US"
    }
    
    Returns:
    {
        "success": true,
        "message": "Device registered successfully",
        "data": {...}
    }
    """
    
    def post(self, request):
        data = request.data
        
        # Validate input data
        serializer = DeviceRegistrationSerializer(data=data)
        if not serializer.is_valid():
            return error_response('Validation failed', status=400, errors=serializer.errors)
        
        validated_data = serializer.validated_data
        device_id = validated_data['device_id']
        
        # Check if device already exists
        existing_device = Device.objects.select_related('profile').filter(device_id=device_id).first()
        if existing_device:
            device_serializer = DeviceSerializer(existing_device)
            return success_response('Device already registered', data=device_serializer.data)
        
        # Step 1: Create UserProfile with blank data
        user_profile = UserProfile.objects.create()
        
        # Step 2: Create Device and bind to UserProfile
        device = Device.objects.create(
            device_id=device_id,
            device_type=validated_data.get('device_type', ''),
            app_version=validated_data.get('app_version', ''),
            region=validated_data.get('region', ''),
            profile=user_profile
        )
        
        device_serializer = DeviceSerializer(device)
        return success_response('Device registered successfully', data=device_serializer.data, status=201)
