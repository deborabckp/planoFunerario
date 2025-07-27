from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    FuncionarioFuneraria, ClienteFuneraria, DependenteFuneraria,
    PlanoFuneraria, PagamentoFuneraria, ServicoPrestadoFuneraria,
    FunerariaStatus, FunerariaTipos, DependenteStatus
)


class LoginSerializer(serializers.Serializer):
    """Serializer para login de funcionários"""
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Credenciais inválidas')
            if not user.is_active:
                raise serializers.ValidationError('Conta desativada')
            data['user'] = user
        else:
            raise serializers.ValidationError('Username e password são obrigatórios')
        
        return data


class FuncionarioFunerariaSerializer(serializers.ModelSerializer):
    """Serializer para funcionários da funerária"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = FuncionarioFuneraria
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'cpf', 'data_nascimento', 'telefone', 'password',
            'is_active', 'date_joined'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = FuncionarioFuneraria.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class FunerariaStatusSerializer(serializers.ModelSerializer):
    """Serializer para status da funerária"""
    
    class Meta:
        model = FunerariaStatus
        fields = ['id', 'status', 'descricao']


class DependenteStatusSerializer(serializers.ModelSerializer):
    """Serializer para status de dependentes"""
    
    class Meta:
        model = DependenteStatus
        fields = ['id', 'status', 'descricao']


class FunerariaTiposSerializer(serializers.ModelSerializer):
    """Serializer para tipos de serviços"""
    
    class Meta:
        model = FunerariaTipos
        fields = ['id', 'descricao']


class PlanoFunerariaSerializer(serializers.ModelSerializer):
    """Serializer para planos funerários"""
    plano_status_nome = serializers.CharField(source='plano_status.status', read_only=True)
    funcionario_criacao_nome = serializers.CharField(
        source='funcionario_criacao.get_full_name', read_only=True
    )
    funcionario_atualizacao_nome = serializers.CharField(
        source='funcionario_atualizacao.get_full_name', read_only=True
    )
    
    class Meta:
        model = PlanoFuneraria
        fields = [
            'id', 'valor_mensal', 'tipo_renovacao', 'cobertura', 'data_fim',
            'plano_status', 'plano_status_nome',
            'funcionario_criacao', 'funcionario_criacao_nome',
            'funcionario_atualizacao', 'funcionario_atualizacao_nome',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ClienteFunerariaSerializer(serializers.ModelSerializer):
    """Serializer para clientes da funerária"""
    cliente_status_nome = serializers.CharField(source='cliente_status.status', read_only=True)
    funcionario_cadastro_nome = serializers.CharField(
        source='funcionario_cadastro.get_full_name', read_only=True
    )
    funcionario_atualizacao_nome = serializers.CharField(
        source='funcionario_atualizacao.get_full_name', read_only=True
    )
    total_dependentes = serializers.IntegerField(
        source='dependentes.count', read_only=True
    )
    
    class Meta:
        model = ClienteFuneraria
        fields = [
            'id', 'nome', 'cpf', 'data_nascimento', 'telefone', 'endereco', 'email',
            'cliente_status', 'cliente_status_nome',
            'funcionario_cadastro', 'funcionario_cadastro_nome',
            'funcionario_atualizacao', 'funcionario_atualizacao_nome',
            'total_dependentes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DependenteFunerariaSerializer(serializers.ModelSerializer):
    """Serializer para dependentes dos clientes"""
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    dependente_status_nome = serializers.CharField(source='dependente_status.status', read_only=True)
    funcionario_criacao_nome = serializers.CharField(
        source='funcionario_criacao.get_full_name', read_only=True
    )
    funcionario_atualizacao_nome = serializers.CharField(
        source='funcionario_atualizacao.get_full_name', read_only=True
    )
    
    class Meta:
        model = DependenteFuneraria
        fields = [
            'id', 'nome', 'cpf', 'data_nascimento', 'genero', 'telefone', 'endereco',
            'cliente', 'cliente_nome',
            'dependente_status', 'dependente_status_nome',
            'funcionario_criacao', 'funcionario_criacao_nome',
            'funcionario_atualizacao', 'funcionario_atualizacao_nome',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PagamentoFunerariaSerializer(serializers.ModelSerializer):
    """Serializer para pagamentos dos planos"""
    plano_info = serializers.CharField(source='plano_funeraria.__str__', read_only=True)
    status_pagamento_nome = serializers.CharField(source='status_pagamento.status', read_only=True)
    
    class Meta:
        model = PagamentoFuneraria
        fields = [
            'id', 'valor_pago', 'data_hora_pagto', 'forma_pagamento',
            'plano_funeraria', 'plano_info',
            'status_pagamento', 'status_pagamento_nome',
            'created_at'
        ]
        read_only_fields = ['created_at']


class ServicoPrestadoFunerariaSerializer(serializers.ModelSerializer):
    """Serializer para serviços prestados"""
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    plano_info = serializers.CharField(source='plano.__str__', read_only=True)
    tipo_descricao = serializers.CharField(source='tipo.descricao', read_only=True)
    funcionario_criacao_nome = serializers.CharField(
        source='funcionario_criacao.get_full_name', read_only=True
    )
    funcionario_atualizacao_nome = serializers.CharField(
        source='funcionario_atualizacao.get_full_name', read_only=True
    )
    
    class Meta:
        model = ServicoPrestadoFuneraria
        fields = [
            'id', 'data_hora_servico', 'observacoes',
            'cliente', 'cliente_nome',
            'plano', 'plano_info',
            'tipo', 'tipo_descricao',
            'funcionario_criacao', 'funcionario_criacao_nome',
            'funcionario_atualizacao', 'funcionario_atualizacao_nome',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# Serializers detalhados para relatórios
class ClienteDetalhadoSerializer(ClienteFunerariaSerializer):
    """Serializer detalhado para clientes com dependentes"""
    dependentes = DependenteFunerariaSerializer(many=True, read_only=True)
    servicos = ServicoPrestadoFunerariaSerializer(many=True, read_only=True)
    
    class Meta(ClienteFunerariaSerializer.Meta):
        fields = ClienteFunerariaSerializer.Meta.fields + ['dependentes', 'servicos']


class PlanoDetalhadoSerializer(PlanoFunerariaSerializer):
    """Serializer detalhado para planos com pagamentos e serviços"""
    pagamentos = PagamentoFunerariaSerializer(many=True, read_only=True)
    servicos = ServicoPrestadoFunerariaSerializer(many=True, read_only=True)
    total_arrecadado = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    
    class Meta(PlanoFunerariaSerializer.Meta):
        fields = PlanoFunerariaSerializer.Meta.fields + [
            'pagamentos', 'servicos', 'total_arrecadado'
        ]