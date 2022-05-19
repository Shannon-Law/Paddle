# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import paddle
from paddle.fluid.layer_helper import LayerHelper
from paddle.fluid.layers.utils import flatten
from paddle.incubate.autograd.primrules import _orig2prim, _prim2orig, _jvp, _transpose

paddle.enable_static()


############################ Test prim2orig rules ############################
class TestAddPPrim2Orig(unittest.TestCase):
    def setUp(self):
        self.main_program = paddle.static.Program()
        self.startup_program = paddle.static.Program()
        self.layer_help = LayerHelper('TestPrim2Orig')

        with paddle.static.program_guard(self.main_program,
                                         self.startup_program):
            self.init_data()

    def init_data(self):
        self.op_type = 'add_p'
        X = paddle.static.data(name='X', shape=[2, 2], dtype='float')
        Y = paddle.static.data(name='Y', shape=[2, 2], dtype='float')

        self.input = {'X': X, 'Y': Y}
        self.output = {
            'Z':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {}

        self.prim2orig_args = (X, Y)
        self.all_ops = ['add_p', 'elementwise_add']
        # { prim_op_output_var: orign_op_out_index }
        self.out_map = {self.output['Z']: 0}

    def test_op(self):
        with paddle.static.program_guard(self.main_program,
                                         self.startup_program):
            op = self.layer_help.append_op(
                type=self.op_type,
                inputs=self.input,
                outputs=self.output,
                attrs=self.attrs)

            orig_out = _prim2orig(op, *self.prim2orig_args)
            all_ops = [op.type for op in self.main_program.block(0).ops]
            self.assertEqual(sorted(all_ops), sorted(self.all_ops))
            orig_out = flatten(orig_out)
            for k, v in self.out_map.items():
                self.assertEqual(k.shape, orig_out[v].shape)


class TestSubPPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'sub_p'
        X = paddle.static.data(name='X', shape=[7, 8], dtype='float64')
        Y = paddle.static.data(name='Y', shape=[7, 8], dtype='float64')

        self.input = {'X': X, 'Y': Y}
        self.output = {
            'Z':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {}

        self.prim2orig_args = (X, Y)
        self.all_ops = ['sub_p', 'elementwise_sub']
        self.out_map = {self.output['Z']: 0}


class TestMulPPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'mul_p'
        X = paddle.static.data(name='X', shape=[7, 8], dtype='float64')
        Y = paddle.static.data(name='Y', shape=[7, 8], dtype='float64')

        self.input = {'X': X, 'Y': Y}
        self.output = {
            'Z':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {}

        self.prim2orig_args = (X, Y)
        self.all_ops = ['mul_p', 'elementwise_mul']
        self.out_map = {self.output['Z']: 0}


class TestDivPPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'div_p'
        X = paddle.static.data(name='X', shape=[7, 8], dtype='float64')
        Y = paddle.static.data(name='Y', shape=[7, 8], dtype='float64')

        self.input = {'X': X, 'Y': Y}
        self.output = {
            'Z':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {}

        self.prim2orig_args = (X, Y)
        self.all_ops = ['div_p', 'elementwise_div']
        self.out_map = {self.output['Z']: 0}


class TestSqrtPPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'sqrt_p'
        X = paddle.static.data(name='X', shape=[7, 8], dtype='float64')

        self.input = {'X': X, }
        self.output = {
            'Y':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {}

        self.prim2orig_args = (X, )
        self.all_ops = ['sqrt_p', 'sqrt']
        self.out_map = {self.output['Y']: 0}


class TestTanhPPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'tanh_p'
        X = paddle.static.data(name='X', shape=[7, 8], dtype='float64')

        self.input = {'X': X, }
        self.output = {
            'Y':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {}

        self.prim2orig_args = (X, )
        self.all_ops = ['tanh_p', 'tanh']
        self.out_map = {self.output['Y']: 0}


class TestReshapePPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'reshape_p'
        X = paddle.static.data(name='X', shape=[2, 8], dtype='float64')

        self.input = {'X': X, }
        self.output = {
            'Y':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {'shape': [4, 4]}

        self.prim2orig_args = (X, )
        self.all_ops = ['reshape_p', 'reshape2']
        self.out_map = {self.output['Y']: 0}


class TestBroadcastPPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'broadcast_p'
        X = paddle.static.data(name='X', shape=[2, 8], dtype='float64')

        self.input = {'X': X, }
        self.output = {
            'Y':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {'shape': [10, 2, 8]}

        self.prim2orig_args = (X, )
        self.all_ops = ['broadcast_p', 'expand_v2']
        self.out_map = {self.output['Y']: 0}


class TestTransposePPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'transpose_p'
        X = paddle.static.data(name='X', shape=[7, 8, 9, 10], dtype='float64')

        self.input = {'X': X, }
        self.output = {
            'Y':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {'axis': [1, 2, 0, 3]}

        self.prim2orig_args = (X, )
        self.all_ops = ['transpose_p', 'transpose2']
        self.out_map = {self.output['Y']: 0}


class TestSplitPPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'split_p'
        X = paddle.static.data(name='X', shape=[3, 9, 5], dtype='float64')

        self.input = {'X': X, }
        self.output = {
            'YS': [
                self.layer_help.create_variable_for_type_inference(
                    dtype=X.dtype) for i in range(3)
            ]
        }
        self.attrs = {'num_or_sections': [2, 3, 4], 'axis': 1}

        self.prim2orig_args = (X, )
        self.all_ops = ['split_p', 'split']
        self.out_map = {
            self.output['YS'][0]: 0,
            self.output['YS'][1]: 1,
            self.output['YS'][2]: 2,
        }


class TestConcatPPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'concat_p'
        X = paddle.static.data(name='X', shape=[3, 9, 5], dtype='float64')
        Y = paddle.static.data(name='Y', shape=[2, 9, 5], dtype='float64')
        Z = paddle.static.data(name='Z', shape=[1, 9, 5], dtype='float64')

        self.input = {'XS': [X, Y, Z], }
        self.output = {
            'Y':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {'axis': 0}

        self.prim2orig_args = ((X, Y, Z), )
        self.all_ops = ['concat_p', 'concat']
        self.out_map = {self.output['Y']: 0}


class TestReducePPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'reduce_p'
        X = paddle.static.data(name='X', shape=[3, 9, 5], dtype='float64')

        self.input = {'X': X}
        self.output = {
            'Y':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {'axis': [1], 'keepdim': True}

        self.prim2orig_args = (X, )
        self.all_ops = ['reduce_p', 'reduce_sum']
        self.out_map = {self.output['Y']: 0}


class TestMatmulPPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'matmul_p'
        X = paddle.static.data(name='X', shape=[9, 5], dtype='float64')
        Y = paddle.static.data(name='Y', shape=[5, 9], dtype='float64')

        self.input = {'X': X, 'Y': Y}
        self.output = {
            'Z':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {}

        self.prim2orig_args = (X, Y)
        self.all_ops = ['matmul_p', 'matmul_v2']
        self.out_map = {self.output['Z']: 0}


class TestSliceSelectPPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'slice_select_p'
        X = paddle.static.data(name='X', shape=[9, 5], dtype='float64')

        self.input = {'X': X, }
        self.output = {
            'Y':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {'axis': [0], 'starts': [1], 'ends': [8], 'strides': [2]}

        self.prim2orig_args = (X, )
        self.all_ops = ['slice_select_p', 'strided_slice']
        self.out_map = {self.output['Y']: 0}


class TestSliceAssignPPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'slice_assign_p'
        X = paddle.static.data(name='X', shape=[9, 5], dtype='float64')
        Y = paddle.static.data(name='Y', shape=[9, 3], dtype='float64')

        self.input = {'X': X, 'Y': Y}
        self.output = {
            'Z':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {'axis': [1], 'starts': [0], 'ends': [3], 'strides': [1]}

        self.prim2orig_args = (X, Y)
        self.all_ops = ['slice_assign_p', 'assign', 'set_value']
        self.out_map = {self.output['Z']: 0}


class TestGatherPPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'gather_p'
        X = paddle.static.data(name='X', shape=[9, 5], dtype='float64')
        IndexTensor = paddle.static.data(
            name='IndexTensor', shape=[3], dtype='int32')

        self.input = {'X': X, 'IndexTensor': IndexTensor}
        self.output = {
            'Y':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {'axis': 0, }

        self.prim2orig_args = (
            IndexTensor,
            X, )
        self.all_ops = ['gather_p', 'gather']
        self.out_map = {self.output['Y']: 0}


class TestScatterAddPPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'scatter_add_p'
        X = paddle.static.data(name='X', shape=[9, 5], dtype='float64')
        Y = paddle.static.data(name='Y', shape=[3, 5], dtype='float64')
        IndexTensor = paddle.static.data(
            name='IndexTensor', shape=[3], dtype='int32')

        self.input = {'X': X, 'Y': Y, 'IndexTensor': IndexTensor}
        self.output = {
            'Z':
            self.layer_help.create_variable_for_type_inference(dtype=X.dtype)
        }
        self.attrs = {'axis': 0, }

        self.prim2orig_args = (IndexTensor, X, Y)
        self.all_ops = [
            'scatter_add_p', 'fill_any_like', 'scatter', 'elementwise_add'
        ]
        self.out_map = {self.output['Z']: 0}


class TestFillConstantPPrim2Orig(TestAddPPrim2Orig):
    def init_data(self):
        self.op_type = 'fill_constant_p'

        self.input = {}
        self.output = {
            'Y':
            self.layer_help.create_variable_for_type_inference(paddle.int32)
        }
        self.attrs = {'value': 10, 'shape': [5, 5], 'dtype': paddle.int32}

        self.prim2orig_args = ()
        self.all_ops = ['fill_constant_p', 'fill_constant']
        self.out_map = {self.output['Y']: 0}


if __name__ == '__main__':
    unittest.main()