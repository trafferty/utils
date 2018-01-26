#include <string>  // string
#include <iomanip> // std::setw, put_time

#include <ctime>   // localtime
#include <chrono>  // chrono::system_clock
#include <sstream> // stringstream
#include <iostream>

// std::string getTimeStampX(int64_t offset_ms = 0)
// {
//     std::stringstream ss;

//     auto p = std::chrono::high_resolution_clock::now();
//     //auto now_c = std::chrono::high_resolution_clock::to_time_t(p);
//     auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(p.time_since_epoch());
//     ms += std::chrono::milliseconds(offset_ms);
//     auto s = std::chrono::duration_cast<std::chrono::seconds>(ms);
//     std::time_t t = s.count();
//     std::size_t fractional_seconds = ms.count() % 1000;

//     //ss << std::put_time(std::localtime(&now_c), "%c"); ///gotta wait for c++14 support in gcc for this one...sigh
//     char buf[20];
//     std::strftime(buf, sizeof(buf), "%F %T", std::localtime(&t));
//     ss << buf;
//     ss << ".";
//     ss << std::right << std::setw(3) << std::setfill('0') << fractional_seconds;
//     return ss.str();
// }

std::string getTimeStamp(int64_t offset_ms = 0)
{
    std::stringstream ss;

    auto p = std::chrono::high_resolution_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(p.time_since_epoch());
    ms += std::chrono::milliseconds(offset_ms);
    auto s = std::chrono::duration_cast<std::chrono::seconds>(ms);
    std::time_t t = s.count();
    std::size_t fractional_seconds = ms.count() % 1000;

    char buf[20];
    std::strftime(buf, sizeof(buf), "%F %T", std::localtime(&t));
    ss << buf;
    ss << ".";
    ss << std::right << std::setw(3) << std::setfill('0') << fractional_seconds;
    return ss.str();
}


int main( int argc, char *argv[] )
{
    double offset_s(1.2345);
    
    if (argc > 1)
        offset_s = std::stof(argv[1]);

    int64_t offset_ms = offset_s * 1000;

    std::string ts_1 = getTimeStamp();
    std::string ts_2 = getTimeStamp(offset_ms);

    std::cout << "ts1: " << ts_1 << std::endl;
    std::cout << "ts2: " << ts_2 << std::endl;
    std::cout << "offset_s: " << offset_s << std::endl;
    std::cout << "offset_ms: " << offset_ms << std::endl;

    return 1;
}