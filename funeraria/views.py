from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from django.utils import timezone
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
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout realizado com sucesso'})
        except Exception:
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)


class FuncionarioFunerariaViewSet(viewsets.ModelViewSet):
    queryset = FuncionarioFuneraria.objects.all()
    serializer_class = FuncionarioFunerariaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'data_nascimento']
    search_fields = ['username', 'first_name', 'last_name', 'cpf', 'email']
    ordering_fields = ['date_joined', 'username', 'first_name']
    ordering = ['-date_joined']


class FunerariaStatusViewSet(viewsets.ModelViewSet):
    queryset = FunerariaStatus.objects.all()
    serializer_class = FunerariaStatusSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['status', 'descricao']
    ordering = ['status']


class DependenteStatusViewSet(viewsets.ModelViewSet):
    queryset = DependenteStatus.objects.all()
    serializer_class = DependenteStatusSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['status', 'descricao']
    ordering = ['status']


class FunerariaTiposViewSet(viewsets.ModelViewSet):
    queryset = FunerariaTipos.objects.all()
    serializer_class = FunerariaTiposSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['descricao']
    ordering = ['descricao']


class PlanoFunerariaViewSet(viewsets.ModelViewSet):
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
        plano = self.get_object()
        plano_data = PlanoDetalhadoSerializer(plano).data
        total = plano.pagamentos.aggregate(total=Sum('valor_pago'))['total'] or 0
        plano_data['total_arrecadado'] = total
        return Response(plano_data)
    
    @action(detail=False)
    def relatorio_financeiro(self, request):
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
        cliente = self.get_object()
        return Response(ClienteDetalhadoSerializer(cliente).data)
    
    @action(detail=False, methods=['get'])
    def buscar_cpf(self, request):
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
        cliente_id = request.query_params.get('cliente_id')
        if not cliente_id:
            return Response({'error': 'cliente_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        dependentes = self.get_queryset().filter(cliente_id=cliente_id)
        serializer = self.get_serializer(dependentes, many=True)
        return Response(serializer.data)


class PagamentoFunerariaViewSet(viewsets.ModelViewSet):
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
        plano_id = request.query_params.get('plano_id')
        if not plano_id:
            return Response({'error': 'plano_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        pagamentos = self.get_queryset().filter(plano_funeraria_id=plano_id)
        serializer = self.get_serializer(pagamentos, many=True)
        
        total_pago = pagamentos.aggregate(total=Sum('valor_pago'))['total'] or 0
        
        return Response({
            'pagamentos': serializer.data,
            'total_pago': total_pago,
            'quantidade_pagamentos': pagamentos.count()
        })
    
    @action(detail=False)
    def relatorio_periodo(self, request):
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')
        
        queryset = self.get_queryset()
        
        if data_inicio:
            queryset = queryset.filter(data_hora_pagto__gte=parse_date(data_inicio))
        if data_fim:
            queryset = queryset.filter(data_hora_pagto__lte=parse_date(data_fim))
        
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
        cliente = serializer.validated_data.get('cliente')
        
        plano = None
        if cliente:
            plano = PlanoFuneraria.objects.filter(
                cliente=cliente,
                plano_status__status='Ativo'
            ).first()
        
        servico = serializer.save(
            funcionario_criacao=self.request.user,
            funcionario_atualizacao=self.request.user,
            data_hora_servico=timezone.now(),
            plano=plano
        )
        
        tipo_servico = servico.tipo
        if tipo_servico.valor and tipo_servico.valor > 0:
            status_pendente = FunerariaStatus.objects.get(status='Pendente')
            PagamentoFuneraria.objects.create(
                valor_pago=tipo_servico.valor,
                data_hora_pagto=timezone.now(),
                forma_pagamento='PIX',
                plano_funeraria=plano,
                status_pagamento=status_pendente,
                created_at=timezone.now()
            )
    
    def perform_update(self, serializer):
        serializer.save(funcionario_atualizacao=self.request.user)
    
    @action(detail=False)
    def por_cliente(self, request):
        cliente_id = request.query_params.get('cliente_id')
        if not cliente_id:
            return Response({'error': 'cliente_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        servicos = self.get_queryset().filter(cliente_id=cliente_id)
        serializer = self.get_serializer(servicos, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def relatorio_tipos(self, request):
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')
        
        queryset = self.get_queryset()
        
        if data_inicio:
            queryset = queryset.filter(data_hora_servico__gte=parse_date(data_inicio))
        if data_fim:
            queryset = queryset.filter(data_hora_servico__lte=parse_date(data_fim))
        
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
    permission_classes = [IsAuthenticated]
    
    @action(detail=False)
    def estatisticas(self, request):
        hoje = datetime.now().date()
        inicio_mes = hoje.replace(day=1)
        
        total_clientes = ClienteFuneraria.objects.count()
        total_dependentes = DependenteFuneraria.objects.count()
        total_planos = PlanoFuneraria.objects.count()
        
        servicos_mes = ServicoPrestadoFuneraria.objects.filter(
            data_hora_servico__gte=inicio_mes
        ).count()
        
        pagamentos_mes = PagamentoFuneraria.objects.filter(
            data_hora_pagto__gte=inicio_mes
        )
        valor_arrecadado_mes = pagamentos_mes.aggregate(
            total=Sum('valor_pago')
        )['total'] or 0
        
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