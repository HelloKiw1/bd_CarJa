from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.conf import settings

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from veiculo.models import Compra, Locacao
from django.db.utils import ProgrammingError, OperationalError

class Login(View):

    def get(self, request):
        contexto={'mensagem': ''}
        if request.user.is_authenticated:
            return redirect("/veiculo")
        else:
            return render(request, 'autenticacao.html', contexto)   

    def post(self, request):
        
        #Obtem as crendenciais de autenticação do formulário
        usuario = request.POST.get('usuario', None)
        senha = request.POST.get('senha', None)

        #Verificar as crendencias de autenticação fornecidas
        user = authenticate(request, username=usuario, password=senha)
        if user is not None:

        #Verificar se o usuario esta ativo
            if user.is_active:
                login(request, user)
                return redirect("/veiculo")

            return render(request, 'autenticacao.html', {'mensagem': ' Usuario inatico'})
    
        return render(request, 'autenticacao.html', {'mensagem': 'Usuario ou Senha Invalidos'})

class Logout(View):
    """
    Class Based View para realizar logout de usuarios.
    """
    def get(self, request):
        logout(request)
        return redirect("/")
    
class LoginAPI(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'id': user.id,
            'nome': user.first_name,
            'email': user.email,
            'token': token.key
        })


class Register(View):

    def get(self, request):
        # se já autenticado redireciona
        if request.user.is_authenticated:
            return redirect('/veiculo')
        return render(request, 'register.html', {'mensagem': ''})

    def post(self, request):
        username = request.POST.get('usuario')
        password = request.POST.get('senha')

        if not username or not password:
            return render(request, 'register.html', {'mensagem': 'Usuário e senha são obrigatórios.'})

        # Verifica se já existe
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'mensagem': 'Nome de usuário já existe.'})

        # Cria usuário comum (is_staff/is_superuser = False)
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = False
        user.is_superuser = False
        user.save()

        # Faz login automático e redireciona para área de veiculos
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth_login(request, user)
            return redirect('/veiculo')

        return render(request, 'register.html', {'mensagem': 'Erro ao criar usuário, tente novamente.'})


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminDashboard(View):
    def get(self, request):
        # lista compras e locacoes para o admin
        try:
            compras = Compra.objects.select_related('user', 'veiculo').order_by('-created_at')[:200]
            locacoes = Locacao.objects.select_related('user', 'veiculo').order_by('-created_at')[:200]
        except (ProgrammingError, OperationalError):
            # provável que as tabelas ainda não existam (migrations não aplicadas)
            compras = []
            locacoes = []
        return render(request, 'admin_dashboard.html', {'compras': compras, 'locacoes': locacoes})