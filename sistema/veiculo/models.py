from django.db import models
from datetime import datetime
from veiculo.consts import *
from django.contrib.auth.models import User
from django.utils import timezone

class Veiculo(models.Model):
    marca = models.SmallIntegerField(choices=OPCOES_MARCAS)
    combustivel = models.SmallIntegerField(choices=OPCOES_COMBUSTIVEL)
    cor = models.SmallIntegerField(choices=OPCOES_CORES)

    modelo = models.CharField(max_length=100)
    ano = models. IntegerField()

    preco = models.CharField(max_length=100, null=True)
    preco_diaria = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    foto = models.ImageField(blank=True, null=True, upload_to='veiculo/fotos')


    @property
    def veiculo_novo(self):
        return self.ano == datetime.now().year

    def anos_de_uso(self):
        return datetime.now().year - self.ano
    

class Compra(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='compras')
    veiculo = models.ForeignKey('Veiculo', on_delete=models.SET_NULL, null=True, related_name='compras')
    preco = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Compra #{self.id} - {self.veiculo.modelo if self.veiculo else "-"} by {self.user.username if self.user else "-"}'


class Locacao(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='locacoes')
    veiculo = models.ForeignKey('Veiculo', on_delete=models.SET_NULL, null=True, related_name='locacoes')
    dias = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Locacao #{self.id} - {self.veiculo.modelo if self.veiculo else "-"} ({self.dias} dias)'
    
    