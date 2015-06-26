from unittest import TestCase

from mock import Mock

from tailor.builder import *
from tailor.template import *


class CastListTests(TestCase):
    def test_read_list_convert_float_rect_bad_raises_syntaxerror(self):
        test_values = [1, 2, 'a', object()]
        with self.assertRaises(TemplateBuilder.SyntaxError):
            cast_list_float(test_values)

    def test_read_list_convert_float_good_rect_int(self):
        test_values = ['0', 0, 2, '4']
        self.assertEqual(cast_list_float(test_values), [0, 0, 2, 4])

    def test_read_list_convert_float_good_rect_float(self):
        test_values = ['0.0', 0.1, 2.5, '.4']
        self.assertEqual(cast_list_float(test_values), [0.0, 0.1, 2.5, .4])


class RootNodeTests(TestCase):
    def build_root_node(self):
        node = {
            'type': 'area',
            'name': 'root',
            'data': {
                'dpi': 72,
                'units': 'inches',
                'rect': [0, 0, 2, 6]
            },
            'children': []
        }
        return node

    def test_root_not_named_root_raises_syntaxerror(self):
        node = self.build_root_node()
        node['name'] = 'not_root'
        handler = RootNodeHandler()
        with self.assertRaises(TemplateBuilder.SyntaxError):
            handler.create_node(node)

    def test_root_missing_name_raises_syntaxerror(self):
        node = self.build_root_node()
        del node['name']
        handler = RootNodeHandler()
        with self.assertRaises(TemplateBuilder.SyntaxError):
            handler.create_node(node)

    def test_root_missing_dpi_raises_syntaxerror(self):
        node = self.build_root_node()
        del node['data']['dpi']
        handler = RootNodeHandler()
        with self.assertRaises(TemplateBuilder.SyntaxError):
            handler.create_node(node)

    def test_root_missing_units_raises_syntaxerror(self):
        node = self.build_root_node()
        del node['data']['units']
        handler = RootNodeHandler()
        with self.assertRaises(TemplateBuilder.SyntaxError):
            handler.create_node(node)


class TestRenderer(TestCase):
    def test_render(self):
        renderer = TemplateRenderer()
        builder = JSONTemplateBuilder()
        root = builder.read('../tailor/resources/templates/test_template.json')

        from PIL import Image

        im = Image.new('RGB', (1024, 1024), (128, 0, 0))
        root.push_image(im)

        im = Image.new('RGB', (1024, 1024), (0, 128, 0))
        root.push_image(im)

        im = Image.new('RGB', (1024, 1024), (0, 0, 128))
        root.push_image(im)

        im = Image.new('RGB', (1024, 1024), (255, 255, 0))
        root.push_image(im)

        renderer.render(root)


class NodeBuilderTests(TestCase):
    def build_root_node(self):
        placeholder_node = {
            'type': 'placeholder',
            'data': {},
            'children': []
        }

        area_node = {
            'type': 'area',
            'data': {
                'rect': [0, 0, 2, 6]
            },
            'children': [placeholder_node]
        }

        root = {
            'type': 'area',
            'name': 'root',
            'data': {
                'dpi': 72,
                'units': 'inches',
                'rect': [0, 0, 2, 6]
            },
            'children': [area_node]
        }
        return root

    def build_test_graph(self):
        builder = TemplateBuilder()
        root = self.build_root_node()
        return builder.build_graph(root)

    def test_missing_type_raises_syntaxerror(self):
        builder = TemplateBuilder()
        root = self.build_root_node()
        del root['type']
        with self.assertRaises(TemplateBuilder.SyntaxError):
            builder.build_node(root)

    def test_invalid_node_type_raises(self):
        # TODO: implement a testable method to check node type validity
        builder = TemplateBuilder()
        root = self.build_root_node()
        root['type'] = 'invalid_node_type_forever_and_ever_and_ever_123!@#'
        with self.assertRaises(TemplateBuilder.UnrecognizedNodeTypeError):
            builder.build_node(root)

    def test_push_image(self):
        graph = self.build_test_graph()
        image = Mock()

        self.assertEqual(graph.children[0].children[0].data, None)
        graph.push_image(image)
        self.assertEqual(graph.children[0].children[0].data, image)
