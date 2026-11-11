from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Producto


class PaginasTest(TestCase):
    def test_pagina_inicial(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inicio.html')
        self.assertContains(response, 'Pastelería Dulce Hogar')

    def test_pagina_inicial_muestra_solo_productos_disponibles(self):
        Producto.objects.create(
            nombre='Torta de chocolate',
            descripcion='Torta artesanal',
            precio='15990.00',
        )
        Producto.objects.create(
            nombre='Galletas agotadas',
            descripcion='Galletas de temporada',
            precio='2500.00',
            disponible=False,
        )

        response = self.client.get('/')

        self.assertContains(response, 'Torta de chocolate')
        self.assertNotContains(response, 'Galletas agotadas')

    def test_admin_puede_agregar_producto(self):
        usuario = get_user_model().objects.create_superuser(
            username='administrador',
            email='admin@example.com',
            password='clave-de-prueba',
        )
        self.client.force_login(usuario)

        response = self.client.post(
            reverse('admin:pasteleria_producto_add'),
            {
                'nombre': 'Cheesecake',
                'descripcion': 'Cheesecake de frutilla',
                'precio': '8500.00',
                'imagen_url': '',
                'disponible': 'on',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Producto.objects.filter(nombre='Cheesecake').exists())

    @override_settings(DEBUG=False)
    def test_pagina_404_para_producto_no_disponible(self):
        response = self.client.get('/productos/no-disponible/')

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        self.assertContains(response, 'Producto no disponible', status_code=404)
