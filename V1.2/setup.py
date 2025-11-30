from distutils.core import setup, Extension
import os

# Define the extension module
keyboard_hook_module = Extension(
    'keyboardhook',
    sources=['keyboard_hook.c'],
    libraries=['user32', 'imm32'],
    define_macros=[('WIN32', '1')]
)

setup(
    name='KeyboardHook',
    version='1.0',
    description='Windows Keyboard Hook Module',
    ext_modules=[keyboard_hook_module]
)