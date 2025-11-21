from django.urls import path
from veiculo.views import *
from sistema.views import AdminDashboard

urlpatterns = [
    path('', ListarVeiculos.as_view(), name='listar-veiculos'),                      # /veiculo/
    path('novo/', CriarVeiculos.as_view(), name='criar-veiculos'),
    path('deletar/<int:pk>', DeletarVeiculos.as_view(), name='deletar-veiculos'),   # /veiculo/deletar/1/
    path('exibir/', ExibirVeiculos.as_view(), name='exibir-veiculos'),      # /veiculo/exibir/1/
    path('<int:pk>/', EditarVeiculos.as_view(), name='editar-veiculos'),
    path('<int:pk>/detalhes/', DetalharVeiculo.as_view(), name='detalhar-veiculo'),
    path('<int:pk>/comprar/', ComprarVeiculo.as_view(), name='comprar-veiculo'),
    path('<int:pk>/alugar/', AlugarVeiculo.as_view(), name='alugar-veiculo'),
    path('alugar/resumo/', ResumoLocacao.as_view(), name='resumo-locacao'),
    path('dashboard/', AdminDashboard.as_view(), name='admin-dashboard'),
    path('meus/transacoes/', UserDashboard.as_view(), name='user-dashboard'),
    path('compra/deletar/<int:pk>/', UserDeleteCompra.as_view(), name='user-delete-compra'),
    path('locacao/deletar/<int:pk>/', UserDeleteLocacao.as_view(), name='user-delete-locacao'),
    path('api/', APIListarVeiculos.as_view(), name='api-listar-veiculos'),
    path('api/<int:pk>/', APIDeletarVeiculo.as_view(), name='api-deletar-veiculos'),
    path('foto/<str:arquivo>', FotoVeiculo.as_view(), name='foto-veiculo'),


]