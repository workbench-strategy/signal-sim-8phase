# Sphinx configuration for documentation
import os
import sys
sys.path.insert(0, os.path.abspath('../src'))
project = 'signal-sim-8phase'
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']
