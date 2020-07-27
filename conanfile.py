from conans import ConanFile, CMake, tools
import os

class xxHash(ConanFile):
    name = "xxhash"
    license = "BSD-2-Clause"
    version = "v0.6.5"
    scm = {
        "type": "git",
        "url": "https://github.com/Alti-2/xxHash.git",
        "revision": "conan_cmake"
    }
    options = {"long_long_support": [True, False], "inline_all": [True, False], "shared": [True, False], 
               "bundled_mode": [True, False]}
    default_options = {"long_long_support": False, "inline_all": False, "shared": False, 
                       "bundled_mode": True}
    python_requires = "SES-ARM/[>=4]", "conan-helper/[0.0.12]",
    python_requires_extend = "conan-helper.ArchiveHelper"
    _source_list = ["xxhash.c"]
    _header_list = ["xxhash.h"]
    _compile_defines = {"XXH_BUNDLED_MODE": None}
    _vs_sln = os.path.join("visual_studio", "xxHash.sln")

    def _set_compile_defines(self):
        if self.options.inline_all == True:
            self._compile_defines["XXH_INLINE_ALL"] = 1

        if self.options.long_long_support == False:
            self._compile_defines["XXH_NO_LONG_LONG"] = 1

        self._compile_defines["XXH_BUNDLED_MODE"] = int(self.options.bundled_mode == True)
