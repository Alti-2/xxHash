from conans import ConanFile, CMake, tools
import os

class xxHash(ConanFile):
    name = "xxHash"
    license = "BSD-2-Clause"
    version = "v0.6.5"
    settings = "compiler", "arch", "target"
    generators = "cmake"
    scm = {
        "type": "git",
        "url": "https://github.com/Alti-2/xxHash.git",
        "revision": "conan_cmake"
    }
    build_requires = "ninja-build/[>=1.9.0]"

    def build_requirements(self):
        if self.settings.compiler == "ses_arm":
            self.build_requires("SES-ARM/[>=4.0.0]")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        
        if self.should_configure:
            cmake.verbose = True
            cmake.definitions["CMAKE_MAKE_PROGRAM"] = os.path.join(self.deps_cpp_info["ninja-build"].rootpath, "ninja")
            cmake_defines = None

            if self.settings.target == "mcu":
                # xxHash supports "bundled mode", which does not install the final product on the host machine.
                # If we're cross compiling, we definitely do not want to install.
                cmake.definitions["XXHASH_BUNDLED_MODE"] = "ON"
                # Cross compiling to an mcu means the xxhsum project is not compatible.
                cmake_defines = dict({"BUILD_XXHSUM": False, "BUILD_SHARED_LIBS": False})
                cmake.definitions["CMAKE_C_ABI_COMPILED"] = self.settings.compiler.abi
                cmake.definitions["CMAKE_CROSS_COMPILING"] = 1
                cmake.definitions["CONAN_DISABLE_CHECK_COMPILER"] = 1
                cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = 1
            
            if str(self.settings.arch).find("arm") != -1:
                cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = "arm"
                
            cmake.configure(source_dir="cmake_unofficial", defs=cmake_defines)
        
        if self.should_build:
            cmake.build()

    def package(self):
        self.copy("*.h")
        self.copy("*.a", src=os.path.join(self.build_folder, "lib"), keep_path=False)
        self.copy("*.so", src=os.path.join(self.build_folder, "lib"), keep_path=False)
        self.copy("*.lib", src=os.path.join(self.build_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = [""]
        self.cpp_info.libs.append("libxxhash.a")
