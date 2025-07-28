# funeraria/services.py

from django.utils import timezone
from .models import ServicoPrestadoFuneraria, PagamentoFuneraria, FunerariaStatus

def criar_servico(cliente, plano, tipo_servico, funcionario, **kwargs):
    servico = ServicoPrestadoFuneraria.objects.create(
        cliente=cliente,
        plano=plano,
        tipo=tipo_servico,
        funcionario_criacao=funcionario,
        funcionario_atualizacao=funcionario,
        data_hora_servico=timezone.now(),
        **kwargs
    )
    
    if tipo_servico.valor:
        status_pendente = FunerariaStatus.objects.get(status='Pendente')
        PagamentoFuneraria.objects.create(
            valor_pago=tipo_servico.valor,
            data_hora_pagto=timezone.now(),
            forma_pagamento='PIX',
            plano_funeraria=plano,
            status_pagamento=status_pendente,
        )
    
    return servico