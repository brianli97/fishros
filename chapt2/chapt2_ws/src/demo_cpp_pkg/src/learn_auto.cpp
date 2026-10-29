#include <iostream>

int main() {
    auto x = 42; // x is deduced to be of type int
    auto y = 3.14; // y is deduced to be of type double
    auto z = "Hello, World!"; // z is deduced to be of type const char*

    std::cout << "x: " << x << ", y: " << y << ", z: " << z << std::endl;

    return 0;
}