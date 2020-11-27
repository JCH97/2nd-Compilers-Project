class Main inherits IO {
    f(a: Int): AUTO_TYPE{
        if a<3 then a else f(a-3) fi
    };
};