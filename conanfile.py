import os
import glob
from conans import ConanFile, CMake, tools


class GlfwConan(ConanFile):
    name = "glfw"
    version = "3.4"
    description = "The GLFW library - Builds on Windows, Linux and Macos/OSX"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, "fPIC": True}
    license = "Zlib"
    url = "https://github.com/bincrafters/conan-glfw"
    homepage = "https://github.com/glfw/glfw"
    topics = ("conan", "gflw", "opengl", "vulcan", "opengl-es")
    exports = "LICENSE"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def requirements(self):
        if self.settings.os == 'Linux':
            self.requires("libx11/1.6.8@bincrafters/stable")
            self.requires("libxrandr/1.5.2@bincrafters/stable")
            self.requires("libxinerama/1.1.4@bincrafters/stable")
            self.requires("libxcursor/1.2.0@bincrafters/stable")
            self.requires("libxi/1.7.10@bincrafters/stable")
            # self.requires("opengl/virtual@bincrafters/stable")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        # https://github.com/glfw/glfw/tree/e0c77f71f90e3bb8495c5c88fb0fb054d71cf7fc
        snapshot_version= 'e0c77f71f90e3bb8495c5c88fb0fb054d71cf7fc'
        sha256 = "c1750ee907113c823d6e768b3e509c87de59bb69de42d4b6104e8ac329669b4c"
        tools.get("{}/archive/{}.zip".format(self.homepage, snapshot_version))
        extracted_folder = self.name + '-' + snapshot_version
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["GLFW_BUILD_EXAMPLES"] = False
        cmake.definitions["GLFW_BUILD_TESTS"] = False
        cmake.definitions["GLFW_BUILD_DOCS"] = False
        cmake.configure(build_dir=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

        if self.settings.os == "Macos" and self.options.shared:
            with tools.chdir(os.path.join(self._source_subfolder, 'src')):
                for filename in glob.glob('*.dylib'):
                    self.run('install_name_tool -id {filename} {filename}'.format(filename=filename))

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.pdb", dst="bin", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(['m', 'dl', 'pthread'])
            if self.options.shared:
                self.cpp_info.exelinkflags.append("-lrt -lm -ldl")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["Cocoa", "IOKit", "CoreVideo"])