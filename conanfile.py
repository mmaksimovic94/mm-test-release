from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps

class HelloWorldConan(ConanFile):
    name = "hello_world"
    version = "1.0"
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"
    exports_sources = "CMakeLists.txt", "src/*"

    def layout(self):
        self.folders.source = "."
        self.folders.build = "build"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
