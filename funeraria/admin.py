from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    FuncionarioFuneraria, ClienteFuneraria, DependenteFuneraria,
    PlanoFuneraria, PagamentoFuneraria, ServicoPrestadoFuneraria,
    FunerariaStatus, FunerariaTipos, DependenteStatus, ClientePlano,
    FormaPagamento # Adicionado FormaPagamento aqui
)


@admin.register(FuncionarioFuneraria)
class FuncionarioFunerariaAdmin(UserAdmin):
    """Admin para funcionários da funerária"""
    list_display = ('username', 'first_name', 'last_name', 'cpf', 'email', 'is_active')
    list_filter = ('is_active', 'is_staff', 'data_nascimento')
    search_fields = ('username', 'first_name', 'last_name', 'cpf', 'email')
    ordering = ('username',)

    filter_horizontal = ('groups', 'user_permissions')

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
    list_display = ('status', 'descricao', 'categoria') # Adicionado categoria para melhor visualização
    list_filter = ('categoria',) # Filtro por categoria
    search_fields = ('status', 'descricao')
    ordering = ('status',)


@admin.register(DependenteStatus)
class DependenteStatusAdmin(admin.ModelAdmin):
    list_display = ('status', 'descricao')
    search_fields = ('status',)
    ordering = ('status',)


@admin.register(FunerariaTipos)
class FunerariaTiposAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'categoria', 'valor', 'duracao_em_dias') # Adicionado duracao_em_dias
    list_filter = ('categoria',)
    search_fields = ('descricao',)
    ordering = ('descricao',)
    
    fieldsets = (
        (None, {
            'fields': ('descricao', 'categoria', 'valor', 'duracao_em_dias') # Adicionado duracao_em_dias aqui
        }),
    )

@admin.register(PlanoFuneraria)
class PlanoFunerariaAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_plano', 'valor_mensal', 'data_fim', 'plano_status', 'created_at') # 'tipo_renovacao' é opcional
    list_filter = ('tipo_plano', 'plano_status', 'created_at') # Filtro por tipo_plano
    search_fields = ('cobertura', 'tipo_plano__descricao') # Adicionado busca por descrição do tipo de plano
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    autocomplete_fields = ('tipo_plano', 'plano_status', 'funcionario_criacao', 'funcionario_atualizacao', 'tipo_renovacao') # Adicionado tipo_renovacao

    fieldsets = (
        ('Informações do Plano', {
            'fields': ('valor_mensal', 'tipo_renovacao', 'cobertura', 'data_fim', 'tipo_plano', 'plano_status')
        }),
        ('Controle', {
            'fields': ('funcionario_criacao', 'funcionario_atualizacao', 'created_at', 'updated_at')
        }),
    )

class ClientePlanoInline(admin.TabularInline):
    model = ClientePlano
    extra = 1
    autocomplete_fields = ['plano']
    fields = ['plano', 'data_inicio', 'data_fim', 'ativo'] # Adicionado data_fim para gerenciamento in-line

class DependenteFunerariaInline(admin.TabularInline):
    model = DependenteFuneraria
    extra = 0
    # Removido readonly_fields para permitir edição de campos como telefone, endereco
    # Se quiser que todos sejam readonly no inline, especifique-os explicitamente
    fields = ['nome', 'cpf', 'data_nascimento', 'genero', 'telefone', 'endereco', 'dependente_status']
    autocomplete_fields = ['dependente_status'] # Mantido autocomplete para status
    # Note: 'cliente', 'funcionario_criacao', 'funcionario_atualizacao' são preenchidos automaticamente pelo cliente principal ou pela criação/atualização.


@admin.register(ClienteFuneraria)
class ClienteFunerariaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'telefone', 'email', 'cliente_status', 'created_at')
    list_filter = ('cliente_status', 'data_nascimento', 'created_at')
    search_fields = ('nome', 'cpf', 'email', 'telefone')
    ordering = ('nome',)
    readonly_fields = ('created_at', 'updated_at')

    autocomplete_fields = ('cliente_status', 'funcionario_cadastro', 'funcionario_atualizacao')

    inlines = [DependenteFunerariaInline, ClientePlanoInline]

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


@admin.register(DependenteFuneraria)
class DependenteFunerariaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'cliente', 'genero', 'dependente_status', 'created_at')
    list_filter = ('genero', 'dependente_status', 'data_nascimento', 'created_at')
    search_fields = ('nome', 'cpf', 'cliente__nome')
    ordering = ('nome',)
    readonly_fields = ('created_at', 'updated_at')

    autocomplete_fields = ('cliente', 'dependente_status', 'funcionario_criacao', 'funcionario_atualizacao')

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

@admin.register(FormaPagamento)
class FormaPagamentoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'categoria')
    list_filter = ('categoria',)
    search_fields = ('descricao',)
    ordering = ('descricao',)


@admin.register(PagamentoFuneraria)
class PagamentoFunerariaAdmin(admin.ModelAdmin):
    list_display = ('id', 'valor_pago', 'data_hora_pagto', 'status_pagamento', 'plano_funeraria', 'created_at')
    list_filter = ('status_pagamento', 'data_hora_pagto')
    search_fields = ('status_pagamento__status', 'plano_funeraria__id')
    ordering = ('-data_hora_pagto',)
    readonly_fields = ('created_at',)

    autocomplete_fields = ('status_pagamento', 'plano_funeraria') # Adicionado plano_funeraria para autocomplete

    fieldsets = (
        ('Informações do Pagamento', {
            'fields': ('valor_pago', 'data_hora_pagto', 'status_pagamento')
        }),
        ('Relacionamento', {
            'fields': ('plano_funeraria',)
        }),
        ('Controle', {
            'fields': ('created_at',)
        }),
    )

@admin.register(ServicoPrestadoFuneraria)
class ServicoPrestadoFunerariaAdmin(admin.ModelAdmin):
    list_display = ('id', 'data_hora_servico', 'cliente', 'tipo', 'plano', 'created_at')
    list_filter = ('tipo', 'data_hora_servico', 'created_at')
    search_fields = ('cliente__nome', 'tipo__descricao', 'observacoes')
    ordering = ('-data_hora_servico',)
    readonly_fields = ('created_at', 'updated_at')

    autocomplete_fields = ('cliente', 'tipo', 'plano', 'funcionario_criacao', 'funcionario_atualizacao')

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