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

    def requirements(self):
        self.requires("fmt/8.1.1")
        self.requires("spdlog/1.9.2")
        self.requires("gtest/1.10.0")

    def build_requirements(self):
        self.build_requires("cmake/3.21.1")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
