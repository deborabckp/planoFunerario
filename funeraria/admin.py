from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    FuncionarioFuneraria, ClienteFuneraria, DependenteFuneraria,
    PlanoFuneraria, PagamentoFuneraria, ServicoPrestadoFuneraria,
    FunerariaStatus, FunerariaTipos, DependenteStatus
)


@admin.register(FuncionarioFuneraria)
class FuncionarioFunerariaAdmin(UserAdmin):
    """Admin para funcionários da funerária"""
    list_display = ('username', 'first_name', 'last_name', 'cpf', 'email', 'is_active')
    list_filter = ('is_active', 'is_staff', 'data_nascimento')
    search_fields = ('username', 'first_name', 'last_name', 'cpf', 'email')
    ordering = ('username',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Pessoais', {
            'fields': ('cpf', 'data_nascimento', 'telefone')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Pessoais', {
            'fields': ('cpf', 'data_nascimento', 'telefone')
        }),
    )


@admin.register(FunerariaStatus)
class FunerariaStatusAdmin(admin.ModelAdmin):
    """Admin para status da funerária"""
    list_display = ('status', 'descricao')
    search_fields = ('status',)
    ordering = ('status',)


@admin.register(DependenteStatus)
class DependenteStatusAdmin(admin.ModelAdmin):
    """Admin para status de dependentes"""
    list_display = ('status', 'descricao')
    search_fields = ('status',)
    ordering = ('status',)


@admin.register(FunerariaTipos)
class FunerariaTiposAdmin(admin.ModelAdmin):
    """Admin para tipos de serviços"""
    list_display = ('descricao',)
    search_fields = ('descricao',)
    ordering = ('descricao',)


@admin.register(PlanoFuneraria)
class PlanoFunerariaAdmin(admin.ModelAdmin):
    """Admin para planos funerários"""
    list_display = ('id', 'tipo_renovacao', 'valor_mensal', 'data_fim', 'plano_status', 'created_at')
    list_filter = ('tipo_renovacao', 'plano_status', 'created_at')
    search_fields = ('cobertura',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações do Plano', {
            'fields': ('valor_mensal', 'tipo_renovacao', 'cobertura', 'data_fim', 'plano_status')
        }),
        ('Controle', {
            'fields': ('funcionario_criacao', 'funcionario_atualizacao', 'created_at', 'updated_at')
        }),
    )


@admin.register(ClienteFuneraria)
class ClienteFunerariaAdmin(admin.ModelAdmin):
    """Admin para clientes da funerária"""
    list_display = ('nome', 'cpf', 'telefone', 'email', 'cliente_status', 'created_at')
    list_filter = ('cliente_status', 'data_nascimento', 'created_at')
    search_fields = ('nome', 'cpf', 'email', 'telefone')
    ordering = ('nome',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'cpf', 'data_nascimento', 'telefone', 'email')
        }),
        ('Endereço', {
            'fields': ('endereco',)
        }),
        ('Status e Controle', {
            'fields': ('cliente_status', 'funcionario_cadastro', 'funcionario_atualizacao', 'created_at', 'updated_at')
        }),
    )


class DependenteFunerariaInline(admin.TabularInline):
    """Inline para dependentes nos clientes"""
    model = DependenteFuneraria
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


# Adicionando inline de dependentes ao admin de clientes
ClienteFunerariaAdmin.inlines = [DependenteFunerariaInline]


@admin.register(DependenteFuneraria)
class DependenteFunerariaAdmin(admin.ModelAdmin):
    """Admin para dependentes dos clientes"""
    list_display = ('nome', 'cpf', 'cliente', 'genero', 'dependente_status', 'created_at')
    list_filter = ('genero', 'dependente_status', 'data_nascimento', 'created_at')
    search_fields = ('nome', 'cpf', 'cliente__nome')
    ordering = ('nome',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'cpf', 'data_nascimento', 'genero', 'telefone')
        }),
        ('Endereço', {
            'fields': ('endereco',)
        }),
        ('Relacionamento e Status', {
            'fields': ('cliente', 'dependente_status')
        }),
        ('Controle', {
            'fields': ('funcionario_criacao', 'funcionario_atualizacao', 'created_at', 'updated_at')
        }),
    )


@admin.register(PagamentoFuneraria)
class PagamentoFunerariaAdmin(admin.ModelAdmin):
    """Admin para pagamentos dos planos"""
    list_display = ('id', 'valor_pago', 'data_hora_pagto', 'forma_pagamento', 'plano_funeraria', 'status_pagamento')
    list_filter = ('forma_pagamento', 'status_pagamento', 'data_hora_pagto', 'created_at')
    search_fields = ('plano_funeraria__id', 'valor_pago')
    ordering = ('-data_hora_pagto',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Informações do Pagamento', {
            'fields': ('valor_pago', 'data_hora_pagto', 'forma_pagamento')
        }),
        ('Relacionamento', {
            'fields': ('plano_funeraria', 'status_pagamento')
        }),
        ('Controle', {
            'fields': ('created_at',)
        }),
    )


@admin.register(ServicoPrestadoFuneraria)
class ServicoPrestadoFunerariaAdmin(admin.ModelAdmin):
    """Admin para serviços prestados"""
    list_display = ('id', 'data_hora_servico', 'cliente', 'tipo', 'plano', 'created_at')
    list_filter = ('tipo', 'data_hora_servico', 'created_at')
    search_fields = ('cliente__nome', 'tipo__descricao', 'observacoes')
    ordering = ('-data_hora_servico',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações do Serviço', {
            'fields': ('data_hora_servico', 'tipo', 'observacoes')
        }),
        ('Relacionamentos', {
            'fields': ('cliente', 'plano')
        }),
        ('Controle', {
            'fields': ('funcionario_criacao', 'funcionario_atualizacao', 'created_at', 'updated_at')
        }),
    )


# Customização do site admin
admin.site.site_header = "Sistema de Gerenciamento Funerária"
admin.site.site_title = "Funerária Admin"
admin.site.index_title = "Painel Administrativo"