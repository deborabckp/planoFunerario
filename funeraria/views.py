from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from django.utils.dateparse import parse_date
import csv
from datetime import datetime, timedelta

from .models import (
    FuncionarioFuneraria, ClienteFuneraria, DependenteFuneraria,
    PlanoFuneraria, PagamentoFuneraria, ServicoPrestadoFuneraria,
    FunerariaStatus, FunerariaTipos, DependenteStatus
)
from .serializers import (
    LoginSerializer, FuncionarioFunerariaSerializer,
    ClienteFunerariaSerializer, DependenteFunerariaSerializer,
    PlanoFunerariaSerializer, PagamentoFunerariaSerializer,
    ServicoPrestadoFunerariaSerializer, FunerariaStatusSerializer,
    FunerariaTiposSerializer, DependenteStatusSerializer,
    ClienteDetalhadoSerializer, PlanoDetalhadoSerializer
)


class AuthViewSet(viewsets.ViewSet):
    """ViewSet para autenticação"""
    permission_classes = []
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login de funcionários"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.get_full_name(),
                    'email': user.email
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout de funcionários"""
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout realizado com sucesso'})
        except Exception:
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)


class FuncionarioFunerariaViewSet(viewsets.ModelViewSet):
    """ViewSet para funcionários da funerária"""
    queryset = FuncionarioFuneraria.objects.all()
    serializer_class = FuncionarioFunerariaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'data_nascimento']
    search_fields = ['username', 'first_name', 'last_name', 'cpf', 'email']
    ordering_fields = ['date_joined', 'username', 'first_name']
    ordering = ['-date_joined']


class FunerariaStatusViewSet(viewsets.ModelViewSet):
    """ViewSet para status da funerária"""
    queryset = FunerariaStatus.objects.all()
    serializer_class = FunerariaStatusSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['status', 'descricao']
    ordering = ['status']


class DependenteStatusViewSet(viewsets.ModelViewSet):
    """ViewSet para status de dependentes"""
    queryset = DependenteStatus.objects.all()
    serializer_class = DependenteStatusSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['status', 'descricao']
    ordering = ['status']


class FunerariaTiposViewSet(viewsets.ModelViewSet):
    """ViewSet para tipos de serviços"""
    queryset = FunerariaTipos.objects.all()
    serializer_class = FunerariaTiposSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['descricao']
    ordering = ['descricao']


class PlanoFunerariaViewSet(viewsets.ModelViewSet):
    """ViewSet para planos funerários"""
    queryset = PlanoFuneraria.objects.select_related(
        'plano_status', 'funcionario_criacao', 'funcionario_atualizacao'
    ).prefetch_related('pagamentos', 'servicos')
    serializer_class = PlanoFunerariaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo_renovacao', 'plano_status', 'funcionario_criacao']
    search_fields = ['cobertura']
    ordering_fields = ['valor_mensal', 'data_fim', 'created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(
            funcionario_criacao=self.request.user,
            funcionario_atualizacao=self.request.user
        )
    
    def perform_update(self, serializer):
        serializer.save(funcionario_atualizacao=self.request.user)
    
    @action(detail=True)
    def detalhado(self, request, pk=None):
        """Retorna plano com detalhes de pagamentos e serviços"""
        plano = self.get_object()
        plano_data = PlanoDetalhadoSerializer(plano).data
        
        # Calcular total arrecadado
        total = plano.pagamentos.aggregate(total=Sum('valor_pago'))['total'] or 0
        plano_data['total_arrecadado'] = total
        
        return Response(plano_data)
    
    @action(detail=False)
    def relatorio_financeiro(self, request):
        """Relatório financeiro dos planos"""
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')
        
        queryset = self.get_queryset()
        
        if data_inicio:
            queryset = queryset.filter(created_at__gte=parse_date(data_inicio))
        if data_fim:
            queryset = queryset.filter(created_at__lte=parse_date(data_fim))
        
        relatorio = []
        for plano in queryset:
            total_arrecadado = plano.pagamentos.aggregate(
                total=Sum('valor_pago')
            )['total'] or 0
            
            relatorio.append({
                'plano_id': plano.id,
                'tipo_renovacao': plano.tipo_renovacao,
                'valor_mensal': plano.valor_mensal,
                'total_arrecadado': total_arrecadado,
                'total_pagamentos': plano.pagamentos.count(),
                'total_servicos': plano.servicos.count()
            })
        
        return Response(relatorio)


class ClienteFunerariaViewSet(viewsets.ModelViewSet):
    """ViewSet para clientes da funerária"""
    queryset = ClienteFuneraria.objects.select_related(
        'cliente_status', 'funcionario_cadastro', 'funcionario_atualizacao'
    ).prefetch_related('dependentes', 'servicos')
    serializer_class = ClienteFunerariaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['cliente_status', 'funcionario_cadastro', 'data_nascimento']
    search_fields = ['nome', 'cpf', 'email', 'telefone']
    ordering_fields = ['nome', 'data_nascimento', 'created_at']
    ordering = ['nome']
    
    def perform_create(self, serializer):
        serializer.save(
            funcionario_cadastro=self.request.user,
            funcionario_atualizacao=self.request.user
        )
    
    def perform_update(self, serializer):
        serializer.save(funcionario_atualizacao=self.request.user)
    
    @action(detail=True)
    def detalhado(self, request, pk=None):
        """Retorna cliente com dependentes e serviços"""
        cliente = self.get_object()
        return Response(ClienteDetalhadoSerializer(cliente).data)
    
    @action(detail=False, methods=['get'])
    def buscar_cpf(self, request):
        """Busca cliente por CPF"""
        cpf = request.query_params.get('cpf')
        if not cpf:
            return Response({'error': 'CPF é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cliente = ClienteFuneraria.objects.get(cpf=cpf)
            return Response(ClienteDetalhadoSerializer(cliente).data)
        except ClienteFuneraria.DoesNotExist:
            return Response({'error': 'Cliente não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False)
    def exportar_csv(self, request):
        """Exporta clientes em CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="clientes.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Nome', 'CPF', 'Data Nascimento', 'Telefone', 
            'Email', 'Status', 'Data Cadastro'
        ])
        
        for cliente in self.get_queryset():
            writer.writerow([
                cliente.id, cliente.nome, cliente.cpf, cliente.data_nascimento,
                cliente.telefone, cliente.email, cliente.cliente_status.status,
                cliente.created_at.strftime('%d/%m/%Y')
            ])
        
        return response


