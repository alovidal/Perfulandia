from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from functools import wraps

def rol_requerido(roles_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            
            if request.user.rol not in roles_permitidos:
                raise PermissionDenied("No tienes permisos para acceder a esta página.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

class RolRequeridoMixin(LoginRequiredMixin):
    roles_permitidos = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if self.roles_permitidos and request.user.rol not in self.roles_permitidos:
            raise PermissionDenied("No tienes permisos para acceder a esta página.")
        
        return super().dispatch(request, *args, **kwargs)
