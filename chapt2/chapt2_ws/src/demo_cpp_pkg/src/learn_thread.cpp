#include <iostream>
#include <thread>
#include <chrono>
#include <functional>
#include <cpp-httplib/httplib.h>

class Download
{
    public:
        void download(const std::string &host, const std::string &path, 
            const std::function<void(const std::string &, const std::string &)> &callback)
        {
            std::cout << "线程ID：" << std::this_thread::get_id() << std::endl;
            httplib::Client cli(host.c_str());
            auto res = cli.Get(path.c_str());
            if (res && res->status == 200)
            {
                callback(path, res->body);
            }
            else
            {
                std::cout << "下载失败，状态码：" << (res ? res->status : 0) << std::endl;
            }
        }

        void start_download(const std::string &host, const std::string &path, 
            const std::function<void(const std::string &, const std::string &)> &callback)
        {
            auto download_fun = std::bind(&Download::download, this, std::placeholders::_1, 
                std::placeholders::_2, std::placeholders::_3);
            std::thread download_thread(download_fun, host, path, callback);
            download_thread.detach(); // 分离线程，允许后台运行
        }
};

int main()
{
    Download download;
    auto download_finish_callback = [](const std::string &path, const std::string &result) -> void 
    {
        std::cout << "下载完成，路径：" << path << "，内容长度：" << result.length() << 
        "字， 内容为：" << result.substr(0, 16) << std::endl;
    };

    download.start_download("http://localhost:8000", "/novel1.txt", download_finish_callback);
    download.start_download("http://localhost:8000", "/novel2.txt", download_finish_callback);
    download.start_download("http://localhost:8000", "/novel3.txt", download_finish_callback);
    std::this_thread::sleep_for(std::chrono::seconds(10)); // 等待下载完成

    return 0;
}