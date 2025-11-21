from veiculo.models import Veiculo
from django.shortcuts import render
from django.urls import reverse_lazy
from veiculo.forms import FormularioVeiculo
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import ListAPIView, DestroyAPIView
from veiculo.serializers import SerializadorVeiculo
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions
from veiculo.models import Compra, Locacao
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from decimal import Decimal, InvalidOperation
import re


def parse_price_to_decimal(s):
    """Converte strings de preço (ex: 'R$ 10.000,00' ou '10000.00') para Decimal com regras seguras."""
    if s is None:
        return Decimal('0')
    s = re.sub(r"[^0-9,.-]", "", str(s))
    if not s:
        return Decimal('0')
    if "." in s and "," in s:
        # ponto como separador de milhares, vírgula decimal
        s = s.replace('.', '')
        s = s.replace(',', '.')
    else:
        if "," in s:
            s = s.replace(',', '.')
    try:
        return Decimal(s)
    except InvalidOperation:
        return Decimal('0')

class ListarVeiculos(LoginRequiredMixin, ListView):
    model = Veiculo
    context_object_name = 'veiculos'
    template_name = 'veiculo/listar.html'


class CriarVeiculos(LoginRequiredMixin, CreateView):
    
    model = Veiculo
    form_class= FormularioVeiculo
    template_name = 'veiculo/novo.html'
    success_url = reverse_lazy('listar-veiculos')


class EditarVeiculos(LoginRequiredMixin, UpdateView):

    model = Veiculo
    form_class = FormularioVeiculo
    template_name = 'veiculo/editar.html'
    success_url = reverse_lazy('listar-veiculos')

class DeletarVeiculos(LoginRequiredMixin, DeleteView):

    model = Veiculo
    template_name = 'veiculo/deletar.html'
    success_url = reverse_lazy('listar-veiculos')


class ExibirVeiculos(ListView):

    model = Veiculo
    context_object_name = 'veiculos'
    template_name = 'veiculo/exibir.html'

class FotoVeiculo(View):
    def get(self, request, arquivo):
        try:
            veiculo = Veiculo.objects.get(foto='veiculo/fotos/{}' .format(arquivo))
            return FileResponse(veiculo.foto)
        except ObjectDoesNotExist:
            raise Http404('Foto não encontrada ou acesso não autorizado!')
        except Exception as exception:
            raise exception

class DetalharVeiculo(DetailView):
    model = Veiculo
    template_name = 'veiculo/detalhes.html'


class ComprarVeiculo(DetailView):
    model = Veiculo
    template_name = 'veiculo/comprar.html'

    def post(self, request, *args, **kwargs):
        # Simples confirmação de compra — aqui você pode criar model Order/Transaction
        self.object = self.get_object()
        # calcula preço e salva a compra (usar Decimal para precisão)
        # Preferir o preço de venda (`preco`) do veículo; usar `preco_diaria` apenas como fallback
        preco_val = Decimal('0')
        # tenta obter preço de venda (campo `preco`, possivelmente string formatada)
        sale_price = parse_price_to_decimal(self.object.preco) if (hasattr(self.object, 'preco') and self.object.preco) else Decimal('0')
        if sale_price > Decimal('0'):
            preco_val = sale_price
        elif self.object.preco_diaria is not None:
            preco_val = Decimal(self.object.preco_diaria)

        # Salva compra no banco
        compra = Compra.objects.create(
            user=request.user if request.user.is_authenticated else None,
            veiculo=self.object,
            preco=preco_val
        )

        return render(request, self.template_name, {'object': self.object, 'mensagem': 'Compra confirmada. Obrigado!', 'compra': compra})


class AlugarVeiculo(DetailView):
    model = Veiculo
    template_name = 'veiculo/alugar.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        dias = int(request.POST.get('dias', 1))
        # calcula o valor unitário e total usando preco_diaria se disponível
        try:
            if self.object.preco_diaria is not None:
                preco_unitario = Decimal(self.object.preco_diaria)
            else:
                preco_unitario = parse_price_to_decimal(self.object.preco)
            total = (preco_unitario * Decimal(dias)) if preco_unitario is not None else Decimal('0')
        except Exception:
            preco_unitario = Decimal('0')
            total = Decimal('0')

        # salva os dados da locação na sessão temporariamente
        request.session['last_rental'] = {
            'usuario_id': request.user.id if request.user.is_authenticated else None,
            'usuario_nome': request.user.username if request.user.is_authenticated else 'Convidado',
            'veiculo_id': self.object.id,
            'veiculo_modelo': self.object.modelo,
            'dias': dias,
            'preco_unitario': str(preco_unitario) if preco_unitario is not None else None,
            'total': str(total),
        }

        # Salva locação no banco
        from veiculo.models import Locacao
        loc = Locacao.objects.create(
            user=request.user if request.user.is_authenticated else None,
            veiculo=self.object,
            dias=dias,
                preco_unitario=(preco_unitario if preco_unitario is not None else None),
                total=total
        )
        # Atualiza sessão com id da locacao
        request.session['last_rental']['locacao_id'] = loc.id

        # Em vez de mostrar a confirmação completa, mostramos um botão para ver o resumo
        return render(request, self.template_name, {'object': self.object, 'show_summary_button': True, 'locacao': loc})


class ResumoLocacao(View):
    def get(self, request):
        data = request.session.get('last_rental')
        if not data:
            return render(request, 'veiculo/resumo.html', {'error': 'Nenhuma locação encontrada.'})

        veiculo = None
        try:
            veiculo = Veiculo.objects.get(pk=data.get('veiculo_id'))
        except Exception:
            veiculo = None

        return render(request, 'veiculo/resumo.html', {'rental': data, 'veiculo': veiculo})

class APIListarVeiculos(ListAPIView):
    serializer_class = SerializadorVeiculo
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Veiculo.objects.all()
    
class APIDeletarVeiculo(DestroyAPIView):
    serializer_class = SerializadorVeiculo
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Veiculo.objects.all()


class UserDashboard(LoginRequiredMixin, View):
    def get(self, request):
        # lista compras e locações do usuário
        compras = Compra.objects.filter(user=request.user).select_related('veiculo').order_by('-created_at')
        locacoes = Locacao.objects.filter(user=request.user).select_related('veiculo').order_by('-created_at')
        return render(request, 'veiculo/user_dashboard.html', {'compras': compras, 'locacoes': locacoes})


class UserOwnsObjectMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        # permite apenas se o objeto pertence ao usuário
        return obj.user == self.request.user


class UserDeleteCompra(LoginRequiredMixin, UserOwnsObjectMixin, DeleteView):
    model = Compra
    template_name = 'veiculo/confirm_delete_compra.html'
    success_url = reverse_lazy('user-dashboard')

    def get_queryset(self):
        return Compra.objects.filter(user=self.request.user)


class UserDeleteLocacao(LoginRequiredMixin, UserOwnsObjectMixin, DeleteView):
    model = Locacao
    template_name = 'veiculo/confirm_delete_locacao.html'
    success_url = reverse_lazy('user-dashboard')

    def get_queryset(self):
        return Locacao.objects.filter(user=self.request.user)