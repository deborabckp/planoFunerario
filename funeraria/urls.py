from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AuthViewSet, FuncionarioFunerariaViewSet, ClienteFunerariaViewSet,
    DependenteFunerariaViewSet, PlanoFunerariaViewSet, PagamentoFunerariaViewSet,
    ServicoPrestadoFunerariaViewSet, FunerariaStatusViewSet, FunerariaTiposViewSet,
    DependenteStatusViewSet, DashboardViewSet
)

# Configuração do router para as APIs
router = DefaultRouter()
router.register(r'funcionarios', FuncionarioFunerariaViewSet)
router.register(r'clientes', ClienteFunerariaViewSet)
router.register(r'dependentes', DependenteFunerariaViewSet)
router.register(r'planos', PlanoFunerariaViewSet)
router.register(r'pagamentos', PagamentoFunerariaViewSet)
router.register(r'servicos', ServicoPrestadoFunerariaViewSet)
router.register(r'status', FunerariaStatusViewSet)
router.register(r'tipos-servicos', FunerariaTiposViewSet)
router.register(r'dependente-status', DependenteStatusViewSet)
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    # Endpoints das APIs
    path('', include(router.urls)),
    
    # JWT Token endpoints
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]