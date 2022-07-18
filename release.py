import os
import sys
from zipfile import ZipFile, is_zipfile

NAME="hashgen"
EXT="zip"
VERSION_MAJOR=0
VERSION_MINOR=5
VERSION_BUILD=0

ALPHA=True
BETA=False

DIST_FOLDER="dist"

FILES = [
	DIST_FOLDER + "/hashgen.exe"
]


if __name__ == "__main__":
	
	name = f"{NAME}-{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}.{EXT}"
	
	with ZipFile(name,mode='w') as z:
		for f in FILES:
			print(f"Writing: {f}")
			z.write(f)
		
		
	if is_zipfile(name):
		print(f"Release {name} successfully created")
		
	
			