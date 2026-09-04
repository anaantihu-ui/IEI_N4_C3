from django.shortcuts import render

# Renderizado de página de bienvenida
def bienvenida(request):
    return render(request, 'bienvenida.html')