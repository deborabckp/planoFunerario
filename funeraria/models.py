from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re


def validate_cpf(value):
    """Valida CPF"""
    cpf = re.sub(r'[^0-9]', '', value)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido')
    
    # Validação dos dígitos verificadores
    def calculate_digit(cpf_digits, weights):
        total = sum(int(digit) * weight for digit, weight in zip(cpf_digits, weights))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder
    
    first_digit = calculate_digit(cpf[:9], range(10, 1, -1))
    second_digit = calculate_digit(cpf[:10], range(11, 1, -1))
    
    if cpf[9] != str(first_digit) or cpf[10] != str(second_digit):
        raise ValidationError('CPF inválido')


class FuncionarioFuneraria(AbstractUser):
    first_name = models.CharField('Nome', max_length=150, blank=False, null=False)
    last_name = models.CharField('Sobrenome', max_length=150, blank=False, null=False)

    groups = models.ManyToManyField(
        Group,
        related_name='funcionarios_funeraria',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
        related_query_name='funcionario_funeraria'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='funcionarios_funeraria',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
        related_query_name='funcionario_funeraria'
    )

    cpf = models.CharField(
        max_length=14,
        unique=True,
        validators=[validate_cpf],
        verbose_name='CPF'
    )
    data_nascimento = models.DateField(verbose_name='Data de Nascimento')
    telefone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\(\d{2}\)\s\d{4,5}-\d{4}$')],
        verbose_name='Telefone'
    )

    class Meta:
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'
        db_table = 'funcionario_funeraria'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class FunerariaStatus(models.Model):
    """Status gerais do sistema"""
    status = models.CharField(max_length=50, verbose_name='Status')
    descricao = models.TextField(verbose_name='Descrição')
    
    class Meta:
        verbose_name = 'Status'
        verbose_name_plural = 'Status'
        db_table = 'funeraria_status'
    
    def __str__(self):
        return self.status

class DependenteStatus(models.Model):
    """Status específicos para dependentes"""
    status = models.CharField(max_length=50, verbose_name='Status')
    descricao = models.TextField(verbose_name='Descrição')
    
    class Meta:
        verbose_name = 'Status do Dependente'
        verbose_name_plural = 'Status dos Dependentes'
        db_table = 'dependente_status'
    
    def __str__(self):
        return self.status


class FunerariaTipos(models.Model):
    descricao = models.CharField(max_length=100, verbose_name='Descrição')
    categoria = models.CharField(
        max_length=50,
        choices=[
            ('plano', 'Plano'),
            ('servico', 'Serviço'),
            ('renovacao', 'Renovação'),
        ],
        default='plano',
        verbose_name='Categoria do Tipo'
    )
    
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,      # pode ser null caso não tenha valor (ex: 'outro')
        blank=True,
        verbose_name='Valor'
    )
    class Meta:
        verbose_name = 'Funerária Tipo'
        verbose_name_plural = 'Funerária Tipos'
        db_table = 'funeraria_tipos'
    
    def __str__(self):
        return self.descricao


