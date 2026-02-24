"""
Example CRUD API views.

This is a reference implementation showing the standard patterns used in this
template. Copy, rename, and adapt for your project-specific resources.

Patterns demonstrated:
- DRF APIView with response helpers
- HMAC/JWT auth via @jwt_required decorator
- Per-endpoint throttling
- Paginated list responses
- Cache-aside reads
- OpenAPI schema annotations
"""
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema

from ...utils import success_response, error_response, paginated_response, pagination_params, get_cache, set_cache
from ...throttling import ContentListingRateThrottle, DataModificationRateThrottle
from ...apis.auth.decorator import jwt_required


@extend_schema(tags=["Example"])
@method_decorator(csrf_exempt, name="dispatch")
class ExampleListView(APIView):
    """
    GET  /api/v1/example/        — list all items (paginated, cached)
    POST /api/v1/example/        — create a new item (jwt required)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        throttle = ContentListingRateThrottle()
        throttle.allow_request(request, self)

        page, page_size = pagination_params(request)

        cache_key = f"example_list:{page}:{page_size}"
        cached = get_cache(cache_key)
        if cached is not None:
            return success_response("Items retrieved (cached)", data=cached)

        # TODO: Replace with your queryset
        # items = MyModel.objects.filter(is_active=True).order_by("-created_at")
        # total = items.count()
        # page_items = items[(page - 1) * page_size : page * page_size]
        # serializer = MySerializer(page_items, many=True)
        # data = serializer.data
        total = 0
        data = []

        result = paginated_response(data, total=total, page=page, page_size=page_size)
        set_cache(cache_key, result, timeout=60 * 5)
        return success_response("Items retrieved", data=result)

    @jwt_required
    def post(self, request):
        throttle = DataModificationRateThrottle()
        throttle.allow_request(request, self)

        # TODO: Validate input and create your model instance
        # serializer = MySerializer(data=request.data)
        # if not serializer.is_valid():
        #     return error_response("Validation failed", status=400, errors=serializer.errors)
        # instance = serializer.save()
        # return success_response("Item created", data=MySerializer(instance).data, status=201)

        return success_response("Item created (stub)", status=201)


@extend_schema(tags=["Example"])
@method_decorator(csrf_exempt, name="dispatch")
class ExampleDetailView(APIView):
    """
    GET    /api/v1/example/<pk>/  — retrieve a single item
    PUT    /api/v1/example/<pk>/  — update an item (jwt required)
    DELETE /api/v1/example/<pk>/  — delete an item (jwt required)
    """
    permission_classes = [AllowAny]

    def get(self, request, pk):
        throttle = ContentListingRateThrottle()
        throttle.allow_request(request, self)

        # TODO: Fetch your model instance
        # instance = get_object_or_404(MyModel, pk=pk, is_active=True)
        # return success_response("Item retrieved", data=MySerializer(instance).data)

        return success_response("Item retrieved (stub)", data={"id": pk})

    @jwt_required
    def put(self, request, pk):
        throttle = DataModificationRateThrottle()
        throttle.allow_request(request, self)

        # TODO: Update your model instance
        # instance = get_object_or_404(MyModel, pk=pk)
        # serializer = MySerializer(instance, data=request.data, partial=True)
        # if not serializer.is_valid():
        #     return error_response("Validation failed", status=400, errors=serializer.errors)
        # serializer.save()
        # return success_response("Item updated", data=serializer.data)

        return success_response("Item updated (stub)")

    @jwt_required
    def delete(self, request, pk):
        # TODO: Soft-delete or hard-delete your model instance
        # instance = get_object_or_404(MyModel, pk=pk)
        # instance.deleted_at = timezone.now()
        # instance.save()
        # return success_response("Item deleted")

        return success_response("Item deleted (stub)")
