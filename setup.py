import setuptools 

with open("README.md", "r") as fh: 
	long_description = fh.read() 

requirements = ["aiohttp>=3.8.0,<3.9.0"] 
 
setuptools.setup( 
	name="light_telegram_bot", 
    version="0.0.1",
	author="Alexey Chebotarev", 
    author_email="alexey.p.chebotarev@gmail.com",
	description="Light python module for telegram bot api", 
	long_description=long_description, 
	long_description_content_type="text/markdown", 
	url="https://github.com/Chebotarev-Alexey/light_telegram_bot", 
	packages=setuptools.find_packages(), 
	install_requires=requirements, 
	classifiers=[ 
		"Programming Language :: Python :: 3.10",
		"Programming Language :: Python :: 3.9",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.6",
		"License :: OSI Approved :: MIT License", 
		"Operating System :: OS Independent", 
	], 
	# Требуемая версия Python. 
	python_requires='>=3.8', 
)