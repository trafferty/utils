#include <iostream>
#include <memory>
#include <functional>

class Base {
  public:
    virtual ~Base()
    {
        std::cout << "~Base()\n";
    }
};

class Derived : public Base {
  public:
    virtual ~Derived()
    {
        std::cout << "~Derived()\n";
    }
};

void free_func_deleter(Base* obj)
{
    std::cout << "Using custom deleter as a free function that doesn't need access to Manager internals\n";
    delete obj;
}

class Callable_deleter {
public:
    void operator()(Base* obj) const    {
        std::cout << "Using callable object as custom deleter\n";
        delete obj;
    };
};

class Manager {
public:
    Manager() :
        _handler_default{nullptr},
        _handler_mgr_deleter{nullptr, [&](Base* b){Mgr_custom_deleter(b);}},
        _handler_free_func_deleter{nullptr, free_func_deleter},
        _handler_callable_deleter{nullptr, Callable_deleter{}}
    { }
    virtual ~Manager()
    {
        std::cout << "~Manager()\n";
    }
    bool init_default(Base* obj)
    {
        _handler_default.reset(obj);
        return static_cast<bool>(_handler_default);
    }
    bool init_mgr_deleter(Base* obj)
    {
        _handler_mgr_deleter.reset(obj);
        return static_cast<bool>(_handler_mgr_deleter);
    }
    bool init_free_deleter(Base* obj)
    {
        _handler_free_func_deleter.reset(obj);
        return static_cast<bool>(_handler_free_func_deleter);
    }
    bool init_callable_deleter(Base* obj)
    {
        _handler_callable_deleter.reset(obj);
        return static_cast<bool>(_handler_callable_deleter);
    }
    // bool init_callable_friend_deleter(Base* obj)    
    // {   
    //  _handler_callable_friend_deleter.reset(obj);    
    //  return  static_cast<bool>(_handler_callable_friend_deleter);    
    // }    
    
private:
    std::unique_ptr<Base> _handler_default;
    std::unique_ptr<Base, std::function<void(Base*)>> _handler_mgr_deleter;
    std::unique_ptr<Base, void(*)(Base*)> _handler_free_func_deleter;
    std::unique_ptr<Base, Callable_deleter> _handler_callable_deleter;
    // std::unique_ptr<Base, Callable_friend_deleter> _handler_callable_friend_deleter;    
    // int _internal_access_demo{42};    
    // friend class Callable_friend_deleter;

    void Mgr_custom_deleter(Base* handled_object)
    {
        std::cout << "Using custom deleter as a member function of the manager - full access to manager internals, if needed\n";
        delete handled_object;
    }
};

/*
using the Callable_friend_deleter technique requires all of the classes to be defined in separate header/source files
this is roughly equivalent to what the compiler generates when using the lambda method:

   _handler_mgr_deleter{nullptr, [&](Base* b){Mgr_custom_deleter(b);}}
   
but this will give fine-grained control if needed.*/

/*
class Callable_friend_deleter {
    public:    
        Callable_friend_deleter(Manager& mgr) : _mgr{mgr} {}
        Callable_friend_deleter(const Callable_friend_deleter&) = default;
        Callable_friend_deleter(Callable_friend_deleter&) = default;   
        Callable_friend_deleter(Callable_friend_deleter&&) = default;    
        
        void operator()(Base* obj) const    
        {        
            std::cout << "Using callable object with full Manager access as custom deleter: " << _mgr._internal_access_demo << '\n';        
            delete obj;    
        }

    private:    
        Manager& _mgr;
};
*/
        
int main()
{
    Manager mgr;
    std::cout << "init_default: " << (mgr.init_default(new Derived) ? "worked" : "failed") << '\n';
    std::cout << "init_mgr_deleter: " << (mgr.init_mgr_deleter(new Derived) ? "worked" : "failed") << '\n';
    std::cout << "init_free_deleter: " << (mgr.init_free_deleter(new Derived) ? "worked" : "failed") << '\n';
    std::cout << "init_callable_deleter: " << (mgr.init_callable_deleter(new Derived) ? "worked" : "failed") << '\n';
    // std::cout << "init_callable_friend_deleter: " << (mgr.init_callable_friend_deleter(new Derived) ? "worked" : "failed") << '\n';    return 0;
}