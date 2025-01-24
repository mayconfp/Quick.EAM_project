import os
import subprocess
import sys

from .Package import Package


class Library:
	def __init__(self):
		reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
		names_and_versions = [r.decode() for r in reqs.split()]
		self._installed_packages = []