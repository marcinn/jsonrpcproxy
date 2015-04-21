from setuptools import setup, find_packages

setup(name='jsonrpcproxy',
      version='0.2',
      description='Damn simple JSON-RPC client',
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      author='Marcin Nowak',
      author_email='marcin.j.nowak@gmail.com',
      url='',
      keywords='web json rpc python',
      install_requires=['requests>=1.2.3, <3.0'],
      py_modules=['jsonrpcproxy'],
      include_package_data=True,
      zip_safe=False,
      )