class PlanoFuneraria(models.Model):
    """Planos funerários oferecidos"""

    tipo_renovacao = models.ForeignKey(
        'FunerariaTipos',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='planos_com_renovacao',
        limit_choices_to={
            'categoria': 'renovacao'
        },
        verbose_name='Tipo de Renovação'
    )

    valor_mensal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor Mensal'
    )

    cobertura = models.TextField(verbose_name='Cobertura')

    data_fim = models.DateField(verbose_name='Data de Fim')

    tipo_plano = models.ForeignKey(
        'FunerariaTipos',
        on_delete=models.PROTECT,
        verbose_name='Tipo do Plano',
        limit_choices_to={
            'categoria': 'plano'
        },
        related_name='planos_funerarios'
    )

    plano_status = models.ForeignKey(
        FunerariaStatus,
        on_delete=models.PROTECT,
        verbose_name='Status do Plano'
    )

    funcionario_criacao = models.ForeignKey(
        FuncionarioFuneraria,
        on_delete=models.PROTECT,
        related_name='planos_criados',
        verbose_name='Funcionário que Criou'
    )

    funcionario_atualizacao = models.ForeignKey(
        FuncionarioFuneraria,
        on_delete=models.PROTECT,
        related_name='planos_atualizados',
        verbose_name='Funcionário que Atualizou'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plano Funerário'
        verbose_name_plural = 'Planos Funerários'
        db_table = 'plano_funeraria'

    def __str__(self):
        return f"Plano {self.tipo_plano} - Renovação: {self.tipo_renovacao or 'N/A'} - R$ {self.valor_mensal}"


class ClienteFuneraria(models.Model):
    """Clientes da funerária"""
    nome = models.CharField(max_length=100, verbose_name='Nome')
    cpf = models.CharField(
        max_length=14,
        unique=True,
        validators=[validate_cpf],
        verbose_name='CPF'
    )
    data_nascimento = models.DateField(verbose_name='Data de Nascimento')
    telefone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\(\d{2}\)\s\d{4,5}-\d{4}$')],
        verbose_name='Telefone'
    )
    endereco = models.TextField(verbose_name='Endereço')
    email = models.EmailField(verbose_name='E-mail')
    cliente_status = models.ForeignKey(
        FunerariaStatus,
        on_delete=models.PROTECT,
        verbose_name='Status do Cliente'
    )
    funcionario_cadastro = models.ForeignKey(
        FuncionarioFuneraria,
        on_delete=models.PROTECT,
        related_name='clientes_cadastrados',
        verbose_name='Funcionário que Cadastrou'
    )
    funcionario_atualizacao = models.ForeignKey(
        FuncionarioFuneraria,
        on_delete=models.PROTECT,
        related_name='clientes_atualizados',
        verbose_name='Funcionário que Atualizou'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        db_table = 'cliente_funeraria'
    
    def __str__(self):
        return f"{self.nome} - {self.cpf}"


class DependenteFuneraria(models.Model):
    """Dependentes dos clientes"""
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    
    nome = models.CharField(max_length=100, verbose_name='Nome')
    cpf = models.CharField(
        max_length=14,
        unique=True,
        validators=[validate_cpf],
        verbose_name='CPF'
    )
    data_nascimento = models.DateField(verbose_name='Data de Nascimento')
    genero = models.CharField(
        max_length=1,
        choices=GENERO_CHOICES,
        verbose_name='Gênero'
    )
    telefone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\(\d{2}\)\s\d{4,5}-\d{4}$')],
        verbose_name='Telefone',
        blank=True
    )
    endereco = models.TextField(verbose_name='Endereço')
    cliente = models.ForeignKey(
        ClienteFuneraria,
        on_delete=models.CASCADE,
        related_name='dependentes',
        verbose_name='Cliente'
    )
    dependente_status = models.ForeignKey(
        FunerariaStatus,
        on_delete=models.PROTECT,
        verbose_name='Status do Dependente'
    )
    funcionario_criacao = models.ForeignKey(
        FuncionarioFuneraria,
        on_delete=models.PROTECT,
        related_name='dependentes_criados',
        verbose_name='Funcionário que Criou'
    )
    funcionario_atualizacao = models.ForeignKey(
        FuncionarioFuneraria,
        on_delete=models.PROTECT,
        related_name='dependentes_atualizados',
        verbose_name='Funcionário que Atualizou'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dependente'
        verbose_name_plural = 'Dependentes'
        db_table = 'dependente_funeraria'
    
    def __str__(self):
        return f"{self.nome} - Dependente de {self.cliente.nome}"


class PagamentoFuneraria(models.Model):
    """Pagamentos dos planos funerários"""
    FORMA_PAGAMENTO_CHOICES = [
        ('DINHEIRO', 'Dinheiro'),
        ('CARTAO_CREDITO', 'Cartão de Crédito'),
        ('CARTAO_DEBITO', 'Cartão de Débito'),
        ('TRANSFERENCIA', 'Transferência Bancária'),
        ('PIX', 'PIX'),
        ('BOLETO', 'Boleto Bancário'),
    ]
    
    valor_pago = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor Pago'
    )
    data_hora_pagto = models.DateTimeField(verbose_name='Data/Hora do Pagamento')
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        verbose_name='Forma de Pagamento'
    )
    plano_funeraria = models.ForeignKey(
        PlanoFuneraria,
        on_delete=models.PROTECT,
        related_name='pagamentos',
        verbose_name='Plano Funerário'
    )
    status_pagamento = models.ForeignKey(
        FunerariaStatus,
        on_delete=models.PROTECT,
        verbose_name='Status do Pagamento'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        db_table = 'pagamento_funeraria'
        ordering = ['-data_hora_pagto']
    
    def __str__(self):
        return f"Pagamento R$ {self.valor_pago} - {self.data_hora_pagto.strftime('%d/%m/%Y')}"


class ServicoPrestadoFuneraria(models.Model):
    """Serviços prestados pela funerária"""
    data_hora_servico = models.DateTimeField(verbose_name='Data/Hora do Serviço')
    cliente = models.ForeignKey(
        ClienteFuneraria,
        on_delete=models.PROTECT,
        related_name='servicos',
        verbose_name='Cliente'
    )
    plano = models.ForeignKey(
        PlanoFuneraria,
        on_delete=models.PROTECT,
        related_name='servicos',
        verbose_name='Plano'
    )
    tipo = models.ForeignKey(
        FunerariaTipos,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Serviço',
        limit_choices_to={
            'categoria': 'servico',
            'descricao__icontains': 'serviço'  # inclui tipo que contenha "serviço" (case insensitive)
        }
    )
    funcionario_criacao = models.ForeignKey(
        FuncionarioFuneraria,
        on_delete=models.PROTECT,
        related_name='servicos_criados',
        verbose_name='Funcionário que Criou'
    )
    funcionario_atualizacao = models.ForeignKey(
        FuncionarioFuneraria,
        on_delete=models.PROTECT,
        related_name='servicos_atualizados',
        verbose_name='Funcionário que Atualizou'
    )
    observacoes = models.TextField(verbose_name='Observações', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Serviço Prestado'
        verbose_name_plural = 'Serviços Prestados'
        db_table = 'servico_prestado_funeraria'
        ordering = ['-data_hora_servico']
    
    def __str__(self):
        return f"{self.tipo.descricao} - {self.cliente.nome} - {self.data_hora_servico.strftime('%d/%m/%Y')}"
    
class ClientePlano(models.Model):
    cliente = models.ForeignKey(
        ClienteFuneraria,
        on_delete=models.CASCADE,
        related_name='cliente_planos',
        verbose_name='Cliente'
    )
    plano = models.ForeignKey(
        PlanoFuneraria,
        on_delete=models.PROTECT,
        related_name='cliente_planos',
        verbose_name='Plano Funerário'
    )
    data_inicio = models.DateField(verbose_name='Data de Início')
    data_fim = models.DateField(null=True, blank=True, verbose_name='Data de Fim')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    funcionario_cadastro = models.ForeignKey(
        FuncionarioFuneraria,
        on_delete=models.PROTECT,
        related_name='cliente_planos_cadastrados',
        verbose_name='Funcionário que Cadastrou',
        blank=True,
        null=True,
    )
    funcionario_atualizacao = models.ForeignKey(
        FuncionarioFuneraria,
        on_delete=models.PROTECT,
        related_name='cliente_planos_atualizados',
        verbose_name='Funcionário que Atualizou',
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cliente Plano'
        verbose_name_plural = 'Clientes Planos'
        db_table = 'cliente_plano'
        ordering = ['-data_inicio']
        unique_together = [('cliente', 'plano', 'data_inicio')]

    def __str__(self):
        return f"{self.cliente.nome} - {str(self.plano)} ({'Ativo' if self.ativo else 'Inativo'})"