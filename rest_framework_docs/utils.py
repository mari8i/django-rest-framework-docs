from rest_framework.views import APIView
import types
from django.utils import six

def api_view(http_method_names=None):

    """
    Decorator that converts a function-based view into an APIView subclass.
    Takes a list of allowed methods for the view as an argument.

    Copied and modified from the DRF original code. If you can re-use
    the original decorator instead of copying the whole code, please be
    nice and contribute, I have no time at the moment.

    The only difference is:

    WrappedAPIView.serializer_class = getattr(func, 'serializer_class', None)

    That I've added in order to be able to use the drf_serializer_class

    Using this, you can do the following and still get the "fields" documentation:

    @api_view(['GET'])
    @permission_classes((AllowAny, ))
    @drf_serializer_class(serializers.AuthUserSerializer)
    def dostuff(request, params):
       return Response()

    """


    http_method_names = ['GET'] if (http_method_names is None) else http_method_names

    def decorator(func):

        WrappedAPIView = type(
            six.PY3 and 'WrappedAPIView' or b'WrappedAPIView',
            (APIView,),
            {'__doc__': func.__doc__}
        )

        # Note, the above allows us to set the docstring.
        # It is the equivalent of:
        #
        #     class WrappedAPIView(APIView):
        #         pass
        #     WrappedAPIView.__doc__ = func.doc    <--- Not possible to do this

        # api_view applied without (method_names)
        assert not(isinstance(http_method_names, types.FunctionType)), \
            '@api_view missing list of allowed HTTP methods'

        # api_view applied with eg. string instead of list of strings
        assert isinstance(http_method_names, (list, tuple)), \
            '@api_view expected a list of strings, received %s' % type(http_method_names).__name__

        allowed_methods = set(http_method_names) | set(('options',))
        WrappedAPIView.http_method_names = [method.lower() for method in allowed_methods]

        def handler(self, *args, **kwargs):
            return func(*args, **kwargs)

        for method in http_method_names:
            setattr(WrappedAPIView, method.lower(), handler)

        WrappedAPIView.__name__ = func.__name__

        WrappedAPIView.renderer_classes = getattr(func, 'renderer_classes',
                                                  APIView.renderer_classes)

        WrappedAPIView.parser_classes = getattr(func, 'parser_classes',
                                                APIView.parser_classes)

        WrappedAPIView.authentication_classes = getattr(func, 'authentication_classes',
                                                        APIView.authentication_classes)

        WrappedAPIView.throttle_classes = getattr(func, 'throttle_classes',
                                                  APIView.throttle_classes)

        WrappedAPIView.permission_classes = getattr(func, 'permission_classes',
                                                    APIView.permission_classes)

        WrappedAPIView.serializer_class = getattr(func, 'serializer_class', None)

        return WrappedAPIView.as_view()

    return decorator


# For this to work, use the above api_view instead of the drf one.
def drf_serializer_class(serializer_class):
    def decorator(func):
        func.serializer_class = serializer_class
        return func
    return decorator
