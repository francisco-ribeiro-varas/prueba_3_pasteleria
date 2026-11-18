from io import BytesIO
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Pedido, Producto


class PaginasTest(TestCase):
    def test_pagina_inicial(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inicio.html')
        self.assertContains(response, 'Pastelería Dulce Hogar')

    def test_pagina_inicial_muestra_productos_disponibles_y_agotados(self):
        Producto.objects.create(
            nombre='Torta de chocolate',
            descripcion='Torta artesanal',
            precio='15990.00',
            stock=5,
        )
        Producto.objects.create(
            nombre='Galletas agotadas',
            descripcion='Galletas de temporada',
            precio='2500.00',
            disponible=False,
            stock=5,
        )

        response = self.client.get('/')

        self.assertContains(response, 'Torta de chocolate')
        self.assertContains(response, 'Galletas agotadas')
        self.assertContains(response, 'No disponible')

    def test_pagina_inicial_no_muestra_productos_eliminados(self):
        producto = Producto.objects.create(
            nombre='Torta eliminada',
            descripcion='Ya no existe',
            precio='1000.00',
        )
        producto.delete()

        response = self.client.get('/')

        self.assertNotContains(response, 'Torta eliminada')

    def test_producto_disponible_muestra_formulario_de_compra(self):
        producto = Producto.objects.create(
            nombre='Torta de chocolate',
            descripcion='Torta artesanal',
            precio='15990.00',
            stock=3,
        )

        response = self.client.get(reverse('detalle_producto', args=[producto.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Confirmar pedido')
        self.assertContains(response, 'name="nombre_cliente"')
        self.assertContains(response, 'name="correo"')
        self.assertContains(response, 'name="telefono"')
        self.assertContains(response, 'name="cantidad"')

    def test_precio_se_muestra_formateado_a_pesos_chilenos(self):
        Producto.objects.create(
            nombre='Torta de chocolate',
            descripcion='Torta artesanal',
            precio='15990.00',
            stock=3,
        )

        response = self.client.get('/')

        self.assertContains(response, '$ 15.990')

    def test_admin_muestra_precio_formateado_a_pesos_chilenos(self):
        Producto.objects.create(
            nombre='Torta de chocolate',
            descripcion='Torta artesanal',
            precio='15990.00',
            stock=3,
        )

        usuario = get_user_model().objects.create_superuser(
            username='administrador',
            email='admin@example.com',
            password='clave-de-prueba',
        )
        self.client.force_login(usuario)

        response = self.client.get('/admin/pasteleria/producto/')

        self.assertContains(response, '$ 15.990')

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
                'stock': '5',
                'disponible': 'on',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Producto.objects.filter(nombre='Cheesecake').exists())

    def test_imagen_cargada_en_admin_aparece_en_sitio_y_listado_admin(self):
        usuario = get_user_model().objects.create_superuser(
            username='administrador',
            email='admin@example.com',
            password='clave-de-prueba',
        )
        self.client.force_login(usuario)
        imagen_buffer = BytesIO()
        Image.new('RGB', (1, 1), color='white').save(imagen_buffer, format='PNG')
        imagen_png = imagen_buffer.getvalue()

        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            response = self.client.post(
                reverse('admin:pasteleria_producto_add'),
                {
                    'nombre': 'Cheesecake',
                    'descripcion': 'Cheesecake de frutilla',
                    'precio': '8500.00',
                    'imagen': SimpleUploadedFile('cheesecake.png', imagen_png, content_type='image/png'),
                    'imagen_url': '',
                    'stock': '1',
                    'disponible': 'on',
                },
            )

            self.assertEqual(response.status_code, 302)

            response = self.client.get('/')
            self.assertContains(response, '/media/productos/cheesecake.png')

            response = self.client.get('/admin/pasteleria/producto/')
            self.assertContains(response, '/media/productos/cheesecake.png')

    @override_settings(DEBUG=True)
    def test_pagina_404_para_producto_no_disponible(self):
        producto = Producto.objects.create(
            nombre='Torta agotada',
            descripcion='Sin stock',
            precio='1000.00',
            disponible=False,
        )

        response = self.client.get(reverse('detalle_producto', args=[producto.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        self.assertContains(response, 'Producto no disponible', status_code=404)
        response = self.client.post(
            reverse('detalle_producto', args=[producto.pk]),
            {
                'nombre_cliente': 'Ana Pérez',
                'correo': 'ana@example.com',
                'telefono': '+56912345678',
                'cantidad': '1',
            },
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Pedido.objects.count(), 0)

    @override_settings(DEBUG=True)
    def test_pagina_404_para_producto_eliminado(self):
        producto = Producto.objects.create(
            nombre='Torta eliminada',
            descripcion='Ya no existe',
            precio='1000.00',
        )
        producto_id = producto.pk
        producto.delete()

        response = self.client.get(reverse('detalle_producto', args=[producto_id]))

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_compra_se_guarda_y_recargar_confirmacion_no_duplica_pedido(self):
        producto = Producto.objects.create(
            nombre='Torta de chocolate',
            descripcion='Torta artesanal',
            precio='15990.00',
            stock=2,
        )

        response = self.client.post(
            reverse('detalle_producto', args=[producto.pk]),
            {
                'nombre_cliente': 'Ana Pérez',
                'correo': 'ana@example.com',
                'telefono': '+56912345678',
                'cantidad': '2',
            },
        )

        pedido = Pedido.objects.get()
        self.assertRedirects(response, reverse('pedido_confirmado', args=[pedido.pk]))
        url_confirmacion = response.url
        producto.refresh_from_db()
        self.assertEqual(producto.stock, 0)
        self.assertEqual(producto.pedidos.count(), 1)

        response = self.client.get(reverse('detalle_producto', args=[producto.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

        response = self.client.get(url_confirmacion)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pedido recibido')
        self.assertEqual(producto.pedidos.count(), 1)

    def test_compra_no_permite_cantidad_cero(self):
        producto = Producto.objects.create(
            nombre='Torta de chocolate',
            descripcion='Torta artesanal',
            precio='15990.00',
            stock=5,
        )

        response = self.client.post(
            reverse('detalle_producto', args=[producto.pk]),
            {
                'nombre_cliente': 'Ana Pérez',
                'correo': 'ana@example.com',
                'telefono': '+56912345678',
                'cantidad': '0',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(producto.pedidos.count(), 0)

    @override_settings(DEBUG=True)
    def test_producto_sin_stock_no_se_puede_comprar(self):
        producto = Producto.objects.create(
            nombre='Torta agotada',
            descripcion='Sin stock',
            precio='1000.00',
            stock=0,
        )

        response = self.client.get('/')
        self.assertContains(response, 'Torta agotada')
        self.assertContains(response, 'Sin stock')

        response = self.client.get(reverse('detalle_producto', args=[producto.pk]))

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

        response = self.client.post(
            reverse('detalle_producto', args=[producto.pk]),
            {
                'nombre_cliente': 'Ana Pérez',
                'correo': 'ana@example.com',
                'telefono': '+56912345678',
                'cantidad': '1',
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Pedido.objects.count(), 0)

    def test_compra_de_cantidad_superior_al_stock_no_crea_pedido_ni_descuenta(self):
        producto = Producto.objects.create(
            nombre='Torta de chocolate',
            descripcion='Torta artesanal',
            precio='15990.00',
            stock=2,
        )

        response = self.client.post(
            reverse('detalle_producto', args=[producto.pk]),
            {
                'nombre_cliente': 'Ana Pérez',
                'correo': 'ana@example.com',
                'telefono': '+56912345678',
                'cantidad': '3',
            },
        )

        producto.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Solo quedan 2 unidades disponibles')
        self.assertEqual(producto.stock, 2)
        self.assertEqual(Pedido.objects.count(), 0)
