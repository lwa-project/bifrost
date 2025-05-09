
# Copyright (c) 2021-2023, The Bifrost Authors. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of The Bifrost Authors nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Unit tests for the various Bifrost tutorial notebooks.
"""

import unittest
import glob
import sys
import re
import os
from tempfile import mkdtemp
from shutil import rmtree
from bifrost.libbifrost_generated import BF_CUDA_ENABLED


run_tutorial_tests = False
try:
    import jupyter_client
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor
    run_tutorial_tests = True
except ImportError:
    pass


__version__  = "0.1"
__author__   = "Jayce Dowell"


def run_notebook(notebook_path, run_path=None, kernel_name=None):
    """
    From:
        http://www.blog.pythonlibrary.org/2018/10/16/testing-jupyter-notebooks/
    """
    
    nb_name, _ = os.path.splitext(os.path.basename(notebook_path))
    dirname = os.path.dirname(notebook_path)
    
    with open(notebook_path, encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
        
    cleanup = False
    if run_path is None:
        run_path = mkdtemp(prefix='test-tutorial-', suffix='.tmp')
        cleanup = True
        
    proc = ExecutePreprocessor(timeout=600, kernel_name=kernel_name)
    proc.allow_errors = True
    
    proc.preprocess(nb, {'metadata': {'path': run_path}})
    output_path = os.path.join(run_path, '{}_all_output.ipynb'.format(nb_name))
    
    with open(output_path, mode='wt', encoding='utf-8') as f:
        nbformat.write(nb, f)
    errors = []
    for cell in nb.cells:
        if 'outputs' in cell:
            for output in cell['outputs']:
                if output.output_type == 'error':
                    errors.append(output)
                    
    if cleanup:
        try:
            rmtree(run_path)
        except OSError:
            pass
            
    return nb, errors


@unittest.skipUnless(run_tutorial_tests, "requires the 'nbformat' and 'nbconvert' modules")
class tutorial_tests(unittest.TestCase):
    """A unittest.TestCase collection of unit tests for the Bifrost tutorial notebooks."""
    
    def setUp(self):
        self.maxDiff = 8192
        
        self._kernel = jupyter_client.KernelManager()
        self._kernel.start_kernel()
        self.kernel_name = self._kernel.kernel_name
        
    def tearDown(self):
        self._kernel.shutdown_kernel()
        self.kernel_name = None


def _test_generator(notebook):
    """
    Function to build a test method for each notebook that is provided.  
    Returns a function that is suitable as a method inside a unittest.TestCase
    class
    """
    
    def test(self):
        nb, errors = run_notebook(notebook, kernel_name=self.kernel_name)
        
        message = ''
        if len(errors) > 0:
            for error in errors:
                message += '%s: %s\n' % (error['ename'], error['evalue'])
                for line in error['traceback']:
                    message += '  %s\n' % line
        self.assertEqual(errors, [], message)
        
    return test


_NOTEBOOKS = glob.glob(os.path.join(os.path.dirname(__file__), '..', 'tutorial', '*.ipynb'))
_NOTEBOOKS.sort()
for notebook in _NOTEBOOKS:
    nb_name = os.path.splitext(os.path.basename(notebook))[0]
    if nb_name in ['06_data_capture']:
        # Skip this for now
        continue
    # These notebooks require CUDA
    if (not BF_CUDA_ENABLED and nb_name in
        ['00_getting_started', '01_useful_functions',
         '02_building_complexity']):
        continue
    test = _test_generator(notebook)
    assert ' ' not in nb_name
    name = 'test_%s' % nb_name
    doc = """Execution of the '%s' notebook.""" % nb_name
    setattr(test, '__doc__', doc)
    setattr(tutorial_tests, name, test)


class tutorial_test_suite(unittest.TestSuite):
    """A unittest.TestSuite class which contains all of the Bifrost tutorial
    notebook tests."""
    
    def __init__(self):
        unittest.TestSuite.__init__(self)
        
        loader = unittest.TestLoader()
        self.addTests(loader.loadTestsFromTestCase(tutorial_tests))


if __name__ == '__main__':
    unittest.main()
    
