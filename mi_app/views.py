from django.shortcuts import render

def bienvenida(request):
    return render(request, 'bienvenida.html')

def mi_error_404(request, exception):
    return render(request, '404.html', status=404)