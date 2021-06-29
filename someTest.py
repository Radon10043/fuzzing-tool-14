import pycparser

if __name__ == "__main__":
    ast = pycparser.parse_file("Datagram.h",use_cpp=True,cpp_path='gcc',cpp_args=['-E', r'-Iutils/fake_libc_include'])
    ast.show()