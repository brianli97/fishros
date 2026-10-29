#include <iostream>
#include <functional>

void save_with_free_fun(const std::string &file_name)
{
    std::cout << "调用了自由函数，保存: " << file_name << std::endl;
}

class FileSave
{
    public:
        void save_with_member_fun(const std::string &file_name)
        {
            std::cout << "调用了成员函数，保存: " << file_name << std::endl;
        };
};

int main() 
{
    // 1.使用自由函数
    std::function<void(const std::string &)> func1 = save_with_free_fun;
    func1("file1.txt");

    // 2.使用成员函数
    FileSave file_save;
    std::function<void(const std::string &)> func2 = std::bind(&FileSave::save_with_member_fun, 
        &file_save, std::placeholders::_1);
    func2("file2.txt");

    // 3.使用lambda函数
    auto save_with_lambda_fun = [](const std::string &file_name) -> void {
        std::cout << "调用了lambda函数，保存: " << file_name << std::endl;
    };
    std::function<void(const std::string &)> func3 = save_with_lambda_fun;
    func3("file3.txt");

    return 0;
}