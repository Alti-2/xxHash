from conans import ConanFile, CMake, tools
import os

class xxHash(ConanFile):
    name = "xxhash"
    license = "BSD-2-Clause"
    version = "v0.6.5"
    settings = "compiler", "arch", "target"
    generators = "cmake"
    scm = {
        "type": "git",
        "url": "https://github.com/Alti-2/xxHash.git",
        "revision": "conan_cmake"
    }
    generators = "cmake", "compiler_args", "visual_studio"
    build_requires = "ninja/[>=1.9.0]", "cmake/[>=3.1.2]", "unity/[>=2.5.0]",
    python_requires = "SES-ARM/[>=4]", "conan-helper/[>=0.0.1]",
    python_requires_extend = "conan-helper.Importer", "conan-helper.DependencyManager", "conan-helper.ConfigurationManager", "conan-helper.ArchiveHelper"

    def build(self):
        cmake = CMake(self)
        compile_defines = {"XXH_NO_LONG_LONG": 1, }
            
        # SES doesn't play nice with CMake without major modifications.
        if self.settings.compiler == "ses_arm":
            self.python_requires["SES-ARM"].module.ses_arm.build_archive(self, "xxhash.c", compile_defines)
        # In all other cases, use CMake.
        else:
            if self.should_configure:
                cmake.verbose = True
                cmake.definitions["CMAKE_MAKE_PROGRAM"] = os.path.join(self.deps_cpp_info["ninja"].rootpath, "ninja")
                cmake_defines = None

                if self.settings.target == "mcu":
                    # xxHash supports "bundled mode", which does not install the final product on the host machine.
                    # If we're cross compiling, we definitely do not want to install.
                    cmake.definitions["XXHASH_BUNDLED_MODE"] = "ON"
                    # Cross compiling to an mcu means the xxhsum project is not compatible.
                    cmake_defines = dict({"BUILD_XXHSUM": 0, "BUILD_SHARED_LIBS": 0, "XXH_NO_LONG_LONG": 1})
                    cmake.definitions["CMAKE_C_ABI_COMPILED"] = "arm-none-eabi"
                    cmake.definitions["CMAKE_CROSS_COMPILING"] = 1
                    cmake.definitions["CONAN_DISABLE_CHECK_COMPILER"] = 1
                    
                if str(self.settings.arch).find("arm") != -1:
                    cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = "arm"
                
                cmake.configure(source_dir="cmake_unofficial", defs=cmake_defines)
        
            if self.should_build:
                cmake.build()
            if self.should_install:
                cmake.install()

    def package(self):
        self.copy("xxhash.h")
        self.copy("*.a", src="lib", keep_path=False)
        self.copy("*.so", src=os.path.join(self.build_folder, "lib"), keep_path=False)
        self.copy("*.lib", keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = [""]
        
        self.cpp_info.libdirs = [""]
        
        if self.settings.compiler != "ses_arm":
            self.cpp_info.libs = [("lib%s.a" % self.name),]
