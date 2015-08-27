import unittest
import numpy as np
from pymesh.wires import WireNetwork
from pymesh.wires import Tiler
from pymesh.wires import Parameters
from WireTestCase import WireTestCase

class TilerTest(WireTestCase):
    def test_tile_with_bbox(self):
        wire_network = self.load_wires("brick5.wire");
        params = Parameters(wire_network, 0.5);
        bbox_min = np.zeros(3);
        bbox_max = np.ones(3) * 5 * 2;
        reps = np.ones(3) * 2;

        tiler = Tiler(wire_network);
        tiler.tile_with_guide_bbox(bbox_min, bbox_max, reps, params);
        tiled_wire_network = tiler.wire_network;

        self.assertEqual(8 * wire_network.num_edges,
                tiled_wire_network.num_edges);
        self.assertEqual(8 * wire_network.num_vertices - 12,
                tiled_wire_network.num_vertices);
        self.assert_array_equal(
                [bbox_min, bbox_max], tiled_wire_network.bbox);
        self.assertTrue(tiled_wire_network.has_attribute("thickness"));
        self.assertTrue(tiled_wire_network.has_attribute("vertex_offset"));
        self.assert_array_equal(
                np.ones(tiled_wire_network.num_vertices) * 0.5,
                tiled_wire_network.get_attribute("thickness").ravel());

    def test_tile_with_guide_mesh(self):
        wire_network = self.load_wires("brick5.wire");
        params = Parameters(wire_network, 0.5);

        tiler = Tiler(wire_network);

        mesh = self.load_mesh("hex_s1.msh");

        tiler = Tiler(wire_network);
        tiler.tile_with_guide_mesh(mesh, params);
        tiled_wire_network = tiler.wire_network;

        self.assertEqual(8 * wire_network.num_edges,
                tiled_wire_network.num_edges);
        self.assertEqual(8 * wire_network.num_vertices - 12,
                tiled_wire_network.num_vertices);
        self.assert_array_equal(
                mesh.bbox, tiled_wire_network.bbox);
        self.assertTrue(tiled_wire_network.has_attribute("thickness"));
        self.assertTrue(tiled_wire_network.has_attribute("vertex_offset"));
        self.assert_array_equal(
                np.ones(tiled_wire_network.num_vertices) * 0.5,
                tiled_wire_network.get_attribute("thickness").ravel());

    def test_tile_with_mixed_patterns(self):
        wire_networks = [
                self.load_wires("pattern0746.wire"),
                self.load_wires("pattern1065.wire"), ];
        params = [Parameters(wire_networks[0], 0.5),
                Parameters(wire_networks[1], 0.5)];
        map(lambda p: p.load_default_isotropic_parameters(), params);

        max_num_dofs = max(params[0].num_dofs, params[1].num_dofs);
        pattern_id = np.array([0, 1, 1, 0, 1, 0, 0, 1]);

        mesh = self.load_mesh("hex_s1.msh");
        mesh.add_attribute("pattern_id");
        mesh.set_attribute("pattern_id", pattern_id);
        for i in range(max_num_dofs):
            dof_name = "dof_{}".format(i);
            dof = np.array([params[j].dofs[i]
                if i < params[j].num_dofs else 0
                for j in pattern_id ]);

            mesh.add_attribute(dof_name);
            mesh.set_attribute(dof_name, dof);

        tiler = Tiler(wire_networks);
        tiler.tile_with_mixed_patterns(mesh);
        tiled_wire_network = tiler.wire_network;

        self.assert_array_equal(
                mesh.bbox, tiled_wire_network.bbox);
        self.assertEqual(
                (wire_networks[0].num_edges +
                    wire_networks[1].num_edges) * 4,
                tiled_wire_network.num_edges);
        self.assertEqual(
                (wire_networks[0].num_vertices +
                    wire_networks[1].num_vertices) * 4 - 4 * 4 * 3,
                tiled_wire_network.num_vertices);