class DependenteFunerariaViewSet(viewsets.ModelViewSet):
    """ViewSet para dependentes dos clientes"""
    queryset = DependenteFuneraria.objects.select_related(
        'cliente', 'dependente_status', 'funcionario_criacao', 'funcionario_atualizacao'
    )
    serializer_class = DependenteFunerariaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['cliente', 'dependente_status', 'genero', 'funcionario_criacao']
    search_fields = ['nome', 'cpf']
    ordering_fields = ['nome', 'data_nascimento', 'created_at']
    ordering = ['nome']
    
    def perform_create(self, serializer):
        serializer.save(
            funcionario_criacao=self.request.user,
            funcionario_atualizacao=self.request.user
        )
    
    def perform_update(self, serializer):
        serializer.save(funcionario_atualizacao=self.request.user)
    
    @action(detail=False, methods=['get'])
    def por_cliente(self, request):
        """Lista dependentes por cliente"""
        cliente_id = request.query_params.get('cliente_id')
        if not cliente_id:
            return Response({'error': 'cliente_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        dependentes = self.get_queryset().filter(cliente_id=cliente_id)
        serializer = self.get_serializer(dependentes, many=True)
        return Response(serializer.data)


class PagamentoFunerariaViewSet(viewsets.ModelViewSet):
    """ViewSet para pagamentos dos planos"""
    queryset = PagamentoFuneraria.objects.select_related(
        'plano_funeraria', 'status_pagamento'
    )
    serializer_class = PagamentoFunerariaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['plano_funeraria', 'status_pagamento', 'forma_pagamento']
    search_fields = ['valor_pago']
    ordering_fields = ['data_hora_pagto', 'valor_pago', 'created_at']
    ordering = ['-data_hora_pagto']
    
    @action(detail=False)
    def historico_plano(self, request):
        """Histórico de pagamentos por plano"""
        plano_id = request.query_params.get('plano_id')
        if not plano_id:
            return Response({'error': 'plano_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        pagamentos = self.get_queryset().filter(plano_funeraria_id=plano_id)
        serializer = self.get_serializer(pagamentos, many=True)
        
        # Calcular totais
        total_pago = pagamentos.aggregate(total=Sum('valor_pago'))['total'] or 0
        
        return Response({
            'pagamentos': serializer.data,
            'total_pago': total_pago,
            'quantidade_pagamentos': pagamentos.count()
        })
    
    @action(detail=False)
    def relatorio_periodo(self, request):
        """Relatório de pagamentos por período"""
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')
        
        queryset = self.get_queryset()
        
        if data_inicio:
            queryset = queryset.filter(data_hora_pagto__gte=parse_date(data_inicio))
        if data_fim:
            queryset = queryset.filter(data_hora_pagto__lte=parse_date(data_fim))
        
        # Agrupar por forma de pagamento
        formas_pagamento = queryset.values('forma_pagamento').annotate(
            total=Sum('valor_pago'),
            quantidade=Count('id')
        ).order_by('-total')
        
        total_geral = queryset.aggregate(total=Sum('valor_pago'))['total'] or 0
        
        return Response({
            'formas_pagamento': formas_pagamento,
            'total_geral': total_geral,
            'periodo': {
                'data_inicio': data_inicio,
                'data_fim': data_fim
            }
        })


class ServicoPrestadoFunerariaViewSet(viewsets.ModelViewSet):
    """ViewSet para serviços prestados"""
    queryset = ServicoPrestadoFuneraria.objects.select_related(
        'cliente', 'plano', 'tipo', 'funcionario_criacao', 'funcionario_atualizacao'
    )
    serializer_class = ServicoPrestadoFunerariaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['cliente', 'plano', 'tipo', 'funcionario_criacao']
    search_fields = ['observacoes']
    ordering_fields = ['data_hora_servico', 'created_at']
    ordering = ['-data_hora_servico']
    
    def perform_create(self, serializer):
        serializer.save(
            funcionario_criacao=self.request.user,
            funcionario_atualizacao=self.request.user
        )
    
    def perform_update(self, serializer):
        serializer.save(funcionario_atualizacao=self.request.user)
    
    @action(detail=False)
    def por_cliente(self, request):
        """Serviços prestados por cliente"""
        cliente_id = request.query_params.get('cliente_id')
        if not cliente_id:
            return Response({'error': 'cliente_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        servicos = self.get_queryset().filter(cliente_id=cliente_id)
        serializer = self.get_serializer(servicos, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def relatorio_tipos(self, request):
        """Relatório de serviços por tipo"""
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')
        
        queryset = self.get_queryset()
        
        if data_inicio:
            queryset = queryset.filter(data_hora_servico__gte=parse_date(data_inicio))
        if data_fim:
            queryset = queryset.filter(data_hora_servico__lte=parse_date(data_fim))
        
        # Agrupar por tipo de serviço
        tipos_servico = queryset.values(
            'tipo__id', 'tipo__descricao'
        ).annotate(
            quantidade=Count('id')
        ).order_by('-quantidade')
        
        return Response({
            'tipos_servico': tipos_servico,
            'total_servicos': queryset.count(),
            'periodo': {
                'data_inicio': data_inicio,
                'data_fim': data_fim
            }
        })


class DashboardViewSet(viewsets.ViewSet):
    """ViewSet para dashboard com estatísticas gerais"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False)
    def estatisticas(self, request):
        """Estatísticas gerais do sistema"""
        hoje = datetime.now().date()
        inicio_mes = hoje.replace(day=1)
        
        # Contadores gerais
        total_clientes = ClienteFuneraria.objects.count()
        total_dependentes = DependenteFuneraria.objects.count()
        total_planos = PlanoFuneraria.objects.count()
        
        # Serviços do mês
        servicos_mes = ServicoPrestadoFuneraria.objects.filter(
            data_hora_servico__gte=inicio_mes
        ).count()
        
        # Pagamentos do mês
        pagamentos_mes = PagamentoFuneraria.objects.filter(
            data_hora_pagto__gte=inicio_mes
        )
        valor_arrecadado_mes = pagamentos_mes.aggregate(
            total=Sum('valor_pago')
        )['total'] or 0
        
        # Clientes por status
        clientes_por_status = ClienteFuneraria.objects.values(
            'cliente_status__status'
        ).annotate(quantidade=Count('id'))
        
        return Response({
            'totais': {
                'clientes': total_clientes,
                'dependentes': total_dependentes,
                'planos': total_planos,
                'servicos_mes': servicos_mes
            },
            'financeiro': {
                'valor_arrecadado_mes': valor_arrecadado_mes,
                'quantidade_pagamentos_mes': pagamentos_mes.count()
            },
            'clientes_por_status': list(clientes_por_status)
        })
        
    