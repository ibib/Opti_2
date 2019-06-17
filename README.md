# Opti²

Opti² is a tool to support optical simulation in the development and optimization of optical systems. Opti² was developed for the optics simulation software [Zemax OpticStudio®]( https://www.zemax.com/products/opticstudio) version 18.4 to implement a hybrid raytracing method using [PyZDDE](https://github.com/xzos/PyZDDE). The method is based on coupling sequential and non-sequential ray tracing, which combines the respective advantages of the two ray tracing programs in one simulation environment. In addition, Rayfiles can be deposited in Opti² in the settings area, which are automatically inserted into the non-sequential model when the sequential model is converted into the non-sequential model. By executing a raytrace in the non-sequential mode, the luminous flux determined on the detector is transferred to the enclosed *.ZPL macro for the optimization of the system. This macro enables the optimization of the optical system with regard to efficiency and serves as an example. Programming and including own macros into Opti², allows user-defined optimization of optical systems.

### Prerequisites

Install the listed requirements of the requirements.txt in your Python enviroment. Tested with Anaconda and Python 3.5.
Insert the *.ZPL macro in the macro folder.

### Starting

Execute the main.py.

## Build portable

Install Pyinstaller in your enviroment and run the build.bat. When the build process is finished execute ./dist/Start.bat.
It does not work if QT ist installed over Anaconda. Instead you can use the pip source.

## Program Authors

* **J. August**
* **P.-P. Ley**

## License

This project is licensed under the GPL License - see the [LICENSE](LICENSE) file for details

## Special Acknowledgments

* This tool was developed within the framework of the "[Wege in die Forschung II]( https://www.uni-hannover.de/de/forschung/wiss-nachwuchs/postdocs/bisher-gefoerderte-projekte/wif-ii-projekte-2017/wolf/)" funding programme for young researchers at Leibniz Universität Hannover.
* [Institute of Product Development](https://www.ipeg.uni-hannover.de/institut.html?&L=1)
* [PyZDDE](https://github.com/xzos/PyZDDE)

